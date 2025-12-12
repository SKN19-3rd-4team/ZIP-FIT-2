# URL 라우팅 문제 최종 해결

## 문제 상황

- `http://127.0.0.1:8000/` 접속 시 랜딩 페이지가 아닌 Swagger 페이지로 이동
- `http://127.0.0.1:8000/main` 접속 시 404 오류 발생
- 404 오류 메시지에 `[name='chat_interface']`가 보임 (이는 `zf_django`의 패턴)

## 원인 분석

1. **`web.urls`가 제대로 로드되지 않음**: Django가 `web.urls`를 찾지 못하고 있습니다.
2. **`app_name` 누락**: `web/urls.py`에 `app_name`이 없어서 namespace가 제대로 작동하지 않을 수 있습니다.

## 해결 방법

### 1. `web/urls.py`에 `app_name` 추가

```python
# web/urls.py
from django.urls import path
from . import views

app_name = 'web'  # 추가

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('main/', views.main_view, name='main'),
    path('user-info/', views.user_info_view, name='user_info'),
    path('chat/', views.chat_view, name='chat'),
    path('list/', views.list_view, name='list'),
]
```

### 2. `config/urls.py` 수정

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    # 웹 페이지 (랜딩 페이지 포함) - 먼저 매칭되도록 먼저 배치
    path('', include('web.urls')),
    # API 엔드포인트 - web.urls 이후에 매칭
    path('', include('chatbot.urls')),
]
```

## 확인 사항

1. **서버 재시작**: Django 서버를 완전히 재시작하세요.
2. **브라우저 캐시 삭제**: 브라우저 캐시를 삭제하고 다시 접속하세요.
3. **템플릿 파일 확인**: `web/templates/web/landing.html` 파일이 존재하는지 확인하세요.

## 테스트 방법

1. 서버 재시작:
   ```bash
   python manage.py runserver 8000
   ```

2. 브라우저에서 접속:
   - `http://127.0.0.1:8000/` → 랜딩 페이지
   - `http://127.0.0.1:8000/main/` → 메인 페이지 (끝에 슬래시 포함)
   - `http://127.0.0.1:8000/api/docs/` → Swagger UI

## 참고사항

- Django는 URL 패턴을 **순서대로** 매칭합니다.
- `web.urls`가 먼저 오므로 루트 경로(`''`)는 `landing_view`에 매칭됩니다.
- `chatbot.urls`에는 루트 경로 매핑이 없으므로 API 엔드포인트만 매칭됩니다.

