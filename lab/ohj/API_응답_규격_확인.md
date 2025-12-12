# API 응답 규격 확인

## 1. GET /api/anncs

### 요청 파라미터
- `annc_title` (선택)
- `annc_status` (선택)
- `items_per_page` (필수, 기본값: 10)
- `current_page` (필수, 기본값: 1)

### 응답 형식
```json
{
  "message": "성공적으로 공고 목록을 조회했습니다.",
  "status": "success",
  "data": {
    "page_info": {
      "total_count": 100,
      "current_page": 1,
      "items_per_page": 10,
      "total_pages": 10
    },
    "items": [
      {
        "annc_id": 1,
        "annc_title": "공고 제목",
        "annc_url": "https://...",
        "created_at": "2025-12-12T00:00:00Z",  // ✅ created_at 사용
        "annc_status": "접수중",
        "annc_type": "임대",
        "annc_dtl_type": "영구임대주택",
        "annc_region": "서울",
        "annc_pblsh_dt": "2025-12-01",
        "annc_deadline_dt": "2025-12-20"
      }
    ]
  }
}
```

### 확인 사항 ✅
- ✅ `created_at` 필드 사용 (프론트엔드와 일치)
- ✅ 추가 필드 포함 (`annc_type`, `annc_dtl_type`, `annc_region`, `annc_pblsh_dt`, `annc_deadline_dt`)
- ✅ serializer 사용으로 일관된 형식 보장

---

## 2. POST /api/chat

### 요청 본문
```json
{
  "user_key": "anonymous",
  "session_key": "uuid-string",
  "user_message": "질문 내용"
}
```

### 응답 형식
```json
{
  "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
  "status": "success",
  "data": {
    "ai_response": {
      "id": 123,
      "session_id": "uuid-string",
      "sequence": 2,
      "message_type": "bot",
      "message": "AI 응답 내용"
    }
  }
}
```

### 확인 사항 ✅
- ✅ `session_key` 파라미터 지원 (프론트엔드와 일치)
- ✅ LangGraph 통합 완료
- ✅ `Chat`, `ChatMessage` 모델 사용

---

## 3. GET /api/chathistories

### 요청 파라미터
- `user_key` (필수)

### 응답 형식
```json
{
  "message": "성공적으로 채팅 히스토리 목록을 조회했습니다.",
  "status": "success",
  "data": [
    {
      "title": "채팅 제목",
      "session_key": "uuid-string"
    }
  ]
}
```

### 확인 사항 ⚠️
- ⚠️ 현재 더미 데이터 반환 (팀원 코드도 동일)
- 추후 DB 연동 필요

---

## 4. GET /api/chathistories/{session_key}

### 요청 파라미터
- `user_key` (필수)

### 응답 형식
```json
{
  "message": "성공적으로 특정 채팅 히스토리를 조회했습니다.",
  "status": "success",
  "data": {
    "title": "채팅 제목",
    "session_key": "uuid-string",
    "user_key": "anonymous",
    "chat_list": [
      {
        "id": 1,
        "sequence": 1,
        "message_type": "user",
        "message": "사용자 메시지"
      },
      {
        "id": 2,
        "sequence": 2,
        "message_type": "bot",
        "message": "봇 응답"
      }
    ]
  }
}
```

### 확인 사항 ⚠️
- ⚠️ 현재 더미 데이터 반환 (팀원 코드도 동일)
- 추후 DB 연동 필요

---

## 5. GET /api/annc_summary

### 응답 형식
```json
{
  "message": "성공적으로 공고 요약 정보를 조회했습니다.",
  "status": "success",
  "data": {
    "cnt_total": 100,
    "cnt_lease": 60,
    "cnt_sale": 30,
    "cnt_etc": 10
  }
}
```

### 확인 사항 ✅
- ✅ DB에서 실제 데이터 조회
- ✅ 팀원 코드와 동일한 구조

---

## 결론

### ✅ 호환성 확인 완료
1. **공고 목록 API**: `created_at` 필드 사용, 추가 필드 포함 ✅
2. **채팅 API**: `session_key` 파라미터 지원, LangGraph 통합 ✅
3. **응답 형식**: 프론트엔드와 일치 ✅

### ⚠️ 추후 작업 필요
1. **채팅 히스토리 API**: DB 연동 필요 (현재 더미 데이터)
2. **마이그레이션**: 실행 필요

