# 개발 전 확인 및 논의 사항 → 답변 문서

> **개발 문서(`20251210_dev_01.txt`) 분석 결과 및 추가 확인 필요 사항**

---

## ❓ 추가 확인이 필요한 사항

### 1. API 엔드포인트 URL

**질문**: 실제 API 서버의 베이스 URL은 무엇인가요?

- 현재 `zipfit_django/web/views.py`의 `ask_view`에서 `http://localhost:8000/chatbot/ask/` 사용
- 하지만 `api.yaml`에는 `/api/chat`로 정의되어 있음 → **이 방식으로 진행할 것, 이게 백엔드에서 개발되는 문서를 바탕으로 전달된 것이다.**
- **확인 필요**: 실제 API 서버 주소와 엔드포인트 경로

**제안**:
```python
# settings.py에 추가
API_BASE_URL = 'http://localhost:8000'  # 또는 실제 서버 주소
```

→ **이게 무엇인지 궁금하다, 실제 서버 주소?**

### 2. 사용자 ID 생성 로직

**질문**: 사용자 ID 생성 방식을 Django 세션으로 변경할 때도 동일하게 유지하나요?

**현재 (figma14)**:
- JavaScript에서 랜덤 생성: `매콤한 숫사슴`
- `sessionStorage`에 저장
- 새 세션마다 새로운 ID 생성

**Django 변환 시**:
```python
# views.py에서 생성
import random

def generate_user_id():
    adjectives = ['매콤한', '달콤한', ...]
    animals = ['숫사슴', '오로라', ...]
    return f"{random.choice(adjectives)} {random.choice(animals)}"

# 세션에 저장
if 'user_id' not in request.session:
    request.session['user_id'] = generate_user_id()
```

**확인 필요**: 이 방식으로 진행해도 될까요? → **이렇게 진행하면 리스트에 랜덤으로 선택하는 것이라서 다양성이 없어질 것 같은데 괜찮을까요?**

### 3. 세션 키 관리

**질문**: 채팅 세션 키(`session_key`)는 어떻게 생성/관리하나요?

**api.yaml 기준**:
- 채팅 요청 시 `session_key` 필수
- 채팅 히스토리 조회 시 `session_key` 사용

**제안**:
```python
import uuid

# 새 채팅 시작 시
if 'chat_session_key' not in request.session:
    request.session['chat_session_key'] = str(uuid.uuid4())
```

**확인 필요**: 이 방식이 맞나요? 아니면 다른 방식이 있나요?
→ **혹시 zf_django 폴더에 다른 팀원이 개발한 내용에 참고할 자료가 있지 않을까요? zf_django 이게 팀에서 개발한 github 를 내려받은 최신 데이터입니다. 다만, 저는 팀 폴더에 병합전 테스트 및 개발로 figma_django 폴더로 작업을 할 예정입니다.**
---

## 🔄 논의가 필요한 사항

### 1. 채팅 추천 질문 처리 방법

**현재 상황**:
- `chat.html`에 하드코딩된 4개 추천 질문 카드
- 클릭 시 Mock 응답 표시

**논의 포인트**:

#### 옵션 A: 하드코딩 유지 (추천) → **이 방식으로 진행해도 될 것 같습니다.**
- 추천 질문은 고정된 4개 유지
- 클릭 시 API 호출하여 실제 응답 받기
- **장점**: 간단하고 빠름
- **단점**: 추천 질문이 동적이지 않음

#### 옵션 B: API에서 추천 질문 받기
- API에서 추천 질문 리스트를 받아옴
- 동적으로 카드 생성
- **장점**: 유연함
- **단점**: API 엔드포인트 추가 필요

**제안**: **옵션 A 추천**
- 추천 질문은 프론트엔드에서 하드코딩
- 클릭 시 `/api/chat` 호출하여 실제 응답 받기

### 2. 채팅 응답 JSON 저장 및 표시 방법

**현재 요구사항**:
> "실제로 호출해서 받아온 데이터를 어딘가에 저장을 한 번 하고 그걸 보여주는 형태"

**논의 포인트**:

#### 옵션 A: 세션에 저장 (추천)
```python
# views.py
def chat_api_view(request):
    # API 호출
    response_data = call_chat_api(...)
    
    # 세션에 채팅 히스토리 저장
    chat_history = request.session.get('chat_history', [])
    chat_history.append({
        'user_message': user_message,
        'ai_response': response_data,
        'timestamp': datetime.now().isoformat()
    })
    request.session['chat_history'] = chat_history
    
    return JsonResponse(response_data)
```

**장점**:
- 간단하고 빠름
- DB 없이도 동작
- 사용자별로 자동 관리

**단점**:
- 세션 만료 시 데이터 손실
- 대용량 데이터 부적합

#### 옵션 B: 로컬 스토리지에 저장
```javascript
// JavaScript
fetch('/api/chat/', {...})
    .then(response => response.json())
    .then(data => {
        // 로컬 스토리지에 저장
        const chatHistory = JSON.parse(localStorage.getItem('chat_history') || '[]');
        chatHistory.push(data);
        localStorage.setItem('chat_history', JSON.stringify(chatHistory));
        
        // 화면에 표시
        displayMessage(data);
    });
```

**장점**:
- 브라우저를 닫아도 유지됨
- 서버 부하 없음

**단점**:
- 브라우저별로 다름
- 보안 이슈 가능

#### 옵션 C: 임시 JSON 파일 저장 (개발용)
```python
# 개발 중에만 사용
import json
from datetime import datetime

def save_response_for_dev(response_data):
    filename = f"lab/ohj/chat_responses/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
```

**장점**:
- 개발 중 응답 형식 확인 용이
- 디버깅 편리

**단점**:
- 프로덕션에서는 사용 불가
- 파일 관리 필요

**제안**: **옵션 A (세션 저장) + 옵션 C (개발용 파일 저장)** → **이 방식으로 진행하겠다, 대신 개발이 완료되면 추후에 정리해서 문서화해서 정리해야한다고 TODO 알려줘야함**
- 프로덕션: 세션에 저장
- 개발 중: 추가로 JSON 파일로도 저장하여 형식 확인

### 3. 채팅 응답 형식 렌더링

**현재 상황**:
- 채팅 예시 파일(`lab/ohj/chat_form/*.txt`) 확인 완료
- 복잡한 HTML 구조 (참고 문서, 공고 카드, 표 등)

**논의 포인트**:

#### API 응답 형식 가정

**가정 1: 마크다운 형식**
```json
{
    "status": "success",
    "data": {
        "ai_response": {
            "message": "신혼부부 특별공급에 대해 안내드립니다.\n\n✅ **기본 자격 요건**\n• 혼인 기간 7년 이내\n...",
            "message_type": "bot",
            "references": [
                {
                    "title": "LH_고양 삼송지구 청년 행복주택_공고문.pdf",
                    "page": 3,
                    "relevance": 0.95,
                    "excerpt": "신청자격: 만 19세 이상 39세 이하..."
                }
            ],
            "announcements": [
                {
                    "title": "고양 삼송지구 청년 행복주택",
                    "agency": "LH",
                    "type": "청년 행복주택",
                    "location": "경기도 고양시 덕양구 삼송동",
                    "recruitment_period": "2025.01.15 ~ 2025.01.25",
                    "deposit": "1,000만원",
                    "monthly_rent": "20만원",
                    "supply_count": 320,
                    "qualifications": ["만 19~39세", "무주택자", "소득 120% 이하"]
                }
            ]
        }
    }
}
```

**가정 2: HTML 형식**
```json
{
    "status": "success",
    "data": {
        "ai_response": {
            "message": "<div>신혼부부 특별공급에 대해 안내드립니다...</div>",
            "message_type": "bot",
            "format": "html"
        }
    }
}
```

**제안**: **가정 1 (구조화된 JSON) 추천** → **이 형식이 될 것으로 생각합니다.**
- 마크다운 텍스트 + 별도 데이터 구조
- 프론트엔드에서 렌더링 제어 가능
- 확장성 좋음

**확인 필요**: 실제 API 응답 형식이 어떻게 되나요?

### 4. 공고 비교 테이블 형식

**요구사항**:
> "2개의 공고에 대해서 비교해주는 테이블 형태로 깔끔하게 보여지면 좋겠다."

**논의 포인트**:

#### API 응답에 비교 요청 표시
```json
{
    "data": {
        "ai_response": {
            "message": "두 공고를 비교해드리겠습니다.",
            "message_type": "bot",
            "comparison": {
                "type": "table",
                "announcements": [
                    {
                        "id": 1,
                        "title": "고양 삼송지구 청년 행복주택",
                        ...
                    },
                    {
                        "id": 2,
                        "title": "일산 식사지구 행복주택",
                        ...
                    }
                ],
                "compare_fields": [
                    "location",
                    "recruitment_period",
                    "deposit",
                    "monthly_rent",
                    "supply_count"
                ]
            }
        }
    }
}
```

**제안**: 
- API 응답에 `comparison` 필드 포함
- 프론트엔드에서 테이블로 렌더링
- Bootstrap 테이블 컴포넌트 활용

**확인 필요**: API에서 비교 형식으로 응답을 주나요? 아니면 프론트엔드에서 처리하나요?
→ **API 에서 비교 형식으로 응답을 주는지는 파악을 못했지만, 프론트엔드에서 처리해도 가능할까요?**

### 5. 공고 요약 답변 형식

**요구사항**:
> "공고 요약에 대해서 문의시 답변 형식"

**논의 포인트**:

#### 옵션 A: 텍스트 요약
- 일반 채팅 메시지처럼 텍스트로 요약
- 간단하고 빠름

#### 옵션 B: 구조화된 카드 형식
- 공고 카드 형태로 표시 (현재 예시와 유사)
- 시각적으로 보기 좋음

**제안**: **옵션 B (카드 형식) 추천** → **이 방식으로 진행하겠습니다.**
- 현재 예시 파일의 형식이 좋아 보임
- 공고 정보를 한눈에 파악 가능

---

## 📋 개발 전 체크리스트

### 필수 확인 사항
- [ ] API 서버 베이스 URL 확인
- [ ] 실제 API 응답 형식 확인 (JSON 구조)
- [ ] 세션 키 생성 방식 확인
- [ ] 사용자 ID 생성 방식 확인

### 논의 완료 필요
- [ ] 채팅 추천 질문 처리 방법 결정
- [ ] 채팅 응답 저장 방식 결정 (세션 vs 로컬스토리지)
- [ ] 채팅 응답 렌더링 방식 결정 (마크다운 vs HTML)
- [ ] 공고 비교 테이블 형식 결정
- [ ] 공고 요약 형식 결정

### 기술적 결정
- [ ] 채팅 히스토리 저장 위치 (세션 vs DB)
- [ ] 에러 처리 방식
- [ ] 로딩 상태 표시 방식
- [ ] 반응형 디자인 유지 방법

---

## 🎯 제안하는 개발 순서

### Phase 1: 기본 구조 설정
1. `figma_django` 폴더 생성
2. Django 프로젝트 구조 복사 (`zipfit_django` 기준)
3. 5개 페이지 템플릿 생성 (기본 레이아웃만)

### Phase 2: 정적 페이지 구현
1. `landing.html` 변환 (데이터 연동 없음)
2. `user_info.html` 변환 (세션 저장만)
3. CSS/JS 파일 이동 및 연결

### Phase 3: API 연동 (Mock 데이터)
1. `main.html` 통계 API 연동 (Mock 응답)
2. `list.html` 공고 목록 API 연동 (Mock 응답)
3. `chat.html` 채팅 API 연동 (Mock 응답)

### Phase 4: 실제 API 연동
1. 실제 API 엔드포인트 연결
2. 응답 형식에 맞춰 렌더링 로직 구현
3. 에러 처리 및 로딩 상태 추가

### Phase 5: 고급 기능
1. 채팅 히스토리 표시
2. 공고 비교 테이블
3. 공고 요약 카드
4. 반응형 디자인 최종 점검

---

## 📝 다음 단계

1. **팀원과 논의**: 위의 논의 사항들에 대해 결정
2. **API 응답 형식 확인**: 실제 백엔드 API 응답 구조 확인
3. **개발 시작**: Phase 1부터 순차적으로 진행

---

**작성일**: 2025-12-10  
**작성자**: 개발팀

