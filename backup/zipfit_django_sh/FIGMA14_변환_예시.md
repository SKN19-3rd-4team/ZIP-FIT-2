# figma14 → Django 변환 실제 예시

> **figma14/main.html의 Mock Data를 Django로 변환하는 실제 예시**

---

## 📋 목표

figma14의 `main.html`에 있는 하드코딩된 통계 데이터를 Django API로 변환합니다.

---

## Before: figma14/main.html (현재 상태)

### 하드코딩된 통계 데이터

```html
<!-- main.html의 통계 그리드 부분 -->
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">1,247</div>
        <div class="stat-label">등록된 공고</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">42</div>
        <div class="stat-label">이번 주 신규</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">15,823</div>
        <div class="stat-label">누적 상담</div>
    </div>
    <div class="stat-card">
        <div class="stat-number">3,492</div>
        <div class="stat-label">활성 사용자</div>
    </div>
</div>
```

**문제점**:
- 숫자가 하드코딩되어 있음
- 실제 데이터와 연동 불가능
- 동적으로 업데이트 불가능

---

## After: Django 변환 (단계별)

### Step 1: Django views.py에 API 함수 추가

**파일**: `web/views.py`

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ... 기존 코드 ...

@csrf_exempt
def api_statistics(request):
    """
    홈 페이지 통계 API
    GET /api/statistics/
    
    응답 형식:
    {
        "status": "success",
        "data": {
            "total_announcements": 1247,
            "new_this_week": 42,
            "total_consultations": 15823,
            "active_users": 3492
        }
    }
    """
    # TODO: 나중에 DB에서 실제 데이터 가져오기
    # 예시:
    # from .models import Announcement
    # total_announcements = Announcement.objects.count()
    
    stats = {
        "total_announcements": 1247,
        "new_this_week": 42,
        "total_consultations": 15823,
        "active_users": 3492,
    }
    
    return JsonResponse({
        "status": "success",
        "message": "요청을 성공적으로 처리했습니다.",
        "data": stats,
    })
```

### Step 2: URL 라우팅 추가

**파일**: `web/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('web/', views.chat_view, name='chat'),
    path('profile/', views.profile_view, name='profile'),
    path('announcements/', views.announcements_view, name='announcements'),
    
    # API 엔드포인트 추가
    path('api/statistics/', views.api_statistics, name='api_statistics'),
]
```

### Step 3: HTML 템플릿 변환

**파일**: `web/templates/web/home.html`

#### Before (figma14 스타일)

```html
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-number">1,247</div>
        <div class="stat-label">등록된 공고</div>
    </div>
    <!-- ... -->
</div>
```

#### After (Django 템플릿)

```django
{% extends "base.html" %}
{% load static %}

{% block title %}홈 - 집핏 ZIPFIT{% endblock %}

{% block content %}
<!-- 통계 그리드 -->
<div class="stats-grid" id="statisticsGrid">
    <div class="stat-card">
        <div class="stat-number" id="total-announcements">-</div>
        <div class="stat-label">등록된 공고</div>
    </div>
    <div class="stat-card">
        <div class="stat-number" id="new-this-week">-</div>
        <div class="stat-label">이번 주 신규</div>
    </div>
    <div class="stat-card">
        <div class="stat-number" id="total-consultations">-</div>
        <div class="stat-label">누적 상담</div>
    </div>
    <div class="stat-card">
        <div class="stat-number" id="active-users">-</div>
        <div class="stat-label">활성 사용자</div>
    </div>
</div>

<!-- 로딩 스피너 (선택사항) -->
<div id="loadingSpinner" style="display: none;">
    데이터를 불러오는 중...
</div>
{% endblock %}

{% block extra_js %}
<script>
    // 페이지 로드 시 통계 데이터 가져오기
    document.addEventListener('DOMContentLoaded', function() {
        loadStatistics();
    });
    
    function loadStatistics() {
        // 로딩 표시
        document.getElementById('loadingSpinner').style.display = 'block';
        
        // API 호출
        fetch('/api/statistics/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('네트워크 응답이 올바르지 않습니다');
                }
                return response.json();
            })
            .then(data => {
                // 성공 시 데이터 업데이트
                if (data.status === 'success' && data.data) {
                    updateStatistics(data.data);
                } else {
                    console.error('API 응답 오류:', data);
                    showError('데이터를 불러오는 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                console.error('API 호출 오류:', error);
                showError('서버에 연결할 수 없습니다.');
            })
            .finally(() => {
                // 로딩 숨기기
                document.getElementById('loadingSpinner').style.display = 'none';
            });
    }
    
    function updateStatistics(stats) {
        // 숫자 포맷팅 함수
        function formatNumber(num) {
            return num.toLocaleString('ko-KR');
        }
        
        // 각 통계 업데이트
        document.getElementById('total-announcements').textContent = 
            formatNumber(stats.total_announcements);
        document.getElementById('new-this-week').textContent = 
            formatNumber(stats.new_this_week);
        document.getElementById('total-consultations').textContent = 
            formatNumber(stats.total_consultations);
        document.getElementById('active-users').textContent = 
            formatNumber(stats.active_users);
    }
    
    function showError(message) {
        // 에러 메시지 표시 (간단한 알림)
        alert(message);
        // 또는 더 나은 방법: 토스트 메시지 표시
    }
</script>
{% endblock %}
```

### Step 4: CSS 파일 이동 및 연결

#### CSS 파일 이동

```
figma14/css/base.css     →  web/static/css/base.css
figma14/css/layout.css   →  web/static/css/layout.css
figma14/css/components.css → web/static/css/components.css
```

#### base.html에 CSS 연결

**파일**: `web/templates/base.html`

```django
{% load static %}

<head>
    <!-- ... 기존 코드 ... -->
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">
</head>
```

### Step 5: JavaScript 파일 이동 및 연결

#### JavaScript 파일 이동

```
figma14/js/main.js  →  web/static/js/main.js
```

#### base.html에 JS 연결

**파일**: `web/templates/base.html`

```django
<body>
    <!-- ... 기존 코드 ... -->
    
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
```

---

## 전체 흐름 정리

### 사용자가 홈 페이지를 방문할 때

```
1. 사용자: http://localhost:8000/ 접속
   ↓
2. Django: config/urls.py → web/urls.py → views.home_view 실행
   ↓
3. Django: web/templates/web/home.html 렌더링
   → base.html 확장해서 완성된 HTML 생성
   ↓
4. 브라우저: HTML 받아서 화면 표시
   → 통계 숫자는 아직 "-"로 표시됨
   ↓
5. 브라우저: <script> 태그 실행
   → loadStatistics() 함수 호출
   ↓
6. JavaScript: fetch('/api/statistics/') 호출
   ↓
7. Django: web/urls.py → views.api_statistics 실행
   → JSON 데이터 반환
   ↓
8. JavaScript: JSON 데이터 받아서 updateStatistics() 실행
   → DOM 업데이트 (숫자 표시)
   ↓
9. 사용자: 화면에 실제 통계 숫자 표시됨! 🎉
```

---

## API 응답 형식 (docs/api/api.yaml 기준)

### 요청

```
GET /api/statistics/
```

### 응답

```json
{
    "status": "success",
    "message": "요청을 성공적으로 처리했습니다.",
    "data": {
        "total_announcements": 1247,
        "new_this_week": 42,
        "total_consultations": 15823,
        "active_users": 3492
    }
}
```

**참고**: `docs/api/api.yaml`의 `/api/annc_summary` 엔드포인트와 유사한 구조입니다.

---

## 다음 단계: 실제 DB 연동

### 현재 (Mock Data)

```python
def api_statistics(request):
    stats = {
        "total_announcements": 1247,  # 하드코딩
        # ...
    }
    return JsonResponse({"data": stats})
```

### 향후 (DB 연동)

```python
from .models import Announcement, ChatHistory, User

def api_statistics(request):
    # 실제 DB에서 데이터 가져오기
    stats = {
        "total_announcements": Announcement.objects.count(),
        "new_this_week": Announcement.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        "total_consultations": ChatHistory.objects.count(),
        "active_users": User.objects.filter(
            last_login__gte=timezone.now() - timedelta(days=30)
        ).count(),
    }
    return JsonResponse({"data": stats})
```

---

## 체크리스트

변환 작업을 완료했는지 확인하세요:

- [ ] `web/views.py`에 `api_statistics` 함수 추가
- [ ] `web/urls.py`에 API 경로 추가 (`path('api/statistics/', ...)`)
- [ ] `web/templates/web/home.html`에 JavaScript 코드 추가
- [ ] CSS 파일을 `web/static/css/`로 이동
- [ ] JavaScript 파일을 `web/static/js/`로 이동
- [ ] `base.html`에 CSS/JS 파일 연결
- [ ] 브라우저에서 테스트 (`http://localhost:8000/`)
- [ ] 개발자 도구(F12)에서 네트워크 탭 확인 (API 호출 확인)

---

**작성일**: 2025-01-20  
**버전**: 1.0.0

