# URL 라우팅 디버깅 가이드

## 현재 설정 확인

### 1. config/urls.py
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),  # 랜딩 페이지 먼저
    path('api/', include('chatbot.urls')),  # API 경로
]
```

### 2. web/urls.py
```python
app_name = 'web'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('main/', views.main_view, name='main'),
    path('user-info/', views.user_info_view, name='user_info'),
    path('chat/', views.chat_view, name='chat'),
    path('list/', views.list_view, name='list'),
]
```

### 3. chatbot/urls.py
```python
urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('test/', views.TestApiView.as_view(), name='test_api'),
    path('chat', views.chat_message, name='chat-message'),
    path('chathistories', views.chat_histories, name='chat-histories'),
    path('chathistories/<str:session_key>', views.chat_history_detail, name='chat-history-detail'),
    path('anncs', views.annc_list, name='annc-list'),
    path('annc_summary', views.annc_summary, name='annc-summary'),
    path('chatbot/ask/', views.ask_api, name='ask_api'),
]
```

## 예상되는 URL 매핑

- `/` → `landing_view` (랜딩 페이지)
- `/main/` → `main_view` (메인 페이지)
- `/api/docs/` → Swagger UI
- `/api/anncs` → 공고 목록 API
- `/api/annc_summary` → 공고 요약 API

## 디버깅 단계

### 1. 서버 재시작 확인
```bash
# 서버 완전히 종료 후 재시작
python manage.py runserver 8000
```

### 2. 브라우저 캐시 삭제
- Chrome: Ctrl + Shift + Delete
- 또는 시크릿 모드로 테스트

### 3. Django URL 확인
터미널에서 다음 명령어로 URL 패턴 확인:
```bash
python manage.py show_urls
```

### 4. 직접 테스트
브라우저 콘솔에서 확인:
- `http://127.0.0.1:8000/` 접속 시 어떤 페이지가 로드되는지
- 네트워크 탭에서 실제 요청 URL 확인

### 5. 서버 로그 확인
Django 서버 터미널에서 다음을 확인:
- 어떤 URL 패턴이 매칭되는지
- 404 오류가 발생하는지
- 어떤 view 함수가 호출되는지

## 문제 해결

### 문제: 랜딩 페이지가 Swagger로 리다이렉트됨
**원인**: `chatbot.urls`가 루트 경로에 매핑되어 있을 수 있음
**해결**: `config/urls.py`에서 `path('api/', include('chatbot.urls'))`로 변경

### 문제: 404 오류 발생
**원인**: 
1. 템플릿 파일이 없을 수 있음
2. `web` 앱이 `INSTALLED_APPS`에 없을 수 있음
3. URL 패턴이 잘못되었을 수 있음

**해결**:
1. `figma_django/web/templates/web/landing.html` 파일 존재 확인
2. `config/settings.py`의 `INSTALLED_APPS`에 `'web'` 확인
3. URL 패턴 재확인

### 문제: main 페이지 404 오류
**원인**: URL 패턴이 제대로 매칭되지 않음
**해결**: 
- `/main/` (끝에 슬래시 포함)로 접속
- 또는 `web/urls.py`에서 `path('main/', ...)` 확인

## 확인 사항 체크리스트

- [ ] Django 서버가 실행 중인가?
- [ ] `web` 앱이 `INSTALLED_APPS`에 있는가?
- [ ] `web/templates/web/landing.html` 파일이 존재하는가?
- [ ] `web/views.py`에 `landing_view` 함수가 있는가?
- [ ] `web/urls.py`에 `path('', views.landing_view, name='landing')`가 있는가?
- [ ] `config/urls.py`에 `path('', include('web.urls'))`가 있는가?
- [ ] 브라우저 캐시를 삭제했는가?
- [ ] 서버를 재시작했는가?

