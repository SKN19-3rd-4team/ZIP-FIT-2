# API 호출 문제 해결 방안

## 문제 상황

`USE_MOCK_DATA = false`로 설정 시 다음과 같은 404 오류가 발생합니다:

```
GET http://127.0.0.1:8001/api/annc_summary?user_key=... 404 (Not Found)
GET http://127.0.0.1:8001/api/chathistories?user_key=... 404 (Not Found)
GET http://127.0.0.1:8001/api/anncs?... 404 (Not Found)
```

## 원인 분석

1. **포트 불일치**: 브라우저가 `http://127.0.0.1:8001`에서 페이지를 열고 있지만, Django 서버는 `http://127.0.0.1:8000`에서 실행되고 있을 가능성이 높습니다.

2. **상대 경로 사용**: 현재 코드는 상대 경로(`/api/...`)를 사용하므로, 브라우저가 현재 페이지의 호스트와 포트를 사용합니다.

## 해결 방안

### 방안 1: Django 서버를 올바른 포트에서 실행 (권장)

Django 서버를 `8001` 포트에서 실행하거나, 브라우저에서 `8000` 포트로 접속:

```bash
# Django 서버를 8001 포트에서 실행
python manage.py runserver 8001

# 또는 브라우저에서 8000 포트로 접속
http://127.0.0.1:8000
```

### 방안 2: API_BASE_URL 설정 추가 (선택사항)

만약 프론트엔드와 백엔드가 다른 포트에서 실행되어야 한다면, `api.js`에 `API_BASE_URL` 설정을 추가할 수 있습니다:

```javascript
// api.js 상단에 추가
const API_BASE_URL = window.location.origin; // 현재 페이지의 origin 사용
// 또는
// const API_BASE_URL = 'http://127.0.0.1:8000'; // 고정 URL 사용

// 각 fetch 호출에서 사용
const response = await fetch(`${API_BASE_URL}/api/annc_summary`);
```

## 확인 사항

1. Django 서버가 실행 중인지 확인:
   ```bash
   python manage.py runserver
   ```

2. Django 서버가 실행 중인 포트 확인:
   - 터미널에서 `Starting development server at http://127.0.0.1:8000/` 메시지 확인

3. 브라우저에서 접속한 URL 확인:
   - 주소창에서 현재 URL 확인 (`http://127.0.0.1:8000` 또는 `http://127.0.0.1:8001`)

4. API 엔드포인트가 올바르게 등록되어 있는지 확인:
   - `http://127.0.0.1:8000/api/docs` 접속하여 API 문서 확인

## 현재 코드 상태

현재 `api.js`와 `mockData.js`는 모두 상대 경로(`/api/...`)를 사용하므로, 브라우저가 현재 페이지의 호스트와 포트를 사용합니다.

**권장 사항**: Django 서버를 `8000` 포트에서 실행하고, 브라우저에서도 `http://127.0.0.1:8000`으로 접속하는 것이 가장 간단한 해결 방법입니다.

