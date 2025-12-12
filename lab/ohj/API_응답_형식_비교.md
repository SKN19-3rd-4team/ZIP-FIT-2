# API 응답 형식 비교 및 확인

## 질문: 실제 API 호출 시 responseMessage 형식이 mockData.js와 동일한가?

### 현재 상황

1. **Mock 데이터 형식** (`mockData.js`):
   - 채팅 응답은 단순 문자열 또는 마크다운 형식의 텍스트로 반환됩니다.
   - `MockAPI.sendChatMessage`는 `{ status: 'success', data: { ai_response: '...' } }` 형식으로 반환합니다.

2. **실제 API 응답 형식** (`api응답형식.md` 참조):
   - 실제 API 응답 형식을 확인해야 합니다.

### 확인 필요 사항

1. **LLM 응답 형식**:
   - LLM이 반환하는 응답이 단순 텍스트인지, 마크다운 형식인지, JSON 형식인지 확인
   - 비교 테이블, 참조 링크 등 특수 형식이 포함되는지 확인

2. **프론트엔드 렌더링**:
   - 현재 `chat.html`의 `addMessage` 함수는 단순 텍스트를 HTML로 변환합니다 (`text.replace(/\n/g, '<br>')`).
   - 마크다운 형식이 포함된 경우 마크다운 파서가 필요할 수 있습니다.

### 권장 사항

1. **실제 API 테스트**:
   - `USE_MOCK_DATA = false`로 설정하고 실제 API를 호출하여 응답 형식 확인
   - 다양한 질문 유형(일반 질문, 비교 질문, 공고 참조 질문 등)에 대한 응답 형식 확인

2. **응답 형식 통일**:
   - 백엔드에서 일관된 형식으로 응답을 반환하도록 요청
   - 예: `{ status: 'success', data: { ai_response: '...', references: [...], comparison_table: {...} } }`

3. **프론트엔드 렌더링 개선**:
   - 마크다운 파서 추가 (예: `marked.js` 또는 `markdown-it`)
   - 비교 테이블 렌더링 로직 추가
   - 참조 링크 렌더링 로직 추가

### 다음 단계

1. 실제 API 응답 형식 확인 (`/api/chat` 엔드포인트 테스트)
2. Mock 데이터와 실제 응답 형식 비교
3. 필요시 프론트엔드 렌더링 로직 수정

