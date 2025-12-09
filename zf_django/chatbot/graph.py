# chatbot/graph.py
"""
LangGraph 기반 주택 공고 챗봇 (V5)
- LLM 기반 의도 분류 (Intent Classification)
- 대화 맥락 유지 (Conversation Context)
- 조건부 라우팅 (Conditional Routing)
- 확장 가능한 구조
"""
import json
from typing import TypedDict, List, Optional, Literal
from langgraph.graph import StateGraph, END
from openai import OpenAI
from decouple import config

from .services import AnncAllService, DocChunkService

# OpenAI 클라이언트
client = OpenAI(api_key=config('OPENAI_API_KEY'))

# -----------------------------------------------------------------------------
# 설정 (DB에서 동적으로 가져오도록 확장 가능)
# -----------------------------------------------------------------------------
class ChatbotConfig:
    """챗봇 설정 - 확장 시 DB나 환경변수에서 로드 가능"""
    REGIONS = ['서울특별시', '경기도']
    STATUSES = ['접수중', '공고중']
    LLM_MODEL = "gpt-4o-mini"
    EMBEDDING_MODEL = "text-embedding-3-small"
    MAX_HISTORY_TURNS = 10  # 최대 대화 기록 턴 수
    RAG_TOP_K = 10


# -----------------------------------------------------------------------------
# 의도(Intent) 정의
# -----------------------------------------------------------------------------
class Intent:
    """사용자 의도 타입"""
    NEW_SEARCH = "new_search"           # 새로운 검색 요청
    REFERENCE_PREV = "reference_prev"   # 이전 결과 참조 (1번 공고, 첫번째 등)
    DETAIL_QUESTION = "detail_question" # 선택된 공고에 대한 상세 질문
    GENERAL_CHAT = "general_chat"       # 일반 대화 (인사, 도움말 등)
    CLARIFICATION = "clarification"     # 명확화 필요 (모호한 질문)


# -----------------------------------------------------------------------------
# State 정의
# -----------------------------------------------------------------------------
class GraphState(TypedDict):
    # 입력
    question: str
    chat_history: List[dict]  # [{"role": "user/assistant", "content": "..."}]

    # 의도 분류 결과
    intent: str
    intent_data: dict  # 의도별 추가 데이터 (검색 조건, 참조 인덱스 등)

    # 검색 조건 및 결과
    search_filters: dict
    candidate_anncs: List[dict]
    retrieved_docs: List[dict]

    # 대화 맥락
    prev_anncs: List[dict]      # 이전에 보여준 공고 목록
    selected_annc: Optional[dict]  # 현재 선택된 공고

    # 출력
    answer: str
    debug_info: dict  # 디버깅용


# -----------------------------------------------------------------------------
# 유틸리티 함수
# -----------------------------------------------------------------------------
def get_embedding(text: str) -> List[float]:
    """텍스트 임베딩 생성"""
    response = client.embeddings.create(
        input=text,
        model=ChatbotConfig.EMBEDDING_MODEL
    )
    return response.data[0].embedding


def format_annc_list(anncs: List[dict], include_index: bool = True) -> str:
    """공고 목록 포맷팅"""
    if not anncs:
        return "검색된 공고가 없습니다."

    lines = []
    for i, annc in enumerate(anncs, 1):
        title = annc.get('annc_title', '제목 없음')
        status = annc.get('annc_status', '')
        region = annc.get('annc_region', '')

        if include_index:
            lines.append(f"{i}. **{title}**\n   - 상태: {status} | 지역: {region}")
        else:
            lines.append(f"**{title}**\n   - 상태: {status} | 지역: {region}")

    return "\n".join(lines)


def get_recent_context(chat_history: List[dict], max_turns: int = 5) -> str:
    """최근 대화 맥락을 문자열로 변환"""
    recent = chat_history[-(max_turns * 2):]  # user/assistant 쌍
    if not recent:
        return "이전 대화 없음"

    lines = []
    for msg in recent:
        role = "사용자" if msg["role"] == "user" else "챗봇"
        content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def call_llm(system_prompt: str, user_message: str, json_mode: bool = False, temperature: float = 0) -> str:
    """LLM 호출 헬퍼 함수"""
    kwargs = {
        "model": ChatbotConfig.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": temperature
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


# -----------------------------------------------------------------------------
# 노드 1: 의도 분류 (Intent Classifier)
# -----------------------------------------------------------------------------
def intent_classifier(state: GraphState) -> GraphState:
    """
    사용자 질문의 의도를 분류하고 필요한 정보 추출
    - 새 검색 / 이전 결과 참조 / 상세 질문 / 일반 대화 구분
    """
    question = state["question"]
    chat_history = state.get("chat_history", [])
    prev_anncs = state.get("prev_anncs", [])
    selected_annc = state.get("selected_annc")

    # 이전 공고 목록 정보
    prev_anncs_info = ""
    if prev_anncs:
        prev_anncs_info = f"""
# 이전에 보여준 공고 목록 ({len(prev_anncs)}개)
{format_annc_list(prev_anncs)}
"""

    # 현재 선택된 공고 정보
    selected_info = ""
    if selected_annc:
        selected_info = f"""
# 현재 선택된 공고
- 제목: {selected_annc.get('annc_title')}
- ID: {selected_annc.get('annc_id')}
"""

    system_prompt = f"""당신은 주택 공고 챗봇의 의도 분류기입니다.
사용자 질문을 분석하여 의도를 분류하고 필요한 정보를 추출하세요.

# 대화 맥락
{get_recent_context(chat_history)}
{prev_anncs_info}
{selected_info}

# DB 정보
- 지역: {ChatbotConfig.REGIONS}
- 상태: {ChatbotConfig.STATUSES}
- 유형: 모두 '임대' (별도 필터 불필요)

# 의도 유형 (우선순위 순)
1. `reference_prev`: 이전에 보여준 목록에서 특정 공고 선택/질문
   - "1번 공고", "첫번째꺼", "두번째 공고 알려줘"
   - "1번 공고 신청자격 알려줘", "2번 신청기간은?" (번호 + 질문도 여기!)
   - 반드시 이전 공고 목록이 있어야 함
   - **중요**: 번호가 언급되면 무조건 reference_prev

2. `detail_question`: 현재 선택된 공고에 대한 상세 질문 (번호 없이)
   - "신청자격이 뭐야?", "언제까지야?", "어떻게 신청해?"
   - 반드시 현재 선택된 공고가 있어야 함
   - **중요**: 번호 없이 질문만 있을 때

3. `new_search`: 새로운 공고 검색 요청
   - "서울 청년 공고 보여줘", "접수중인 공고 알려줘", "경기도 신혼 임대"

4. `general_chat`: 일반 대화 (인사, 도움말, 기능 설명 등)
   - "안녕", "뭘 할 수 있어?", "도와줘"

5. `clarification`: 모호하여 명확화가 필요한 경우
   - 이전 목록 없이 "그거", "1번" 등 참조하는 경우

# 응답 형식 (JSON)
{{
  "intent": "new_search" | "reference_prev" | "detail_question" | "general_chat" | "clarification",
  "confidence": 0.0-1.0,
  "reasoning": "판단 이유 간략히",

  // new_search인 경우
  "search_filters": {{
    "annc_region": "서울특별시" | "경기도" | null,
    "annc_status": ["접수중"] | ["공고중"] | ["접수중", "공고중"],
    "keyword": "청년" | "신혼 행복주택" | null,
    "invalid_region": "부산" | null  // DB에 없는 지역을 사용자가 언급한 경우
  }},

  // reference_prev인 경우 (번호 + 질문 포함)
  "reference_index": 1,  // 1-based 인덱스, "마지막"은 -1
  "follow_up_question": "신청자격" | null,  // 번호와 함께 질문이 있으면 여기에

  // detail_question인 경우
  "question_topic": "신청자격" | "신청기간" | "신청방법" | "자격요건" | "기타"
}}
"""

    result_str = call_llm(system_prompt, f"사용자 질문: {question}", json_mode=True)

    try:
        result = json.loads(result_str)
        intent = result.get("intent", Intent.GENERAL_CHAT)

        # 검증: reference_prev인데 이전 목록이 없으면 clarification으로 변경
        if intent == Intent.REFERENCE_PREV and not prev_anncs:
            intent = Intent.CLARIFICATION
            result["reasoning"] = "이전에 보여준 공고 목록이 없어서 참조 불가"

        # 검증: detail_question인데 선택된 공고가 없으면 처리
        if intent == Intent.DETAIL_QUESTION and not selected_annc:
            # 이전 목록이 있고 1개면 자동 선택
            if prev_anncs and len(prev_anncs) == 1:
                return {
                    "intent": Intent.DETAIL_QUESTION,
                    "intent_data": result,
                    "search_filters": {},
                    "selected_annc": prev_anncs[0],  # 자동 선택
                    "candidate_anncs": [prev_anncs[0]],
                    "debug_info": {"intent_result": result, "auto_selected": True}
                }
            else:
                intent = Intent.CLARIFICATION
                result["reasoning"] = "선택된 공고가 없어서 상세 질문 불가"

        return {
            "intent": intent,
            "intent_data": result,
            "search_filters": result.get("search_filters", {}),
            "debug_info": {"intent_result": result}
        }
    except Exception as e:
        return {
            "intent": Intent.GENERAL_CHAT,
            "intent_data": {"error": str(e)},
            "search_filters": {},
            "debug_info": {"error": str(e)}
        }


# -----------------------------------------------------------------------------
# 노드 2: 참조 해결 (Reference Resolver)
# -----------------------------------------------------------------------------
def reference_resolver(state: GraphState) -> GraphState:
    """이전 목록에서 참조된 공고 선택"""
    prev_anncs = state.get("prev_anncs", [])
    intent_data = state.get("intent_data", {})

    ref_index = intent_data.get("reference_index", 1)

    # 마지막(-1) 처리
    if ref_index == -1:
        ref_index = len(prev_anncs)

    # 유효한 인덱스인지 확인
    if 1 <= ref_index <= len(prev_anncs):
        selected = prev_anncs[ref_index - 1]

        # follow_up_question이 있으면 원래 질문 대신 사용
        # (RAG 검색 시 더 정확한 결과를 위해)
        follow_up = intent_data.get("follow_up_question")

        return {
            "selected_annc": selected,
            "candidate_anncs": [selected],  # RAG 검색 대상
            "debug_info": {
                **state.get("debug_info", {}),
                "selected_index": ref_index,
                "follow_up_question": follow_up
            }
        }
    else:
        return {
            "selected_annc": None,
            "answer": f"죄송합니다. {ref_index}번 공고가 목록에 없습니다. 1~{len(prev_anncs)}번 중에서 선택해주세요."
        }


# -----------------------------------------------------------------------------
# 노드 3: DB 검색 (RDB Searcher)
# -----------------------------------------------------------------------------
def rdb_searcher(state: GraphState) -> GraphState:
    """DB에서 공고 검색"""
    filters = state.get("search_filters", {})

    # 기본값 설정
    annc_status = filters.get("annc_status") or ["접수중", "공고중"]

    results = AnncAllService.search_announcements(
        annc_status=annc_status,
        annc_type=None,
        annc_region=filters.get("annc_region"),
        keyword=filters.get("keyword"),
        limit=20
    )

    candidate_anncs = [
        {
            "annc_id": annc["annc_id"],
            "annc_title": annc["annc_title"],
            "annc_status": annc.get("annc_status", ""),
            "annc_region": annc.get("annc_region", ""),
        }
        for annc in results
    ]

    return {
        "candidate_anncs": candidate_anncs,
        "prev_anncs": candidate_anncs,  # 다음 턴을 위해 저장
        "debug_info": {
            **state.get("debug_info", {}),
            "search_filters": filters,
            "result_count": len(candidate_anncs)
        }
    }


# -----------------------------------------------------------------------------
# 노드 4: RAG 검색 (Retriever)
# -----------------------------------------------------------------------------
def expand_query_with_llm(question: str) -> str:
    """
    LLM을 사용하여 검색 쿼리 확장
    - 동의어, 관련 키워드 추가
    - 주택 공고 도메인 특화
    """
    system_prompt = """당신은 주택 공고 문서 검색을 위한 쿼리 확장기입니다.
사용자 질문을 분석하여 검색에 유용한 키워드들을 추가하세요.

# 규칙
1. 원래 질문의 핵심 키워드 유지
2. 주택 공고 문서에서 사용되는 동의어/유사어 추가
3. 공백으로 구분된 키워드 나열 형태로 출력
4. 최대 10개 키워드

# 예시
- "신청기간은 언제야?" → "신청기간 접수기간 청약기간 모집기간 청약신청 신청일정 일정"
- "신청자격 알려줘" → "신청자격 입주자격 자격요건 지원자격 신청조건 자격"
- "임대료 얼마야?" → "임대료 월임대료 임대보증금 보증금 월세 납부금액"
- "어떻게 신청해?" → "신청방법 청약방법 접수방법 신청절차 인터넷신청 방문신청"

# 출력
키워드만 공백으로 구분하여 출력 (설명 없이)
"""

    result = call_llm(system_prompt, question, temperature=0)
    return result.strip()


def retriever(state: GraphState) -> GraphState:
    """벡터 검색으로 관련 문서 청크 검색"""
    candidate_anncs = state.get("candidate_anncs", [])
    selected_annc = state.get("selected_annc")
    question = state["question"]

    # candidate_anncs가 없으면 selected_annc 사용
    if not candidate_anncs and selected_annc:
        candidate_anncs = [selected_annc]

    if not candidate_anncs:
        return {"retrieved_docs": []}

    # LLM으로 쿼리 확장 (동의어 추가)
    expanded_query = expand_query_with_llm(question)

    query_embedding = get_embedding(expanded_query)
    annc_ids = [a["annc_id"] for a in candidate_anncs]

    docs = DocChunkService.hybrid_search(
        query_text=expanded_query,
        query_embedding=query_embedding,
        top_k=ChatbotConfig.RAG_TOP_K,
        annc_id_filter=annc_ids
    )

    return {
        "retrieved_docs": docs,
        "debug_info": {
            **state.get("debug_info", {}),
            "retrieved_count": len(docs),
            "original_query": question,
            "expanded_query": expanded_query
        }
    }


# -----------------------------------------------------------------------------
# 노드 5: 응답 생성 (Response Generators)
# -----------------------------------------------------------------------------
def generate_search_response(state: GraphState) -> GraphState:
    """새 검색 결과에 대한 응답 생성"""
    candidate_anncs = state.get("candidate_anncs", [])
    filters = state.get("search_filters", {})

    # DB에 없는 지역을 요청한 경우
    invalid_region = filters.get("invalid_region")
    if invalid_region:
        answer = f"죄송합니다. **{invalid_region}** 지역의 공고는 현재 등록되어 있지 않습니다.\n\n"
        answer += f"**현재 검색 가능한 지역:**\n"
        for region in ChatbotConfig.REGIONS:
            answer += f"- {region}\n"
        answer += f"\n예: '{ChatbotConfig.REGIONS[0]} 공고 보여줘'"
        return {"answer": answer}

    if not candidate_anncs:
        # 검색 결과 없음
        conditions = []
        if filters.get("annc_region"):
            conditions.append(f"지역: {filters['annc_region']}")
        if filters.get("keyword"):
            conditions.append(f"키워드: {filters['keyword']}")
        if filters.get("annc_status"):
            conditions.append(f"상태: {', '.join(filters['annc_status'])}")

        cond_str = ", ".join(conditions) if conditions else "전체"
        answer = f"죄송합니다. [{cond_str}] 조건에 맞는 공고를 찾지 못했습니다.\n\n"
        answer += "**검색 팁:**\n"
        answer += "- '서울 공고 보여줘' - 지역별 검색\n"
        answer += "- '접수중인 공고' - 상태별 검색\n"
        answer += "- '청년 임대' - 키워드 검색"
        return {"answer": answer}

    # 검색 결과 있음
    header = f"총 **{len(candidate_anncs)}개**의 공고를 찾았습니다.\n\n"
    annc_list = format_annc_list(candidate_anncs)
    footer = "\n\n궁금한 공고 번호를 말씀해주시면 자세한 정보를 알려드릴게요. (예: \"1번 공고 알려줘\")"

    return {"answer": header + annc_list + footer}


def generate_detail_response(state: GraphState) -> GraphState:
    """선택된 공고에 대한 상세 응답 생성 (RAG 기반)"""
    question = state["question"]
    selected_annc = state.get("selected_annc")
    retrieved_docs = state.get("retrieved_docs", [])

    if not selected_annc:
        return {"answer": "선택된 공고가 없습니다. 먼저 공고를 검색해주세요."}

    # 공고 기본 정보
    annc_title = selected_annc.get('annc_title', '제목 없음')
    annc_status = selected_annc.get('annc_status', '')
    annc_region = selected_annc.get('annc_region', '')

    # RAG 검색 결과가 없는 경우 - 공고 기본 정보 + 안내
    if not retrieved_docs:
        answer = f"**{annc_title}**\n\n"
        answer += f"- 상태: {annc_status}\n"
        answer += f"- 지역: {annc_region}\n\n"
        answer += "이 공고에 대해 더 궁금한 점이 있으시면 질문해주세요!\n"
        answer += "(예: 신청자격, 신청기간, 신청방법, 임대료 등)"
        return {"answer": answer}

    # RAG 컨텍스트 구성
    context = "\n\n".join([
        f"[페이지 {doc.get('page_num', '?')}]\n{doc.get('chunk_text', '')}"
        for doc in retrieved_docs[:5]
    ])

    system_prompt = f"""주택 공고 안내 챗봇입니다. 아래 문서를 바탕으로 사용자 질문에 답변하세요.

# 선택된 공고 정보
- 제목: {annc_title}
- 상태: {annc_status}
- 지역: {annc_region}

# 참고 문서
{context}

# 답변 규칙
1. 사용자가 공고에 대해 물어보면 (예: "이거 뭐야?", "알려줘") 먼저 공고 기본 정보(제목, 상태, 지역)를 안내하세요.
2. 구체적인 질문(신청자격, 신청기간 등)은 문서 내용을 바탕으로 답변하고 출처(페이지)를 명시하세요.
3. 문서에 관련 정보가 없으면 공고 기본 정보를 제공하고 "더 구체적인 질문을 해주세요"라고 안내하세요.
4. 친절하고 명확하게 답변하세요.
5. 추가 질문을 유도하세요 (예: 신청자격, 신청기간, 임대료 등).
"""

    answer = call_llm(system_prompt, question, temperature=0.2)

    return {"answer": answer}


def generate_general_response(state: GraphState) -> GraphState:
    """일반 대화 응답 생성"""
    question = state["question"]
    chat_history = state.get("chat_history", [])

    system_prompt = """당신은 친절한 주택 공고 안내 챗봇입니다.

# 기능 안내
- 주택 공고 검색 (지역별, 상태별, 키워드별)
- 공고 상세 정보 안내 (신청자격, 신청기간, 신청방법 등)
- 임대주택 관련 일반 질문 답변

# 응답 규칙
1. 친절하고 자연스럽게 대화하세요.
2. 주택 공고 검색을 유도하세요.
3. 예시를 들어 사용법을 안내하세요.

# 예시 질문 안내
- "서울 청년 임대 공고 보여줘"
- "접수중인 공고 알려줘"
- "신혼부부 주택 있어?"
"""

    # 최근 대화 포함
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:  # 최근 3턴
        messages.append(msg)
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=ChatbotConfig.LLM_MODEL,
        messages=messages,
        temperature=0.7
    )

    return {"answer": response.choices[0].message.content}


def generate_clarification_response(state: GraphState) -> GraphState:
    """명확화 요청 응답 생성"""
    intent_data = state.get("intent_data", {})
    prev_anncs = state.get("prev_anncs", [])

    reasoning = intent_data.get("reasoning", "")

    if "이전에 보여준 공고 목록이 없" in reasoning:
        answer = "어떤 공고를 찾고 계신가요? 먼저 검색을 해주세요.\n\n"
        answer += "**예시:**\n"
        answer += "- '서울 공고 보여줘'\n"
        answer += "- '접수중인 공고 알려줘'\n"
        answer += "- '청년 임대 공고'"
    elif "선택된 공고가 없" in reasoning:
        if prev_anncs:
            answer = "어떤 공고에 대해 알고 싶으신가요?\n\n"
            answer += f"현재 보여드린 공고 목록:\n{format_annc_list(prev_anncs)}\n\n"
            answer += "번호를 말씀해주세요. (예: '1번 공고')"
        else:
            answer = "먼저 공고를 검색해주세요.\n\n"
            answer += "**예시:** '서울 청년 임대 공고 보여줘'"
    else:
        answer = "질문을 잘 이해하지 못했습니다. 다시 말씀해주시겠어요?\n\n"
        answer += "**사용 예시:**\n"
        answer += "- '서울 공고 보여줘' - 공고 검색\n"
        answer += "- '1번 공고 알려줘' - 상세 정보\n"
        answer += "- '신청자격이 뭐야?' - 선택한 공고 질문"

    return {"answer": answer}


# -----------------------------------------------------------------------------
# 라우터 함수
# -----------------------------------------------------------------------------
def route_by_intent(state: GraphState) -> str:
    """의도에 따라 다음 노드 결정"""
    intent = state.get("intent", Intent.GENERAL_CHAT)

    if intent == Intent.NEW_SEARCH:
        return "rdb_searcher"
    elif intent == Intent.REFERENCE_PREV:
        return "reference_resolver"
    elif intent == Intent.DETAIL_QUESTION:
        # selected_annc와 candidate_anncs가 설정되어 있어야 함
        selected = state.get("selected_annc")
        if selected:
            return "retriever"
        else:
            return "clarification_response"
    elif intent == Intent.CLARIFICATION:
        return "clarification_response"
    else:
        return "general_response"


def route_after_reference(state: GraphState) -> str:
    """참조 해결 후 라우팅"""
    selected_annc = state.get("selected_annc")
    if selected_annc:
        return "retriever"
    else:
        return "end"  # 에러 메시지가 이미 설정됨


def route_after_search(state: GraphState) -> str:
    """검색 후 라우팅 - 결과 있으면 바로 응답, 없으면 응답"""
    return "search_response"


def route_after_retrieval(state: GraphState) -> str:
    """RAG 검색 후 라우팅"""
    return "detail_response"


# -----------------------------------------------------------------------------
# 그래프 구성
# -----------------------------------------------------------------------------
def create_chatbot_graph():
    """LangGraph 워크플로우 생성"""
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("intent_classifier", intent_classifier)
    workflow.add_node("reference_resolver", reference_resolver)
    workflow.add_node("rdb_searcher", rdb_searcher)
    workflow.add_node("retriever", retriever)
    workflow.add_node("search_response", generate_search_response)
    workflow.add_node("detail_response", generate_detail_response)
    workflow.add_node("general_response", generate_general_response)
    workflow.add_node("clarification_response", generate_clarification_response)

    # 시작점
    workflow.set_entry_point("intent_classifier")

    # 의도 분류 후 조건부 라우팅
    workflow.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "rdb_searcher": "rdb_searcher",
            "reference_resolver": "reference_resolver",
            "retriever": "retriever",
            "general_response": "general_response",
            "clarification_response": "clarification_response"
        }
    )

    # 참조 해결 후 라우팅
    workflow.add_conditional_edges(
        "reference_resolver",
        route_after_reference,
        {
            "retriever": "retriever",
            "end": END
        }
    )

    # 검색 후 응답 생성
    workflow.add_edge("rdb_searcher", "search_response")
    workflow.add_edge("search_response", END)

    # RAG 후 상세 응답
    workflow.add_edge("retriever", "detail_response")
    workflow.add_edge("detail_response", END)

    # 일반/명확화 응답 후 종료
    workflow.add_edge("general_response", END)
    workflow.add_edge("clarification_response", END)

    return workflow.compile()


# -----------------------------------------------------------------------------
# 싱글톤 및 인터페이스
# -----------------------------------------------------------------------------
_chatbot = None

def get_chatbot():
    """챗봇 인스턴스 반환 (싱글톤)"""
    global _chatbot
    if _chatbot is None:
        _chatbot = create_chatbot_graph()
    return _chatbot


def chat(question: str, session_state: dict = None) -> dict:
    """
    챗봇 메인 인터페이스

    Args:
        question: 사용자 질문
        session_state: 세션 상태 (chat_history, prev_anncs, selected_annc)

    Returns:
        {
            "answer": str,
            "session_state": dict,
            "debug_info": dict (optional)
        }
    """
    if session_state is None:
        session_state = {}

    chatbot = get_chatbot()

    # 초기 상태 구성
    initial_state = {
        "question": question,
        "chat_history": session_state.get("chat_history", []),
        "prev_anncs": session_state.get("prev_anncs", []),
        "selected_annc": session_state.get("selected_annc"),
        "intent": "",
        "intent_data": {},
        "search_filters": {},
        "candidate_anncs": [],
        "retrieved_docs": [],
        "answer": "",
        "debug_info": {}
    }

    # 그래프 실행
    result = chatbot.invoke(initial_state)

    # 대화 기록 업데이트
    new_history = session_state.get("chat_history", []).copy()
    new_history.append({"role": "user", "content": question})
    new_history.append({"role": "assistant", "content": result.get("answer", "")})

    # 최대 기록 수 제한
    if len(new_history) > ChatbotConfig.MAX_HISTORY_TURNS * 2:
        new_history = new_history[-(ChatbotConfig.MAX_HISTORY_TURNS * 2):]

    # 새 세션 상태
    new_session_state = {
        "chat_history": new_history,
        "prev_anncs": result.get("prev_anncs", session_state.get("prev_anncs", [])),
        "selected_annc": result.get("selected_annc", session_state.get("selected_annc"))
    }

    return {
        "answer": result.get("answer", "죄송합니다. 오류가 발생했습니다."),
        "session_state": new_session_state,
        "debug_info": result.get("debug_info", {})
    }
