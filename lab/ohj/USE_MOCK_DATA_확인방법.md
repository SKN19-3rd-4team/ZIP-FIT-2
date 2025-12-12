# USE_MOCK_DATA 확인 방법

> **목적**: 현재 Mock 데이터를 사용 중인지 실제 API를 사용 중인지 확인

---

## 🔍 확인 방법

### 방법 1: 브라우저 콘솔에서 확인

1. 웹 페이지 열기 (예: http://127.0.0.1:8000/main/)
2. **F12** 키를 눌러 개발자 도구 열기
3. **Console** 탭 선택
4. 다음 명령어 입력:

```javascript
// Mock 데이터 사용 여부 확인
console.log('USE_MOCK_DATA:', typeof USE_MOCK_DATA !== 'undefined' ? USE_MOCK_DATA : 'not defined');

// 또는 직접 확인
USE_MOCK_DATA
```

**결과**:
- `true` → Mock 데이터 사용 중
- `false` → 실제 API 사용 중
- `undefined` → 스크립트가 로드되지 않음

---

### 방법 2: 파일에서 직접 확인

**파일 위치**: `figma_django/web/static/js/mockData.js`

**라인 343**:
```javascript
const USE_MOCK_DATA = true; // false로 변경하면 실제 API 사용
```

- `true` → Mock 데이터 사용
- `false` → 실제 API 사용

---

### 방법 3: 네트워크 탭에서 확인

1. 웹 페이지 열기
2. **F12** 키를 눌러 개발자 도구 열기
3. **Network** 탭 선택
4. 페이지 새로고침 (F5)
5. API 호출 확인:
   - Mock 데이터 사용 시: `/api/...` 요청이 없거나 실패
   - 실제 API 사용 시: `/api/...` 요청이 성공적으로 전송됨

---

### 방법 4: 콘솔 로그 확인

Mock 데이터 사용 시 콘솔에 다음과 같은 로그가 나타납니다:

```
[MOCK API] GET /api/annc_summary
[MOCK API] GET /api/anncs?page=1
```

실제 API 사용 시:

```
[REAL API] Response from /api/annc_summary: {...}
```

---

## 📝 현재 상태

**기본값**: `USE_MOCK_DATA = true` (Mock 데이터 사용)

**변경 방법**:
1. `figma_django/web/static/js/mockData.js` 파일 열기
2. 라인 219의 `true`를 `false`로 변경
3. 브라우저 새로고침 (Ctrl + F5)

---

## ⚠️ 주의사항

- Mock 데이터를 사용하면 실제 PostgreSQL 데이터를 가져오지 않습니다
- 실제 API를 사용하려면 `zf_django` 서버가 실행 중이어야 합니다
- 실제 API 사용 시 CORS 오류가 발생할 수 있습니다 (같은 포트에서 실행 시 문제 없음)

---

**작성일**: 2025-12-10

