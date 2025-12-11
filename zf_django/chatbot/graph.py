# chatbot/graph.py
"""
LangGraph 기반 주택 공고 챗봇 (V7)
- RDB 필터 + RAG 검색 통합
- 검색 히스토리 및 비교 기능
- 웹 검색 연동
"""
import json
import re
import time
from datetime import date
from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, END
from openai import OpenAI
from decouple import config

from .services import AnncAllService, DocChunkService

client = OpenAI(api_key=config('OPENAI_API_KEY'))

# Tavily (선택적)
TAVILY_API_KEY = config('TAVILY_API_KEY', default=None)
TAVILY_AVAILABLE = False
tavily_client = None

if TAVILY_API_KEY:
    try:
        from tavily import TavilyClient
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        TAVILY_AVAILABLE = True
    except ImportError:
        pass


# =============================================================================
# 설정
# =============================================================================
class ChatbotConfig:
    LLM_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"
    MAX_HISTORY_TURNS = 10
    MAX_SEARCH_HISTORY = 5
    RAG_TOP_K = 15

    _cache: Dict[str, Any] = {}
    _cache_ttl = 300

    @classmethod
    def _load_cache(cls):
        if cls._cache.get("time") and (time.time() - cls._cache["time"]) < cls._cache_ttl:
            return
        from .models import AnncAll
        active = AnncAll.objects.filter(service_status='OPEN')
        cls._cache = {
            "regions": list(active.values_list('annc_region', flat=True).distinct()),
            "statuses": list(active.values_list('annc_status', flat=True).distinct()),
            "types": list(active.values_list('annc_type', flat=True).distinct()),
            "dtl_types": list(active.values_list('annc_dtl_type', flat=True).distinct()),
            "time": time.time()
        }

    @classmethod
    def get(cls, key: str) -> list:
        cls._load_cache()
        return cls._cache.get(key, [])


# =============================================================================
# 의도 정의
# =============================================================================
class Intent:
    SEARCH = "search"      # 공고 검색 (신규/추가/복원)
    SELECT = "select"      # 목록에서 선택
    DETAIL = "detail"      # 상세 질문
    COMPARE = "compare"    # 비교
    CHAT = "chat"          # 일반 대화/웹 검색


# =============================================================================
# State 정의
# =============================================================================
class GraphState(TypedDict):
    question: str
    chat_history: List[dict]
    # 의도 관련
    intent: str
    intent_data: dict
    # 검색 관련
    search_history: List[dict]  # [{query, anncs, timestamp}]
    prev_anncs: List[dict]
    selected_annc: Optional[dict]
    selected_anncs: List[dict]  # 비교용 다중 선택
    retrieved_docs: List[dict]
    # 출력
    answer: str
    debug_info: dict


# =============================================================================
# 유틸리티
# =============================================================================
def get_embedding(text: str) -> List[float]:
    resp = client.embeddings.create(input=text, model=ChatbotConfig.EMBEDDING_MODEL)
    return resp.data[0].embedding


def call_llm(system: str, user: str, json_mode: bool = False, temp: float = 0) -> str:
    kwargs = {
        "model": ChatbotConfig.LLM_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temp
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    return client.chat.completions.create(**kwargs).choices[0].message.content


def calculate_dday(deadline: str) -> str:
    if not deadline:
        return ""
    try:
        cleaned = re.sub(r'[년월일\s]', '-', deadline).replace('.', '-').replace('--', '-').strip('-')
        m = re.search(r'(\d{2,4})-?(\d{1,2})-?(\d{1,2})', cleaned)
        if not m:
            return ""
        y, mo, d = m.groups()
        if len(y) == 2:
            y = '20' + y
        diff = (date(int(y), int(mo), int(d)) - date.today()).days
        return "마감" if diff < 0 else "D-Day" if diff == 0 else f"D-{diff}"
    except:
        return ""


def format_annc_list(anncs: List[dict], with_url: bool = True) -> str:
    if not anncs:
        return "검색된 공고가 없습니다."
    lines = []
    for i, a in enumerate(anncs, 1):
        dday = calculate_dday(a.get('annc_deadline_dt', ''))
        info = f"상태: {a.get('annc_status', '')} | 지역: {a.get('annc_region', '')}"
        if dday:
            info += f" | {dday}"
        if a.get('annc_deadline_dt'):
            info += f" | 마감: {a['annc_deadline_dt']}"
        line = f"{i}. **{a.get('annc_title', '')}**\n   - {info}"
        if with_url and a.get('annc_url'):
            line += f"\n   - [공고 바로가기]({a['annc_url']})"
        lines.append(line)
    return "\n".join(lines)


def format_context(chat_history: List[dict], prev_anncs: List[dict], selected: Optional[dict]) -> str:
    parts = []
    if chat_history:
        recent = chat_history[-6:]
        conv = "\n".join([f"{'사용자' if m['role']=='user' else '챗봇'}: {m['content'][:100]}" for m in recent])
        parts.append(f"[최근 대화]\n{conv}")
    if prev_anncs:
        titles = "\n".join([f"{i}. {a['annc_title'][:40]}" for i, a in enumerate(prev_anncs, 1)])
        parts.append(f"[현재 공고 목록 ({len(prev_anncs)}개)]\n{titles}")
    if selected:
        parts.append(f"[선택된 공고]\n{selected['annc_title']}")
    return "\n\n".join(parts) if parts else "없음"


# =============================================================================
# 노드 1: 의도 분류
# =============================================================================
def classify_intent(state: GraphState) -> GraphState:
    question = state["question"]
    context = format_context(
        state.get("chat_history", []),
        state.get("prev_anncs", []),
        state.get("selected_annc")
    )

    # DB 메타데이터
    db_info = {
        "statuses": ChatbotConfig.get("statuses"),
        "regions": ChatbotConfig.get("regions"),
        "dtl_types": ChatbotConfig.get("dtl_types")
    }

    search_history_info = ""
    if state.get("search_history"):
        hist = [f"- {h['query']}" for h in state["search_history"][-3:]]
        search_history_info = f"\n[이전 검색 기록]\n" + "\n".join(hist)

    prompt = f"""주택 공고 안내 챗봇의 의도 분류기입니다. 사용자 질문의 의도를 정확히 파악하세요.

{context}
{search_history_info}

# DB 메타데이터 (RDB 필터링 가능 값)
- 상태값: {db_info['statuses']}
- 지역(광역시/도): {db_info['regions']}
- 상세유형: {db_info['dtl_types']}

# 의도 분류 (5가지) - 우선순위 순

## 1. `select` - 목록에서 공고 선택 (최우선)
조건: prev_anncs(검색결과 목록)가 있고, 번호/순서로 특정 공고를 지목
예시:
- "1번" / "2번 공고" / "첫번째" / "두번째꺼"
- "1번 공고 알려줘" / "3번 선택"
- "맨 위에꺼" / "마지막 공고"
주의: "1인가구"는 select가 아님 (대상자 검색)

## 2. `detail` - 선택된 공고의 상세 정보 질문
조건: selected_annc(선택된 공고)가 있고, 해당 공고의 세부 정보 질문
예시:
- "신청자격이 뭐야?" / "자격요건 알려줘"
- "면적 정보" / "평수가 어떻게 돼?"
- "임대료" / "보증금" / "월세"
- "신청기간" / "언제까지야?" / "마감일"
- "필요서류" / "제출서류"
- "당첨자 발표일" / "입주일"
주의: 선택된 공고 없이 "신청자격"만 물으면 search

## 3. `compare` - 여러 공고 비교
조건: prev_anncs가 2개 이상이고, 비교 요청
예시:
- "1번이랑 2번 비교해줘"
- "첫번째랑 세번째 뭐가 달라?"
- "둘 다 비교" / "전부 비교해줘"

## 4. `search` - 공고 검색 (신규/추가/복원)
### 4a. 신규 검색 (search_mode: "new")
- 새로운 조건으로 검색, 기존 결과 대체
- "신혼부부 공고 알려줘" / "청년 대상 공고"
- "접수중인 공고" / "공고중인 것들"
- "경기도 행복주택" / "서울 임대"
- "1인가구 공고" / "무주택자 대상"

### 4b. 추가 검색 (search_mode: "add")
- 기존 검색 결과에 추가 (prev_anncs 유지)
- "~도 보여줘" / "~도 추가해줘" / "~도 포함"
- "경기도도 보여줘" / "공고중인 것도"
- "영구임대도 추가" / "서울도 포함해서"

### 4c. 복원 검색 (search_mode: "restore")
- 이전 검색 결과 다시 보기 (search_history 필요)
- "아까 검색한거" / "이전 결과"
- "아까 신혼부부 공고 다시" / "방금 전 검색"

### RDB 필터 추출 규칙
- annc_status: "접수중", "공고중" 등 상태 언급 시
- annc_dtl_type: "행복주택", "영구임대", "매입임대" 등 유형 언급 시
- rag_keywords: 대상자(신혼부부, 청년, 1인), 지역(수원, 서대문), 기타 키워드

## 5. `chat` - 일반 대화/제도 설명
조건: 위 의도에 해당하지 않는 일반 질문
예시:
- 인사: "안녕" / "고마워" / "도움이 됐어"
- 제도 설명: "행복주택이 뭐야?" / "LH가 뭐야?" / "공공임대란?"
- 일반 질문: "청약 자격요건" / "주택청약 방법"
- 최신 정보: "2025년 청약 정책" (needs_web_search: true)

needs_web_search: true인 경우
- 최신 정책/제도 변경 질문
- 구체적 통계/경쟁률 질문
- LLM 지식으로 답하기 어려운 실시간 정보

# 판단 규칙
1. 숫자+"번"은 select, 숫자+"인"은 대상자(search)
2. selected_annc 없이 상세질문 → search로 전환
3. "~도"가 붙으면 add 모드 검토
4. 애매하면 search (신규)로 분류

# 응답 형식 (JSON만 출력)
{{
  "intent": "search|select|detail|compare|chat",
  "search_mode": "new|add|restore",
  "restore_query": null,
  "select_indices": [],  // 1부터 시작! "1번"→[1], "2번"→[2], "1번이랑 3번"→[1,3]
  "rdb_filters": {{
    "annc_status": null,
    "annc_dtl_type": null
  }},
  "rag_keywords": null,
  "needs_web_search": false,
  "reasoning": "판단 근거 한 줄"
}}

# select_indices 주의사항
- 1-indexed: "1번"은 [1], "첫번째"는 [1]
- "마지막"은 [-1]
- 절대 0을 사용하지 말 것"""

    result_str = call_llm(prompt, f"질문: {question}", json_mode=True)

    try:
        result = json.loads(result_str)
        intent = result.get("intent", Intent.CHAT)

        # 검증 및 보정
        prev_anncs = state.get("prev_anncs", [])
        selected = state.get("selected_annc")
        rag_keywords = result.get("rag_keywords", "")

        # 상세 질문 키워드 패턴
        detail_keywords = ['신청자격', '자격', '면적', '평수', '임대료', '보증금', '월세',
                          '신청기간', '마감', '서류', '입주', '당첨', '소득', '자산']

        # 1. selected_annc가 있고 상세 질문 키워드가 있으면 → detail로 보정
        if selected and intent == Intent.SEARCH:
            question_lower = question.lower()
            if any(kw in question_lower for kw in detail_keywords):
                intent = Intent.DETAIL
                result["intent"] = Intent.DETAIL

        # 2. select인데 목록 없으면 → search
        if intent == Intent.SELECT and not prev_anncs:
            intent = Intent.SEARCH

        # 3. detail인데 선택 없고 목록도 없으면 → search
        if intent == Intent.DETAIL and not selected and not prev_anncs:
            intent = Intent.SEARCH

        # 4. compare인데 목록 부족 → search
        if intent == Intent.COMPARE and len(prev_anncs) < 2:
            intent = Intent.SEARCH

        return {
            "intent": intent,
            "intent_data": result,
            "debug_info": {"intent_result": result}
        }
    except Exception as e:
        return {
            "intent": Intent.CHAT,
            "intent_data": {"error": str(e)},
            "debug_info": {"error": str(e)}
        }


# =============================================================================
# 노드 2: 검색 (RDB 필터 + RAG)
# =============================================================================
def expand_query(question: str) -> str:
    prompt = """주택 공고 RAG 검색을 위한 쿼리 확장기입니다.
사용자 질문에서 핵심 키워드를 추출하고 관련 동의어/유의어로 확장합니다.

# 대상자 관련 동의어
- 신혼부부 → 신혼부부, 혼인, 예비신혼부부, 신혼희망타운, 혼인신고, 결혼예정
- 청년 → 청년, 대학생, 사회초년생, 만19세, 만39세, 청년계층
- 1인가구 → 1인, 단독세대, 독신, 1인세대
- 고령자/노인 → 고령자, 주거약자, 노인, 만65세, 고령자계층
- 저소득층 → 저소득, 기초생활수급자, 차상위계층, 소득기준
- 다자녀 → 다자녀, 3자녀, 미성년자녀, 자녀수

# 자격요건 관련
- 신청자격 → 신청자격, 입주자격, 공급대상, 자격요건, 신청대상, 입주대상자
- 무주택 → 무주택, 무주택세대구성원, 무주택요건, 주택소유여부
- 소득기준 → 소득기준, 월평균소득, 도시근로자, 소득요건, 자산기준
- 자산기준 → 자산, 부동산, 자동차, 금융자산, 자산보유

# 주택정보 관련
- 면적 → 면적, 전용면적, 주거전용, 공급면적, 계약면적, 평형, 평수, ㎡
- 임대료 → 임대료, 보증금, 월임대료, 월세, 임대조건, 납부금액
- 위치 → 위치, 소재지, 주소, 단지, 블록, 동, 호

# 일정 관련
- 신청기간 → 신청기간, 접수기간, 모집기간, 청약일정, 신청일
- 마감 → 마감일, 접수마감, 모집마감, 공고기한
- 입주 → 입주예정, 입주일, 입주시기, 계약체결

# 서류 관련
- 서류 → 제출서류, 구비서류, 필요서류, 증빙서류, 첨부서류
- 신청방법 → 신청방법, 접수방법, 청약방법, 인터넷청약

# 규칙
1. 원본 질문의 핵심 키워드 유지
2. 위 동의어 목록에서 관련 키워드 추가
3. 불필요한 조사/어미 제거 (은, 는, 이, 가, 을, 를, 의 등)
4. 공백으로 구분하여 출력
5. 최대 20개 키워드

# 출력 형식
키워드1 키워드2 키워드3 ... (공백 구분, 키워드만)"""
    return call_llm(prompt, f"질문: {question}", temp=0).strip()


def search_announcements(state: GraphState) -> GraphState:
    intent_data = state.get("intent_data", {})
    question = state["question"]
    search_mode = intent_data.get("search_mode", "new")

    # 복원 모드
    if search_mode == "restore":
        restore_query = intent_data.get("restore_query", "")
        for hist in reversed(state.get("search_history", [])):
            if restore_query.lower() in hist["query"].lower():
                return {
                    "prev_anncs": hist["anncs"],
                    "selected_annc": None,
                    "answer": f"이전 검색 결과를 다시 보여드립니다.\n\n{format_annc_list(hist['anncs'])}"
                }
        # 못찾으면 새로 검색
        search_mode = "new"

    # RDB 필터
    rdb_filters = intent_data.get("rdb_filters", {})
    annc_status = rdb_filters.get("annc_status")
    annc_dtl_type = rdb_filters.get("annc_dtl_type")

    # RDB에서 후보 공고 가져오기
    from .models import AnncAll
    queryset = AnncAll.objects.filter(service_status='OPEN')
    if annc_status:
        queryset = queryset.filter(annc_status=annc_status)
    if annc_dtl_type:
        queryset = queryset.filter(annc_dtl_type__icontains=annc_dtl_type)

    candidate_ids = list(queryset.values_list('annc_id', flat=True))

    # RAG 검색
    rag_keywords = intent_data.get("rag_keywords") or question
    expanded = expand_query(rag_keywords)
    embedding = get_embedding(expanded)

    docs = DocChunkService.hybrid_search(
        query_text=expanded,
        query_embedding=embedding,
        top_k=ChatbotConfig.RAG_TOP_K,
        annc_id_filter=candidate_ids if candidate_ids else None
    )

    # 검색된 청크에서 공고 추출
    seen = set()
    annc_ids = []
    for doc in docs:
        aid = doc.get('annc_id')
        if aid and aid not in seen:
            seen.add(aid)
            annc_ids.append(aid)

    # 공고 정보 조회
    new_anncs = []
    if annc_ids:
        anncs = AnncAllService.get_announcements_by_ids(annc_ids)
        annc_map = {a['annc_id']: a for a in anncs}
        for aid in annc_ids:
            if aid in annc_map:
                a = annc_map[aid]
                new_anncs.append({
                    "annc_id": a["annc_id"],
                    "annc_title": a["annc_title"],
                    "annc_status": a.get("annc_status", ""),
                    "annc_region": a.get("annc_region", ""),
                    "annc_deadline_dt": a.get("annc_deadline_dt", ""),
                    "annc_url": a.get("annc_url", ""),
                    "annc_dtl_type": a.get("annc_dtl_type", ""),
                })

    # 추가 모드: 기존 + 새 결과 병합 (중복 제거)
    if search_mode == "add":
        existing = state.get("prev_anncs", [])
        existing_ids = {a["annc_id"] for a in existing}
        for a in new_anncs:
            if a["annc_id"] not in existing_ids:
                existing.append(a)
        new_anncs = existing

    # 검색 히스토리 저장
    search_history = state.get("search_history", []).copy()
    search_history.append({
        "query": question,
        "anncs": new_anncs,
        "timestamp": time.time()
    })
    if len(search_history) > ChatbotConfig.MAX_SEARCH_HISTORY:
        search_history = search_history[-ChatbotConfig.MAX_SEARCH_HISTORY:]

    return {
        "prev_anncs": new_anncs,
        "selected_annc": None,
        "search_history": search_history,
        "retrieved_docs": docs,
        "debug_info": {
            **state.get("debug_info", {}),
            "expanded_query": expanded,
            "rdb_filters": rdb_filters,
            "search_mode": search_mode
        }
    }


# =============================================================================
# 노드 3: 선택
# =============================================================================
def select_announcement(state: GraphState) -> GraphState:
    intent_data = state.get("intent_data", {})
    indices = intent_data.get("select_indices", [1])
    prev_anncs = state.get("prev_anncs", [])

    if not indices:
        indices = [1]

    idx = indices[0]

    # 0-indexed로 온 경우 보정 (LLM이 가끔 0부터 시작)
    if idx == 0:
        idx = 1
    # 마지막 선택
    if idx == -1:
        idx = len(prev_anncs)

    if 1 <= idx <= len(prev_anncs):
        selected = prev_anncs[idx - 1]
        return {
            "selected_annc": selected,
            "selected_anncs": [selected],
            "debug_info": {**state.get("debug_info", {}), "selected_index": idx}
        }
    else:
        return {
            "answer": f"{idx}번 공고가 없습니다. 1~{len(prev_anncs)}번 중 선택해주세요."
        }


# =============================================================================
# 노드 4: 상세 검색 (RAG)
# =============================================================================
def retrieve_details(state: GraphState) -> GraphState:
    question = state["question"]
    selected = state.get("selected_annc")

    if not selected:
        prev_anncs = state.get("prev_anncs", [])
        if len(prev_anncs) == 1:
            selected = prev_anncs[0]
        else:
            return {"answer": "먼저 공고를 선택해주세요."}

    expanded = expand_query(question)
    embedding = get_embedding(expanded)

    # 상세 질문은 더 많은 청크 필요 (여러 단지 정보 포함)
    detail_top_k = ChatbotConfig.RAG_TOP_K + 10  # 25개

    docs = DocChunkService.hybrid_search(
        query_text=expanded,
        query_embedding=embedding,
        top_k=detail_top_k,
        annc_id_filter=[selected["annc_id"]]
    )

    # 면적/임대료 질문 시 해당 키워드가 포함된 청크 보강
    table_keywords = ['면적', '임대료', '보증금', '월세', '계약면적', '전용면적', '평수']
    if any(kw in question for kw in table_keywords):
        from .models import DocChunks
        from django.db.models import Q

        # 해당 공고의 면적/임대료 관련 테이블 청크 직접 조회
        # 1순위: 계약면적, 전용면적 등 면적 키워드 포함 청크
        # 2순위: 단지명 + 숫자 패턴이 있는 테이블 청크
        extra_chunks = DocChunks.objects.filter(
            annc_id=selected["annc_id"]
        ).filter(
            Q(chunk_text__contains='계약면적') |
            Q(chunk_text__contains='전용면적') |
            Q(chunk_text__contains='주거전용') |
            Q(chunk_text__contains='임대보증금') |
            Q(chunk_text__contains='월임대료') |
            Q(chunk_text__contains='공급형별') |
            Q(chunk_text__contains='공급대상') |
            # 단지별 면적 테이블 패턴
            (Q(chunk_type='table') & (
                Q(chunk_text__contains='16A') |
                Q(chunk_text__contains='26B') |
                Q(chunk_text__contains='36') |
                Q(chunk_text__contains='46') |
                Q(chunk_text__contains='㎡')
            ))
        ).order_by('page_num').values('chunk_id', 'chunk_text', 'chunk_type', 'page_num', 'annc_id', 'file_id')

        # 기존 docs에 없는 청크만 추가 (앞쪽에 추가하여 우선순위 높임)
        existing_ids = {d.get('chunk_id') for d in docs}
        extra_list = []
        for chunk in extra_chunks:
            if chunk['chunk_id'] not in existing_ids:
                extra_list.append(dict(chunk))

        # 면적 관련 청크를 앞에 배치 (페이지 순서대로)
        docs = extra_list + docs

    return {
        "selected_annc": selected,
        "retrieved_docs": docs,
        "debug_info": {
            **state.get("debug_info", {}),
            "expanded_query": expanded,
            "retrieved_count": len(docs)
        }
    }


# =============================================================================
# 노드 5: 비교
# =============================================================================
def compare_announcements(state: GraphState) -> GraphState:
    intent_data = state.get("intent_data", {})
    indices = intent_data.get("select_indices", [1, 2])
    prev_anncs = state.get("prev_anncs", [])

    selected_anncs = []
    for idx in indices:
        if 1 <= idx <= len(prev_anncs):
            selected_anncs.append(prev_anncs[idx - 1])

    if len(selected_anncs) < 2:
        return {"answer": "비교할 공고를 2개 이상 선택해주세요."}

    # 각 공고별 RAG 검색
    all_docs = []
    for annc in selected_anncs:
        docs = DocChunkService.hybrid_search(
            query_text="신청자격 임대료 면적 신청기간",
            query_embedding=get_embedding("신청자격 임대료 면적 신청기간"),
            top_k=5,
            annc_id_filter=[annc["annc_id"]]
        )
        all_docs.extend(docs)

    return {
        "selected_anncs": selected_anncs,
        "retrieved_docs": all_docs,
        "debug_info": {**state.get("debug_info", {}), "compare_count": len(selected_anncs)}
    }


# =============================================================================
# 노드 6: 일반 대화 / 웹 검색
# =============================================================================
def general_chat(state: GraphState) -> GraphState:
    question = state["question"]
    intent_data = state.get("intent_data", {})
    needs_web = intent_data.get("needs_web_search", False)

    web_context = ""
    if needs_web and TAVILY_AVAILABLE:
        try:
            result = tavily_client.search(query=question, max_results=3)
            if result.get("results"):
                web_context = "\n\n[웹 검색 결과 - 최신 정보]\n"
                for r in result["results"][:3]:
                    web_context += f"- **{r.get('title', '')}**: {r.get('content', '')[:200]}\n"
                web_context += "\n위 웹 검색 결과를 참고하여 답변하세요."
        except:
            pass

    prompt = f"""주택 공고 안내 전문 챗봇 '집핏(ZIP-FIT)'입니다.
사용자의 주택/임대/청약 관련 질문에 친절하고 정확하게 답변합니다.

# 챗봇 기능 소개
1. **공고 검색**: 지역, 대상자(신혼부부/청년/고령자 등), 상태(접수중/공고중)별 검색
2. **상세 정보 안내**: 신청자격, 면적, 임대료, 신청기간, 필요서류 등
3. **공고 비교**: 여러 공고의 조건 비교 분석
4. **제도 설명**: 행복주택, 영구임대, 매입임대 등 주택 제도 안내

# 현재 서비스 정보
- 검색 가능 지역: {ChatbotConfig.get('regions')}
- 공고 유형: {ChatbotConfig.get('dtl_types')}
- 공고 상태: {ChatbotConfig.get('statuses')}
{web_context}

# 응답 가이드

## 인사/감사 표현
- 친근하고 따뜻하게 응대
- 추가 도움 제안 ("더 궁금한 점이 있으신가요?")

## 주택 제도 설명 질문
행복주택, 영구임대, 매입임대, 공공임대 등의 제도 질문에는:
- 정의와 목적
- 주요 대상자
- 특징/장점
- 신청 방법 개요

## 청약/자격 일반 질문
- 일반적인 자격요건 설명
- 구체적인 정보는 "공고 검색 후 확인" 안내
- 예: "신혼부부 공고 검색해줘"로 검색 유도

## LH/SH 등 기관 질문
- 기관 소개 및 역할
- 주요 사업 설명
- 공식 웹사이트 안내

## 최신 정책/제도 변경 질문
- 웹 검색 결과가 있으면 해당 정보 기반 답변
- 없으면: "최신 정책은 LH 또는 국토교통부 홈페이지에서 확인해주세요."

## 서비스 범위 외 질문
- 정중히 범위 외임을 알림
- 가능한 대안 제시 (예: 관련 기관 안내)

# 응답 스타일
- 친절하고 전문적인 톤
- 명확하고 구조화된 답변
- 불필요한 수식어 자제
- 필요시 마크다운 활용"""

    messages = [{"role": "system", "content": prompt}]
    messages.extend(state.get("chat_history", [])[-6:])
    messages.append({"role": "user", "content": question})

    resp = client.chat.completions.create(
        model=ChatbotConfig.LLM_MODEL,
        messages=messages,
        temperature=0.7
    )
    return {"answer": resp.choices[0].message.content}


# =============================================================================
# 응답 생성
# =============================================================================
def generate_search_response(state: GraphState) -> GraphState:
    question = state["question"]
    anncs = state.get("prev_anncs", [])
    docs = state.get("retrieved_docs", [])

    if not anncs:
        return {"answer": "조건에 맞는 공고를 찾지 못했습니다. 다른 조건으로 검색해보세요."}

    context = "\n".join([f"[공고:{d.get('annc_id')}, p{d.get('page_num')}] {d.get('chunk_text', '')[:200]}" for d in docs[:8]])

    prompt = f"""주택 공고 검색 결과를 사용자에게 친절하게 안내하는 챗봇입니다.

# 사용자 질문
{question}

# 검색된 공고 목록 (번호 필수 사용!)
{format_annc_list(anncs, with_url=False)}

# 검색된 문서 내용 (RAG)
{context}

# 응답 작성 규칙

## 필수 규칙
1. 반드시 위 [검색된 공고 목록]의 번호(1번, 2번...)를 사용하여 공고를 언급할 것
2. 목록에 없는 공고명이나 번호를 절대 언급하지 말 것
3. 문서 내용을 참고하여 사용자 질문에 맞는 공고를 추천

## 응답 구조
1. **추천 요약** (1-2문장): 질문에 가장 적합한 공고 번호와 이유
2. **간단한 설명** (2-3문장): 왜 해당 공고가 적합한지 문서 기반 설명
3. **다음 안내**: "N번 공고 알려줘"로 상세 정보 확인 유도

## 응답 스타일
- 친절하고 간결한 톤
- 불필요한 서론 없이 바로 본론
- 마크다운 사용 가능 (볼드, 리스트 등)
- 전체 5문장 이내"""

    answer = call_llm(prompt, question, temp=0.3)
    answer += "\n\n---\n" + format_annc_list(anncs)
    return {"answer": answer}


def generate_detail_response(state: GraphState) -> GraphState:
    question = state["question"]
    selected = state.get("selected_annc")
    docs = state.get("retrieved_docs", [])

    if not selected:
        return {"answer": "선택된 공고가 없습니다."}

    dday = calculate_dday(selected.get('annc_deadline_dt', ''))
    dday_str = f" ({dday})" if dday else ""

    # 면적/임대료 질문은 더 많은 청크 필요 (여러 단지 정보 포함)
    table_keywords = ['면적', '임대료', '보증금', '월세', '평수']
    if any(kw in question for kw in table_keywords):
        max_chunks = 20  # 면적/임대료 질문은 더 많은 청크
    else:
        max_chunks = 12

    context = "\n\n".join([f"[p{d.get('page_num', '?')}]\n{d.get('chunk_text', '')}" for d in docs[:max_chunks]])

    prompt = f"""주택 공고의 상세 정보를 안내하는 챗봇입니다.
검색된 문서를 기반으로 사용자 질문에 정확하게 답변합니다.

# 사용자 질문
{question}

# 현재 선택된 공고
- 제목: {selected.get('annc_title')}
- 상태: {selected.get('annc_status')}
- 지역: {selected.get('annc_region')}
- 마감일: {selected.get('annc_deadline_dt', '정보없음')}{dday_str}
- 유형: {selected.get('annc_dtl_type', '')}

# 검색된 문서 내용
{context}

# 응답 작성 규칙

## 필수 규칙
1. **문서 기반 답변**: 위 [검색된 문서 내용]에 있는 정보만 사용
2. **출처 명시**: 답변에 페이지 번호 포함 (예: "p3 참조")
3. **정보 없을 시**: "해당 정보는 공고문에서 찾지 못했습니다. 공고 원문을 확인해주세요."

## ⚠️ 깨진 테이블 데이터 해석 지침
PDF에서 추출된 표 데이터는 줄바꿈으로 분리되어 깨져 있을 수 있습니다.
- 컬럼명이 여러 줄로 나뉨 (예: "공급\\n형별" → "공급형별", "전용\\n면적" → "전용면적")
- 데이터와 헤더가 분리됨
- 구분선(---|---)과 실제 데이터 혼재

**해석 방법**:
1. 표의 구조를 파악하고 헤더와 데이터를 매칭
2. 단지명, 타입, 면적 숫자들의 패턴 인식
3. 비슷한 패턴의 행들을 묶어서 해석
4. 숫자 값(면적: 16.95, 26.87 등 / 금액: 5,000천원 등)을 정확히 추출

**예시 해석**:
- "16A | 16.95 | 5,000 | 50" → 16A타입, 전용면적 16.95㎡, 보증금 5,000천원, 월세 50천원
- 여러 단지가 나오면 (양주옥정3, 양주고읍, 동두천송내 등) 각각 구분하여 표시

## 질문 유형별 답변 가이드

### 신청자격/입주자격 질문
- 대상자 유형별 자격요건 정리
- 소득/자산 기준 포함
- 무주택 요건 설명

### 면적/평수 질문
- 표 형식으로 정리 (전용면적, 공급면적 등)
- **여러 단지가 있으면 단지별로 모두 표시** (예: 동두천 송내, 양주 고읍 등)
- 타입별(16A, 26B 등) 구분 명시
- ㎡ 단위 사용
- **깨진 표에서도 숫자 값들을 정확히 추출하여 표시**

### 임대료/보증금 질문
- 표 형식 권장 (타입별, 계층별)
- **여러 단지가 있으면 단지별로 모두 표시**
- 보증금/월임대료 구분
- 전환보증금 정보 있으면 포함
- **단위 표기 주의**: 천원/만원 단위 확인

### 신청기간/일정 질문
- 날짜 명확히 표기
- 단계별 일정 (신청→발표→계약→입주) 정리
- 온라인/오프라인 접수 구분

### 서류/신청방법 질문
- 필요 서류 리스트 형식
- 발급처/유의사항 포함
- 인터넷 청약 URL 있으면 안내

## 응답 스타일
- 마크다운 표/리스트 적극 활용
- 복잡한 정보는 구조화하여 가독성 높이기
- 핵심 내용 먼저, 부가 설명 나중에

## 긴급 안내
- {dday_str}이 D-7 이내면: "⚠️ 마감이 얼마 남지 않았습니다. 서둘러 신청하세요!"
- {dday_str}이 D-Day/마감이면: "⚠️ 오늘이 마감일입니다!"""

    answer = call_llm(prompt, question, temp=0.2)
    if selected.get('annc_url'):
        answer += f"\n\n📎 [공고 원문 바로가기]({selected['annc_url']})"
    return {"answer": answer}


def generate_compare_response(state: GraphState) -> GraphState:
    selected_anncs = state.get("selected_anncs", [])
    docs = state.get("retrieved_docs", [])

    if len(selected_anncs) < 2:
        return {"answer": "비교할 공고가 부족합니다."}

    annc_info = "\n".join([f"- {a['annc_title']} ({a['annc_region']}, {a['annc_status']})" for a in selected_anncs])
    context = "\n".join([f"[공고:{d.get('annc_id')}, p{d.get('page_num')}] {d.get('chunk_text', '')[:300]}" for d in docs[:10]])

    # 공고별 상세 정보 정리
    annc_details = []
    for a in selected_anncs:
        dday = calculate_dday(a.get('annc_deadline_dt', ''))
        detail = f"""### {a['annc_title']}
- 지역: {a.get('annc_region', '정보없음')}
- 상태: {a.get('annc_status', '')}
- 유형: {a.get('annc_dtl_type', '')}
- 마감: {a.get('annc_deadline_dt', '정보없음')} {f'({dday})' if dday else ''}"""
        annc_details.append(detail)

    prompt = f"""여러 주택 공고를 비교 분석하여 사용자에게 안내하는 챗봇입니다.

# 비교 대상 공고
{chr(10).join(annc_details)}

# 각 공고 관련 문서 내용
{context}

# 응답 작성 규칙

## 필수 비교 항목 (표 형식)
| 항목 | 공고1 | 공고2 | ... |
|------|-------|-------|-----|
| 지역/위치 | | | |
| 대상자 | | | |
| 신청자격 | | | |
| 전용면적 | | | |
| 임대조건(보증금/월세) | | | |
| 신청기간/마감일 | | | |

## 추가 분석 내용
1. **각 공고의 특징/장점** (2-3줄씩)
2. **추천 대상**
   - "신혼부부라면 → N번 공고"
   - "청년 1인 가구라면 → N번 공고"
   - "소득이 낮다면 → N번 공고"
3. **주의사항** (마감 임박, 경쟁률 예상 등)

## 응답 스타일
- 객관적이고 중립적인 비교
- 마크다운 표 적극 활용
- 문서에 없는 정보는 "정보 없음"으로 표기
- 마지막에 "더 자세한 정보는 'N번 공고 알려줘'로 확인하세요" 안내"""

    return {"answer": call_llm(prompt, "비교 분석해줘", temp=0.3)}


# =============================================================================
# 라우터
# =============================================================================
def route_intent(state: GraphState) -> str:
    intent = state.get("intent", Intent.CHAT)
    return {
        Intent.SEARCH: "search",
        Intent.SELECT: "select",
        Intent.DETAIL: "detail",
        Intent.COMPARE: "compare",
        Intent.CHAT: "chat"
    }.get(intent, "chat")


def route_after_select(state: GraphState) -> str:
    if state.get("answer"):
        return "end"
    return "detail_retrieve"


# =============================================================================
# 그래프 구성
# =============================================================================
def create_chatbot_graph():
    g = StateGraph(GraphState)

    # 노드
    g.add_node("classify", classify_intent)
    g.add_node("search", search_announcements)
    g.add_node("select", select_announcement)
    g.add_node("detail_retrieve", retrieve_details)
    g.add_node("compare", compare_announcements)
    g.add_node("chat", general_chat)
    g.add_node("search_response", generate_search_response)
    g.add_node("detail_response", generate_detail_response)
    g.add_node("compare_response", generate_compare_response)

    # 시작
    g.set_entry_point("classify")

    # 의도별 라우팅
    g.add_conditional_edges("classify", route_intent, {
        "search": "search",
        "select": "select",
        "detail": "detail_retrieve",
        "compare": "compare",
        "chat": "chat"
    })

    # 선택 후 라우팅
    g.add_conditional_edges("select", route_after_select, {
        "detail_retrieve": "detail_retrieve",
        "end": END
    })

    # 고정 엣지
    g.add_edge("search", "search_response")
    g.add_edge("search_response", END)
    g.add_edge("detail_retrieve", "detail_response")
    g.add_edge("detail_response", END)
    g.add_edge("compare", "compare_response")
    g.add_edge("compare_response", END)
    g.add_edge("chat", END)

    return g.compile()


# =============================================================================
# 인터페이스
# =============================================================================
_chatbot = None


def get_chatbot():
    global _chatbot
    if _chatbot is None:
        _chatbot = create_chatbot_graph()
    return _chatbot


def chat(question: str, session_state: dict = None) -> dict:
    session_state = session_state or {}

    initial = {
        "question": question,
        "chat_history": session_state.get("chat_history", []),
        "search_history": session_state.get("search_history", []),
        "prev_anncs": session_state.get("prev_anncs", []),
        "selected_annc": session_state.get("selected_annc"),
        "selected_anncs": [],
        "intent": "",
        "intent_data": {},
        "retrieved_docs": [],
        "answer": "",
        "debug_info": {}
    }

    result = get_chatbot().invoke(initial)

    # 히스토리 업데이트
    history = session_state.get("chat_history", []).copy()
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": result.get("answer", "")})

    max_len = ChatbotConfig.MAX_HISTORY_TURNS * 2
    if len(history) > max_len:
        history = history[-max_len:]

    return {
        "answer": result.get("answer", "오류가 발생했습니다."),
        "session_state": {
            "chat_history": history,
            "search_history": result.get("search_history", session_state.get("search_history", [])),
            "prev_anncs": result.get("prev_anncs", session_state.get("prev_anncs", [])),
            "selected_annc": result.get("selected_annc", session_state.get("selected_annc"))
        },
        "debug_info": result.get("debug_info", {})
    }
