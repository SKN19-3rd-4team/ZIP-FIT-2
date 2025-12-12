# URL 라우팅 문제 해결

## 문제 상황

- `http://127.0.0.1:8000/` 접속 시 랜딩 페이지가 아닌 Swagger 페이지로 이동
- `http://127.0.0.1:8000/main` 접속 시 404 오류 발생

## 원인 분석

`config/urls.py`에서 URL 패턴 순서:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('web.urls', 'web'), namespace='web')),  # 웹 페이지
    path('', include('chatbot.urls')),  # API 엔드포인트
]
```

Django는 URL 패턴을 **순서대로** 매칭합니다. 따라서:
1. `''` (루트 경로)는 먼저 `web.urls`에 매칭됩니다.
2. `web.urls`에는 `path('', views.landing_view, name='landing')`가 있습니다.
3. 따라서 루트 경로는 `landing_view`에 매칭되어야 합니다.

## 해결 방법

현재 순서는 올바릅니다. 문제가 발생한다면:

1. **서버 재시작**: Django 서버를 완전히 재시작하세요.
2. **브라우저 캐시 삭제**: 브라우저 캐시를 삭제하고 다시 접속하세요.
3. **URL 확인**: 실제로 어떤 URL로 접속했는지 확인하세요.

## 확인 사항

- `web/urls.py`에 `path('', views.landing_view, name='landing')`가 있는지 확인
- `web/views.py`에 `landing_view` 함수가 있는지 확인
- `web/templates/web/landing.html` 파일이 존재하는지 확인

## 테스트 방법

1. 서버 재시작:
   ```bash
   python manage.py runserver 8000
   ```

2. 브라우저에서 접속:
   - `http://127.0.0.1:8000/` → 랜딩 페이지
   - `http://127.0.0.1:8000/main/` → 메인 페이지
   - `http://127.0.0.1:8000/api/docs/` → Swagger UI

