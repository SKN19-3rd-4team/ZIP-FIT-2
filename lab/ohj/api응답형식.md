# API 실제 응답 형식

> **`/api/docs`에서 실제 API 호출 테스트 후 응답 형식 기록**

---

## 📋 테스트 완료 체크리스트

- [v] `GET /api/annc_summary` - 공고 요약 정보
- [v] `GET /api/anncs` - 공고 목록 조회
- [v] `GET /api/chathistories` - 채팅 히스토리 목록
- [v] `POST /api/chat` - 채팅 메시지 전송

---

## 1. GET /api/annc_summary

**요청**: 파라미터 없음

**실제 응답 형식** (테스트 후 기록):
```json
{
  "message": "성공적으로 공고 요약 정보를 조회했습니다.",
  "status": "success",
  "data": {
    "cnt_total": 2,
    "cnt_lease": 2,
    "cnt_sale": 0,
    "cnt_etc": 0
  }
}
```

**테스트 결과**:
- [ ] 테스트 완료
- [ ] 응답 형식 확인
- [ ] 예상과 다른 점 기록

---

## 2. GET /api/anncs

**요청 파라미터**:
- `annc_status`: "전체" | "공고중" | "접수중" | "접수마감"
- `annc_type`: "전체" | "임대" | "분양"
- `items_per_page`: 숫자 (기본값: 10)
- `current_page`: 숫자 (기본값: 1)
- `annc_title`: 문자열 (선택사항)

**실제 응답 형식** (테스트 후 기록):
```json
{
  "message": "성공적으로 공고 목록을 조회했습니다.",
  "status": "success",
  "data": {
    "page_info": {
      "total_count": 2,
      "current_page": 1,
      "items_per_page": 10,
      "total_pages": 1
    },
    "items": [
      {
        "annc_id": 3,
        "annc_title": "[정정공고]양주회천 A25BL 영구임대주택 입주자 모집공고",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300019125&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=09",
        "created_dttm": "2025-12-10T20:02:23.459855Z",
        "annc_status": "공고중"
      },
      {
        "annc_id": 1,
        "annc_title": "양주시, 동두천시 행복주택 상시모집[선착순동호지정, 입주자격완화, 선계약후검증]",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018161&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=10",
        "created_dttm": "2025-12-10T20:00:29.135119Z",
        "annc_status": "공고중"
      }
    ]
  }
}
```

**테스트 결과**:
- [ ] 테스트 완료
- [ ] 응답 형식 확인
- [ ] 페이지네이션 동작 확인
- [ ] 필터링 동작 확인

---

## 3. GET /api/chathistories

**요청 파라미터**:
- `user_key`: 101

**실제 응답 형식** (테스트 후 기록):
```json
{
  "message": "성공적으로 채팅 히스토리 목록을 조회했습니다.",
  "status": "success",
  "data": [
    {
      "title": "수원 신혼부부 추천",
      "session_key": "session-001"
    },
    {
      "title": "강남 임대 아파트",
      "session_key": "session-002"
    }
  ]
}
```

**테스트 결과**:
- [ ] 테스트 완료
- [ ] 응답 형식 확인
- [ ] 빈 배열인지 확인 (데이터 없을 때)

---

## 4. GET /api/chathistories/{session_key}

**요청 파라미터**:
- `session_key`: session-001
- `user_key`: 101

**실제 응답 형식** (테스트 후 기록):
```json
{
  "message": "성공적으로 특정 채팅 히스토리를 조회했습니다.",
  "status": "success",
  "data": {
    "title": "수원 신혼부부 추천 분양",
    "session_key": "session-001",
    "user_key": "101",
    "chat_list": [
      {
        "id": 1,
        "sequence": 1,
        "message_type": "user",
        "message": "추천해줘"
      },
      {
        "id": 2,
        "sequence": 2,
        "message_type": "bot",
        "message": "여기 추천 목록입니다."
      }
    ]
  }
}
```

**테스트 결과**:
- [ ] 테스트 완료
- [ ] 응답 형식 확인
- [ ] 존재하지 않는 session_key 처리 확인

---

## 5. POST /api/chat

**요청 본문**:
```json
{
  "user_key": "string",
  "session_key": "string",
  "user_message": "string"
}
```

**실제 응답 형식** (테스트 후 기록):
```json
{
  "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
  "status": "success",
  "data": {
    "ai_response": {
      "id": 101,
      "session_id": "8a7e0d3c-9b1f-4d2a-8c5e-6f4b3a2d1e0f",
      "sequence": 2,
      "message_type": "bot",
      "message": "AI가 답변합니다: 'string'에 대한 정보입니다."
    }
  }
}
```

**테스트 결과**:
- [ ] 테스트 완료
- [ ] 응답 형식 확인
- [ ] AI 응답 내용 확인
- [ ] 에러 처리 확인

---

## 📝 추가 확인 사항

## 6. POST /api/schema/

OpenApi3 schema for this API. Format can be selected via content negotiation.

YAML: application/vnd.oai.openapi
JSON: application/vnd.oai.openapi+json

Curl

curl -X 'GET' \
  'http://127.0.0.1:8000/api/schema/' \
  -H 'accept: application/vnd.oai.openapi'

200	
Response body
Unrecognized response type; displaying content as text.

openapi: 3.0.3
info:
  title: ''
  version: 0.0.0
paths:
  /api/annc_summary:
    get:
      operationId: getAnnouncementSummary
      summary: 홈 - 공고 요약 데이터 요약
      tags:
      - 공고 요약
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnncSummaryResponse'
          description: ''
  /api/anncs:
    get:
      operationId: getAnnouncementList
      summary: 공고 목록 조회
      parameters:
      - in: query
        name: annc_status
        schema:
          type: string
          enum:
          - 마감
          - 예정
          - 진행중
      - in: query
        name: annc_title
        schema:
          type: string
      - in: query
        name: annc_type
        schema:
          type: string
      - in: query
        name: current_page
        schema:
          type: integer
          default: 1
        required: true
      - in: query
        name: items_per_page
        schema:
          type: integer
          default: 10
        required: true
      tags:
      - 공고
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AnnouncementListResponse'
          description: ''
  /api/chat:
    post:
      operationId: postChatMessage
      summary: 사용자 - 신규 채팅 메시지 등록 및 AI 응답 받기
      tags:
      - 채팅
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
          application/x-www-form-urlencoded:
            schema:
              $ref: '#/components/schemas/ChatRequest'
          multipart/form-data:
            schema:
              $ref: '#/components/schemas/ChatRequest'
        required: true
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'
          description: ''
  /api/chathistories:
    get:
      operationId: getChatHistories
      summary: 사용자 - 채팅 히스토리 목록 조회
      parameters:
      - in: query
        name: user_key
        schema:
          type: string
        description: 사용자 키
        required: true
      tags:
      - 채팅 히스토리
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatHistoriesResponse'
          description: ''
  /api/chathistories/{session_key}:
    get:
      operationId: getChatHistoryDetail
      summary: 사용자 - 특정 히스토리 조회
      parameters:
      - in: path
        name: session_key
        schema:
          type: string
        required: true
      - in: query
        name: user_key
        schema:
          type: string
        description: 사용자 키
        required: true
      tags:
      - 채팅 히스토리
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatHistoryDetailResponse'
          description: ''
  /api/schema/:
    get:
      operationId: schema_retrieve
      description: |-
        OpenApi3 schema for this API. Format can be selected via content negotiation.

        - YAML: application/vnd.oai.openapi
        - JSON: application/vnd.oai.openapi+json
      parameters:
      - in: query
        name: format
        schema:
          type: string
          enum:
          - json
          - yaml
      - in: query
        name: lang
        schema:
          type: string
          enum:
          - af
          - ar
          - ar-dz
          - ast
          - az
          - be
          - bg
          - bn
          - br
          - bs
          - ca
          - ckb
          - cs
          - cy
          - da
          - de
          - dsb
          - el
          - en
          - en-au
          - en-gb
          - eo
          - es
          - es-ar
          - es-co
          - es-mx
          - es-ni
          - es-ve
          - et
          - eu
          - fa
          - fi
          - fr
          - fy
          - ga
          - gd
          - gl
          - he
          - hi
          - hr
          - hsb
          - ht
          - hu
          - hy
          - ia
          - id
          - ig
          - io
          - is
          - it
          - ja
          - ka
          - kab
          - kk
          - km
          - kn
          - ko
          - ky
          - lb
          - lt
          - lv
          - mk
          - ml
          - mn
          - mr
          - ms
          - my
          - nb
          - ne
          - nl
          - nn
          - os
          - pa
          - pl
          - pt
          - pt-br
          - ro
          - ru
          - sk
          - sl
          - sq
          - sr
          - sr-latn
          - sv
          - sw
          - ta
          - te
          - tg
          - th
          - tk
          - tr
          - tt
          - udm
          - ug
          - uk
          - ur
          - uz
          - vi
          - zh-hans
          - zh-hant
      tags:
      - schema
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          content:
            application/vnd.oai.openapi:
              schema:
                type: object
                additionalProperties: {}
            application/yaml:
              schema:
                type: object
                additionalProperties: {}
            application/vnd.oai.openapi+json:
              schema:
                type: object
                additionalProperties: {}
            application/json:
              schema:
                type: object
                additionalProperties: {}
          description: ''
  /api/test/:
    get:
      operationId: test_retrieve
      description: 테스트용 REST API View. GET 요청 시 Hello World 메시지를 반환합니다.
      tags:
      - test
      security:
      - cookieAuth: []
      - basicAuth: []
      - {}
      responses:
        '200':
          description: No response body
components:
  schemas:
    AnncSummaryData:
      type: object
      properties:
        cnt_total:
          type: integer
        cnt_lease:
          type: integer
        cnt_sale:
          type: integer
        cnt_etc:
          type: integer
      required:
      - cnt_etc
      - cnt_lease
      - cnt_sale
      - cnt_total
    AnncSummaryResponse:
      type: object
      properties:
        message:
          type: string
          default: 요청을 성공적으로 처리했습니다.
        status:
          type: string
          default: success
        data:
          $ref: '#/components/schemas/AnncSummaryData'
      required:
      - data
    AnnouncementData:
      type: object
      properties:
        page_info:
          $ref: '#/components/schemas/PageInfo'
        items:
          type: array
          items:
            $ref: '#/components/schemas/AnnouncementItem'
      required:
      - items
      - page_info
    AnnouncementItem:
      type: object
      properties:
        annc_id:
          type: integer
          readOnly: true
          title: 공고 ID
        annc_title:
          type: string
          title: 공고 제목
          maxLength: 200
        annc_url:
          type: string
          format: uri
          title: 공고 URL
          maxLength: 2000
        created_dttm:
          type: string
          format: date-time
          readOnly: true
          title: 공고 생성 일자
        annc_status:
          type: string
          title: 공고 상태
          maxLength: 20
      required:
      - annc_id
      - annc_status
      - annc_title
      - annc_url
      - created_dttm
    AnnouncementListResponse:
      type: object
      properties:
        message:
          type: string
          default: 요청을 성공적으로 처리했습니다.
        status:
          type: string
          default: success
        data:
          $ref: '#/components/schemas/AnnouncementData'
      required:
      - data
    ChatHistoriesResponse:
      type: object
      properties:
        message:
          type: string
          default: 요청을 성공적으로 처리했습니다.
        status:
          type: string
          default: success
        data:
          type: array
          items:
            $ref: '#/components/schemas/ChatShort'
      required:
      - data
    ChatHistoryDetailData:
      type: object
      properties:
        title:
          type: string
        session_key:
          type: string
        user_key:
          type: string
        chat_list:
          type: array
          items:
            $ref: '#/components/schemas/ChatMessage'
      required:
      - chat_list
      - session_key
      - title
      - user_key
    ChatHistoryDetailResponse:
      type: object
      properties:
        message:
          type: string
          default: 요청을 성공적으로 처리했습니다.
        status:
          type: string
          default: success
        data:
          $ref: '#/components/schemas/ChatHistoryDetailData'
      required:
      - data
    ChatMessage:
      type: object
      properties:
        id:
          type: integer
        sequence:
          type: integer
        message_type:
          type: string
        message:
          type: string
      required:
      - id
      - message
      - message_type
      - sequence
    ChatRequest:
      type: object
      properties:
        user_key:
          type: string
        session_key:
          type: string
        user_message:
          type: string
      required:
      - session_key
      - user_key
      - user_message
    ChatResponse:
      type: object
      properties:
        message:
          type: string
          default: 요청을 성공적으로 처리했습니다.
        status:
          type: string
          default: success
        data:
          $ref: '#/components/schemas/ChatResponseData'
      required:
      - data
    ChatResponseData:
      type: object
      properties:
        ai_response:
          $ref: '#/components/schemas/ChatMessage'
      required:
      - ai_response
    ChatShort:
      type: object
      properties:
        title:
          type: string
        session_key:
          type: string
      required:
      - session_key
      - title
    PageInfo:
      type: object
      properties:
        total_count:
          type: integer
        current_page:
          type: integer
        items_per_page:
          type: integer
        total_pages:
          type: integer
      required:
      - current_page
      - items_per_page
      - total_count
      - total_pages
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
    cookieAuth:
      type: apiKey
      in: cookie
      name: sessionid


### 1. 에러 응답 형식
- [ ] 400 에러 응답 형식 확인
- [ ] 500 에러 응답 형식 확인

### 2. 빈 데이터 처리
- [ ] 데이터가 없을 때 응답 형식 확인
- [ ] 빈 배열 vs null 확인

### 3. 날짜 형식
- [ ] `created_dttm` 형식 확인 (ISO 8601? 한국 시간?)
- [ ] 프론트엔드에서 포맷팅 필요 여부 확인

### 4. URL 형식
- [ ] `annc_url` 형식 확인
- [ ] 상대 경로 vs 절대 경로 확인

---

## 💡 프론트엔드 개발 시 참고

### 1. 데이터 구조
- 실제 응답 형식에 맞춰 JavaScript 코드 작성
- 예상과 다른 경우 수정 필요

### 2. 에러 처리
- 에러 응답 형식에 맞춰 에러 처리 구현
- 사용자에게 적절한 메시지 표시

### 3. 날짜 포맷팅
- `created_dttm` 형식에 맞춰 포맷팅 함수 작성
- 한국 시간으로 변환 필요 여부 확인

---

**작성일**: 2025-01-20  
**상태**: API 테스트 후 실제 응답 형식 기록 예정 ⚠️

