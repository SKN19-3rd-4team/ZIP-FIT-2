# DB 연결 문제 해결 가이드

## 문제 상황

1. **main 페이지 통계 숫자가 DB에서 불러와지지 않음**
2. **공고 목록이 DB에서 불러와지지 않음** ("공고가 없습니다" 표시)
3. **8000/api/docs와 8001/api/docs 모두 접속됨** (이것은 정상입니다)

## 원인 분석

### 1. 모델 Import 문제

`figma_django`가 `zf_django.chatbot.models.AnncAll`을 import하려고 하는데, Python 경로 문제로 실패할 수 있습니다.

**해결 방법:**
- `figma_django/chatbot/views.py`에서 `sys.path`에 `zf_django` 경로를 추가
- 이미 수정 완료했습니다.

### 2. DB 연결 확인

두 서버는 **같은 PostgreSQL DB**를 사용합니다:
- `figma_django`: 프론트엔드 개발용 (8000 포트)
- `zf_django`: 백엔드 API용 (8001 포트)

**중요**: `zf_django` 서버가 실행되지 않아도 모델은 import 가능합니다. 하지만 최신 데이터를 확인하려면 두 서버 모두 실행하는 것이 좋습니다.

### 3. API 문서 접속 문제

**이것은 정상입니다:**
- `http://127.0.0.1:8000/api/docs/` → `figma_django`의 API 문서 (프론트엔드 개발용)
- `http://127.0.0.1:8001/api/docs/` → `zf_django`의 API 문서 (백엔드 API용)

두 서버가 각각 자체 API 문서를 제공하는 것이 정상입니다.

## 해결 방법

### 1. 서버 재시작

모델 import 경로를 수정했으므로 서버를 재시작하세요:

```bash
# 터미널 1: figma_django
cd figma_django
python manage.py runserver 8000

# 터미널 2: zf_django
cd zf_django
python manage.py runserver 8001
```

### 2. 디버깅 로그 확인

서버 터미널에서 다음 로그를 확인하세요:

**정상적인 경우:**
```
[DEBUG] Added zf_django to Python path: C:\SKN_19\ZIP-FIT-2\zf_django
[DEBUG] Successfully imported AnncAll: <class 'chatbot.models.AnncAll'>
[DEBUG] annc_list: USE_REAL_DB=True, AnncAll=<class 'chatbot.models.AnncAll'>
[DEBUG] annc_list: total_count=1234
[DEBUG] annc_list: items_data count=10
```

**문제가 있는 경우:**
```
[ERROR] Failed to import AnncAll: No module named 'chatbot'
[DEBUG] annc_list: Using dummy data (USE_REAL_DB=False, AnncAll=None)
```

### 3. DB 연결 확인

PostgreSQL이 실행 중인지 확인:
```bash
# Docker를 사용하는 경우
docker ps
```

### 4. 데이터 확인

PostgreSQL에 실제로 데이터가 있는지 확인:
```python
# Python 셸에서
python manage.py shell
>>> from chatbot.models import AnncAll
>>> AnncAll.objects.count()
```

## 확인 사항

1. **서버 터미널 로그 확인**
   - `[DEBUG]` 메시지가 보이는지 확인
   - `USE_REAL_DB=True`인지 확인
   - `total_count` 값이 0보다 큰지 확인

2. **브라우저 콘솔 확인**
   - 네트워크 탭에서 `/api/anncs` 요청 확인
   - 응답 데이터 확인

3. **API 직접 테스트**
   - `http://127.0.0.1:8000/api/anncs` 직접 접속
   - JSON 응답 확인

## 추가 문제 해결

만약 여전히 문제가 발생하면:

1. **Python 경로 문제**
   - `PYTHONPATH` 환경 변수에 `C:\SKN_19\ZIP-FIT-2` 추가
   - 또는 `sys.path` 수정 확인

2. **DB 설정 문제**
   - `figma_django/config/settings.py`의 DB 설정 확인
   - `zf_django/config/settings.py`의 DB 설정과 동일한지 확인

3. **모델 필드 문제**
   - `AnncAll` 모델의 필드명 확인
   - API 응답에서 사용하는 필드명과 일치하는지 확인

