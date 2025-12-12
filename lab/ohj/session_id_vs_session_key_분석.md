# session_id vs session_key 변경 영향 분석

## 현재 상황

### 팀원 코드 확인 결과
- **모델 (`models.py`)**: `session_key` 필드 사용 ✅
- **뷰 (`views_chat.py`)**: `session_id` 파라미터 사용 (API 요청에서)
- **응답**: `session_id` 필드 사용

### 우리 코드 현재 상태
- **모델 (`models.py`)**: `session_key` 필드 사용 ✅
- **뷰 (`views_chat.py`)**: `session_key` 파라미터 사용 (호환성으로 `session_id`도 지원)
- **프론트엔드**: `session_key` 사용
- **응답**: `session_id` 필드 사용 (팀원 코드와 일치)

---

## 변경 시 필요한 작업

### ⚠️ 중요: 데이터베이스 모델 필드명은 변경하지 않음
- **모델 필드**: `session_key` 유지 (팀원 코드도 동일)
- **이유**: 데이터베이스 스키마 변경은 복잡하고 위험함

### 변경해야 할 부분

#### 1. API 요청 파라미터 (프론트엔드 → 백엔드)
**현재**: `session_key`
**변경 후**: `session_id`

**파일**:
- `zf_django/web/static/js/api.js` - `sendChatMessage` 함수
- `zf_django/web/templates/web/chat.html` - API 호출 부분
- `zf_django/web/templates/web/main.html` - API 호출 부분
- `zf_django/web/templates/web/list.html` - API 호출 부분

#### 2. API 응답 필드 (백엔드 → 프론트엔드)
**현재**: `session_id` (팀원 코드와 일치)
**변경**: 없음 (이미 `session_id` 사용 중)

**파일**:
- `zf_django/chatbot/views_chat.py` - 응답 생성 부분 ✅ (이미 `session_id` 사용)

#### 3. Serializer 필드명
**현재**: `session_key`
**변경 후**: `session_id`

**파일**:
- `zf_django/chatbot/serializers.py` - `ChatRequestSerializer`, `ChatShortSerializer`, `ChatHistoryDetailDataSerializer`

#### 4. 프론트엔드 내부 변수명
**현재**: `session_key` (sessionStorage 키, 변수명 등)
**변경 후**: `session_id`

**파일**:
- `zf_django/web/static/js/api.js` - 함수명, 변수명
- `zf_django/web/templates/web/chat.html` - JavaScript 변수명
- `zf_django/web/templates/web/main.html` - JavaScript 변수명
- `zf_django/web/templates/web/list.html` - JavaScript 변수명
- `zf_django/web/static/js/mockData.js` - Mock 데이터

#### 5. URL 파라미터
**현재**: `?session_key=...`
**변경 후**: `?session_id=...`

**파일**:
- `zf_django/web/templates/web/chat.html` - URL 파라미터 읽기
- `zf_django/web/templates/web/main.html` - URL 생성
- `zf_django/web/templates/web/list.html` - URL 생성

---

## 변경 시 문제점

### ✅ 문제 없음
1. **데이터베이스 모델**: 필드명 `session_key` 유지 (변경 불필요)
2. **백엔드 로직**: 모델 필드명과 API 파라미터명은 독립적

### ⚠️ 주의사항
1. **프론트엔드 변경 범위가 큼**: 여러 파일의 변수명, 함수명 변경 필요
2. **테스트 필요**: 모든 채팅 관련 기능 테스트 필요
3. **일관성**: 모든 곳에서 `session_id`로 통일 필요

---

## 권장 사항

### 옵션 1: session_id로 변경 (팀원 방향 따르기)
**장점**:
- 팀원 코드와 일관성 유지
- API 명세 통일

**단점**:
- 프론트엔드 대량 수정 필요
- 테스트 시간 필요

**작업량**: 중간 (약 10-15개 파일 수정)

### 옵션 2: 현재 상태 유지 (session_key 사용)
**장점**:
- 프론트엔드 변경 불필요
- 이미 작동 중인 코드 유지

**단점**:
- 팀원 코드와 파라미터명 불일치
- API 명세 불일치 가능

**작업량**: 없음

### 옵션 3: 하이브리드 (양쪽 모두 지원)
**현재 상태**: 이미 구현됨 ✅
```python
session_key = request.data.get('session_key') or request.data.get('session_id')
```

**장점**:
- 기존 코드와 호환
- 팀원 코드와도 호환
- 점진적 마이그레이션 가능

**단점**:
- 코드 복잡도 약간 증가

**작업량**: 없음 (이미 구현됨)

---

## 결론

### 추천: 옵션 3 (현재 상태 유지)
이유:
1. 이미 양쪽 모두 지원하도록 구현됨
2. 프론트엔드는 `session_key` 사용 (변경 불필요)
3. 팀원 코드는 `session_id` 사용 (호환됨)
4. 데이터베이스 모델은 `session_key` 유지 (양쪽 모두 동일)

### 만약 session_id로 변경한다면
1. 프론트엔드 모든 `session_key` → `session_id` 변경
2. Serializer 필드명 변경
3. 전체 테스트 필요
4. 작업 시간: 약 1-2시간

**결론**: 현재 하이브리드 방식이 가장 실용적입니다. 팀원과 협의하여 통일할 필요가 있다면 변경 가능하지만, 기술적으로는 문제 없습니다.

