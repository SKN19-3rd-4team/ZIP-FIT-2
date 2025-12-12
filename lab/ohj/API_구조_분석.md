# API 구조 분석 및 개발 방향

> **127.0.0.1:8000/api/docs 기반 실제 API 구조 파악**

---

## ✅ 확인 완료 사항

1. **API 문서 접속**: `http://127.0.0.1:8000/api/docs` 정상 작동
2. **Docker + PostgreSQL**: 연결 완료
3. **마이그레이션**: 완료
4. **drf_spectacular**: 설치 완료 (requirements.txt 업데이트 필요)
5. **실제 데이터**: 크롤링 데이터 4-5개 PostgreSQL에 저장됨

---

## 📋 API 엔드포인트 구조 분석

### 1. POST `/api/chat` - 채팅 메시지 전송 및 AI 응답

**요청 형식**:
```json
{
    "user_key": "매콤한 숫사슴",
    "session_key": "8a7e0d3c-9b1f-4d2a-8c5e-6f4b3a2d1e0f",
    "user_message": "수원 신혼부부에게 맞는 공고 찾아줄 수 있어?"
}
```

**응답 형식** (BaseResponse 구조):
```json
{
    "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
    "status": "success",
    "data": {
        "ai_response": {
            "id": 1,
            "sequence": 1,
            "message_type": "bot",
            "message": "AI 응답 내용...",
            "session_id": "8a7e0d3c-9b1f-4d2a-8c5e-6f4b3a2d1e0f"
        }
    }
}
```

**중요 사항**:
- `ai_response.message`에 실제 AI 응답 텍스트가 들어옴
- 현재는 단순 텍스트만 반환하는 것으로 보임
- 향후 구조화된 데이터(참고 문서, 공고 카드 등) 추가 예정일 수 있음

---

### 2. GET `/api/chathistories?user_key={user_key}` - 채팅 히스토리 목록

**요청**: Query 파라미터 `user_key`

**응답 형식**:
```json
{
    "message": "성공적으로 채팅 히스토리 목록을 조회했습니다.",
    "status": "success",
    "data": [
        {
            "title": "수원 신혼부부 적합한 공고 알려줘",
            "session_key": "8a7e0d3c-9b1f-4d2a-8c5e-6f4b3a2d1e0f"
        },
        {
            "title": "강남 임대 아파트",
            "session_key": "9b2e1d4c-0c2g-5e3b-9d6f-7f4c4b3e2f1g"
        }
    ]
}
```

**사용 목적**:
- `main.html`의 채팅 히스토리 목록 표시
- 각 히스토리 클릭 시 상세 조회

---

### 3. GET `/api/chathistories/{session_key}?user_key={user_key}` - 특정 히스토리 상세

**요청**: Path 파라미터 `session_key`, Query 파라미터 `user_key`

**응답 형식**:
```json
{
    "message": "성공적으로 특정 채팅 히스토리를 조회했습니다.",
    "status": "success",
    "data": {
        "title": "수원 신혼부부 추천 분양",
        "session_key": "8a7e0d3c-9b1f-4d2a-8c5e-6f4b3a2d1e0f",
        "user_key": "매콤한 숫사슴",
        "chat_list": [
            {
                "id": 1,
                "sequence": 1,
                "message_type": "user",
                "message": "수원 신혼부부에게 맞는 공고 찾아줄 수 있어?"
            },
            {
                "id": 2,
                "sequence": 2,
                "message_type": "bot",
                "message": "AI 응답 내용..."
            }
        ]
    }
}
```

**사용 목적**:
- 채팅 페이지에서 기존 대화 불러오기
- `chat_list` 배열을 순서대로 렌더링

---

### 4. GET `/api/anncs` - 공고 목록 조회

**요청 파라미터**:
- `annc_title` (선택): 공고 제목 검색
- `annc_status` (필수): "전체", "공고중", "접수중", "접수마감"
- `annc_type` (필수): "전체", "임대", "분양"
- `items_per_page` (필수): 페이지당 항목 수 (기본값: 10)
- `current_page` (필수): 현재 페이지 번호 (기본값: 1)

**응답 형식**:
```json
{
    "message": "성공적으로 공고 목록을 조회했습니다.",
    "status": "success",
    "data": {
        "page_info": {
            "total_count": 35,
            "current_page": 1,
            "items_per_page": 10,
            "total_pages": 4
        },
        "items": [
            {
                "annc_id": 1,
                "annc_title": "2025년 상반기 신입사원 공개 채용",
                "annc_url": "https://example.com/announcements/annc_001",
                "created_dttm": "2025-01-20T10:00:00Z",
                "annc_status": "공고중"
            }
        ]
    }
}
```

**사용 목적**:
- `list.html`의 공고 목록 표시
- 페이지네이션 처리

---

### 5. GET `/api/annc_summary` - 공고 요약 정보

**요청**: 파라미터 없음

**응답 형식**:
```json
{
    "message": "성공적으로 공고 요약 정보를 조회했습니다.",
    "status": "success",
    "data": {
        "cnt_total": 1304,
        "cnt_lease": 450,
        "cnt_sale": 34,
        "cnt_etc": 4
    }
}
```

**사용 목적**:
- `main.html`의 통계 숫자 표시
- "등록된 공고", "이번 주 신규" 등

---

## 🔍 확인 필요 사항

### 1. user_key 생성 API

**질문**: `/api/docs`에서 user_key 생성 API가 있는가?

**현재 상태**:
- API 문서에는 user_key 생성 API 없음
- 프론트엔드에서 생성하는 방식으로 구현됨

**확인 방법**:
1. `http://127.0.0.1:8000/api/docs` 접속
2. user_key 관련 엔드포인트 확인
3. 없다면 프론트엔드 생성 방식 유지

### 2. session_key 생성 API

**질문**: `/api/docs`에서 session_key 생성 API가 있는가?

**현재 상태**:
- API 문서에는 session_key 생성 API 없음
- 프론트엔드에서 UUID 생성하는 방식으로 구현됨

**확인 방법**:
1. `http://127.0.0.1:8000/api/docs` 접속
2. session_key 관련 엔드포인트 확인
3. 없다면 프론트엔드 UUID 생성 방식 유지

### 3. 실제 API 응답 형식 확인

**중요**: API 문서의 스키마와 실제 응답이 다를 수 있음

**확인 방법**:
1. `http://127.0.0.1:8000/api/docs`에서 "Try it out" 기능 사용
2. 실제 API 호출하여 응답 형식 확인
3. 특히 `/api/chat` 응답의 `ai_response.message` 형식 확인

---

## 🎯 개발 방향 결정

### 옵션 A: API 문서 기반 개발 (현재 방식)

**장점**:
- API 문서를 기준으로 개발
- 일관된 구조 유지

**단점**:
- 실제 응답과 다를 수 있음
- 나중에 수정 필요할 수 있음

### 옵션 B: 실제 API 테스트 후 개발 (권장)

**장점**:
- 실제 응답 형식 확인
- 한 번에 올바르게 구현 가능
- 불필요한 수정 최소화

**단계**:
1. `/api/docs`에서 실제 API 호출 테스트
2. 응답 형식 확인 및 문서화
3. 그에 맞춰 프론트엔드 개발

---

## 📝 다음 단계 (우선순위)

### 1. 즉시 확인 필요 (최우선)

- [ ] `/api/docs`에서 실제 API 호출 테스트
  - `/api/annc_summary` 호출 → 응답 형식 확인
  - `/api/anncs` 호출 → 응답 형식 확인
  - `/api/chat` 호출 → 응답 형식 확인 (가능하다면)
  - `/api/chathistories` 호출 → 응답 형식 확인

### 2. requirements.txt 업데이트

- [x] `drf-spectacular==0.27.2` 추가 완료

### 3. 개발 진행

- [ ] 실제 API 응답 형식 확인 후
- [ ] 프론트엔드 JavaScript 수정
- [ ] 각 페이지별 API 연동

---

## 💡 제안

**현재 상황**: API 문서는 있지만 실제 응답 형식을 확인하지 않았음

**권장 사항**:
1. **먼저 실제 API를 테스트**하여 응답 형식을 확인
2. **응답 형식을 문서화**하여 개발 가이드 작성
3. **그에 맞춰 프론트엔드 개발** 진행

**이유**:
- API 문서와 실제 응답이 다를 수 있음
- 한 번에 올바르게 구현하는 것이 효율적
- 나중에 수정하는 것보다 초기에 확인하는 것이 좋음

---

**작성일**: 2025-01-20  
**상태**: API 구조 분석 완료, 실제 응답 확인 필요 ⚠️

