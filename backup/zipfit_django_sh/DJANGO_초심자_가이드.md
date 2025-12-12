# Django 프로젝트 초심자 가이드 📚

> **이 문서는 Django를 처음 접하는 개발자를 위해 작성되었습니다.**  
> ZIPFIT 프로젝트의 실제 코드를 바탕으로 Django가 어떻게 작동하는지 단계별로 설명합니다.

---

## 📋 목차

1. [Django란 무엇인가?](#1-django란-무엇인가)
2. [프로젝트 폴더 구조 이해하기](#2-프로젝트-폴더-구조-이해하기)
3. [사용자 요청이 응답까지 가는 전체 흐름](#3-사용자-요청이-응답까지-가는-전체-흐름)
4. [각 파일의 역할 상세 설명](#4-각-파일의-역할-상세-설명)
5. [figma14를 Django로 변환하는 방법](#5-figma14를-django로-변환하는-방법)
6. [API 호출 예시 (JavaScript → Django)](#6-api-호출-예시-javascript--django)

---

## 1. Django란 무엇인가?

### 간단한 비유
**Django는 웹사이트의 "뇌"입니다.**

- **HTML/CSS/JavaScript (figma14)**: 사용자가 보는 화면 (얼굴, 옷, 표정)
- **Django**: 화면 뒤에서 일하는 두뇌 (데이터 처리, 로직, 서버)

### Django의 역할
1. **URL 라우팅**: 어떤 주소(`/home`, `/chat`)가 어떤 페이지를 보여줄지 결정
2. **데이터 처리**: 데이터베이스에서 데이터를 가져오거나 저장
3. **템플릿 렌더링**: HTML 파일에 데이터를 넣어서 완성된 페이지를 만들어줌
4. **API 제공**: JavaScript가 데이터를 요청하면 JSON 형식으로 응답

---

## 2. 프로젝트 폴더 구조 이해하기

```
zipfit_django/
│
├── manage.py                    ⭐ Django 프로젝트의 시작점 (서버 실행)
│
├── config/                      ⭐ 프로젝트 설정 폴더 (뇌의 중추)
│   ├── settings.py              → 전체 프로젝트 설정 (DB, 앱 등록 등)
│   ├── urls.py                  → 최상위 URL 라우팅 (어디로 보낼지 결정)
│   ├── wsgi.py                  → 서버 배포용 (지금은 신경 안 써도 됨)
│   └── asgi.py                  → 비동기 서버용 (지금은 신경 안 써도 됨)
│
├── web/                         ⭐ 웹 화면(UI) 전용 앱
│   ├── urls.py                  → web 앱의 URL 라우팅
│   ├── views.py                 → 실제 로직 처리 (데이터 가공, 템플릿 렌더링)
│   ├── templates/               → HTML 파일들
│   │   ├── base.html            → 공통 레이아웃 (사이드바, 헤더)
│   │   └── web/
│   │       ├── home.html         → 홈 페이지
│   │       ├── chat.html         → 채팅 페이지
│   │       ├── announcements.html → 공고 목록 페이지
│   │       └── profile.html      → 프로필 페이지
│   └── static/                  → CSS, JavaScript, 이미지 파일들
│       ├── css/
│       ├── js/
│       └── images/
│
└── chatbot/                     ⭐ AI 채팅 API 전용 앱
    ├── urls.py                  → chatbot 앱의 URL 라우팅
    ├── views.py                 → AI API 호출 로직
    └── models.py                → 데이터베이스 모델 (지금은 비어있음)
```

### 핵심 개념: "앱(App)"

Django는 **앱(App)** 단위로 기능을 나눕니다.

- **`web` 앱**: 사용자가 보는 화면 (홈, 채팅, 공고 목록 등)
- **`chatbot` 앱**: AI API 호출만 담당

**왜 나눌까?**
- 코드가 깔끔해짐
- 팀원끼리 작업 분담이 쉬움
- 나중에 기능 추가/수정이 편함

---

## 3. 사용자 요청이 응답까지 가는 전체 흐름

### 🎯 예시: 사용자가 "홈 페이지"를 요청할 때

```
1. 사용자가 브라우저에 "http://localhost:8000/" 입력
   ↓
2. Django가 config/urls.py를 확인
   → "어? '/' 경로네? web.urls로 보내야겠다"
   ↓
3. Django가 web/urls.py를 확인
   → "어? '' (빈 경로)네? views.home_view로 보내야겠다"
   ↓
4. Django가 web/views.py의 home_view 함수 실행
   → "홈 페이지를 렌더링해야겠다"
   ↓
5. Django가 web/templates/web/home.html 파일을 읽음
   → base.html을 확장(extends)해서 완성된 HTML 생성
   ↓
6. 완성된 HTML을 사용자 브라우저로 전송
   → 사용자가 화면을 봄! 🎉
```

### 📊 흐름도 (Flow Chart)

```
사용자 브라우저
    ↓ (요청: GET /)
config/urls.py
    ↓ (include('web.urls'))
web/urls.py
    ↓ (path('', views.home_view))
web/views.py
    ↓ (render(request, "web/home.html"))
web/templates/web/home.html
    ↓ ({% extends "base.html" %})
web/templates/base.html
    ↓ (완성된 HTML)
사용자 브라우저 (화면 표시)
```

---

## 4. 각 파일의 역할 상세 설명

### 4.1 `config/settings.py` - 프로젝트 전체 설정

**역할**: Django 프로젝트의 "설정 파일"

```python
# 예시: 우리 프로젝트의 주요 설정들

INSTALLED_APPS = [
    'web',        # ← 우리가 만든 web 앱 등록
    'chatbot',    # ← 우리가 만든 chatbot 앱 등록
]

TEMPLATES = [
    {
        'DIRS': [
            BASE_DIR / 'web' / 'templates',  # ← HTML 파일 위치 알려줌
        ],
    },
]

STATICFILES_DIRS = [
    BASE_DIR / 'web' / 'static',  # ← CSS, JS 파일 위치 알려줌
]
```

**왜 중요한가?**
- Django가 어떤 앱을 사용할지, HTML/CSS 파일을 어디서 찾을지 알려줌
- 이 파일에 등록하지 않으면 Django가 찾지 못함!

---

### 4.2 `config/urls.py` - 최상위 URL 라우팅

**역할**: "어떤 경로를 어떤 앱으로 보낼지" 결정하는 교통정리

```python
from django.urls import path, include

urlpatterns = [
    path('', include('web.urls')),           # ← '/' 경로는 web 앱으로
    path('admin/', admin.site.urls),         # ← '/admin' 경로는 관리자 페이지로
    path('chatbot/', include('chatbot.urls')), # ← '/chatbot' 경로는 chatbot 앱으로
]
```

**예시**:
- 사용자가 `/` 요청 → `web.urls`로 전달
- 사용자가 `/chatbot/ask/` 요청 → `chatbot.urls`로 전달

---

### 4.3 `web/urls.py` - web 앱의 URL 라우팅

**역할**: web 앱 내에서 "어떤 경로가 어떤 함수를 실행할지" 결정

```python
from django.urls import path
from . import views  # ← 같은 폴더의 views.py 가져오기

urlpatterns = [
    path('', views.home_view, name='home'),              # ← '/' → home_view 함수
    path('web/', views.chat_view, name='chat'),          # ← '/web/' → chat_view 함수
    path('profile/', views.profile_view, name='profile'), # ← '/profile/' → profile_view 함수
    path('announcements/', views.announcements_view, name='announcements'),
]
```

**변수 설명**:
- `path('', ...)`: 첫 번째 인자는 URL 경로
- `views.home_view`: 두 번째 인자는 실행할 함수
- `name='home'`: 템플릿에서 `{% url 'home' %}`로 사용 가능

---

### 4.4 `web/views.py` - 실제 로직 처리

**역할**: "실제로 일을 하는 곳" - 데이터 가공, 템플릿 렌더링

#### 예시 1: 홈 페이지 (단순 렌더링)

```python
def home_view(request):
    return render(request, "web/home.html")
```

**설명**:
- `request`: 사용자의 요청 정보가 담긴 객체
- `render()`: HTML 템플릿을 렌더링해서 사용자에게 보여줌
- `"web/home.html"`: `web/templates/web/home.html` 파일을 찾음

#### 예시 2: 공고 목록 페이지 (데이터 처리)

```python
def announcements_view(request):
    # 1. 더미 데이터 생성 (나중에 DB에서 가져올 예정)
    announcements = [
        {"id": 1, "title": "테스트 공고 1", ...},
        {"id": 2, "title": "테스트 공고 2", ...},
    ]
    
    # 2. 필터링 (GET 파라미터로 필터 적용)
    type_filter = request.GET.get("type")  # ← URL의 ?type=청년 같은 값
    if type_filter:
        announcements = [a for a in announcements if a["category"] == type_filter]
    
    # 3. 템플릿에 데이터 전달
    return render(request, "web/announcements.html", {
        "announcements": announcements,  # ← 템플릿에서 사용 가능
    })
```

**설명**:
- `request.GET.get("type")`: URL의 쿼리 파라미터 가져오기 (`?type=청년`)
- 마지막 딕셔너리: 템플릿에 전달할 데이터 (템플릿에서 `{{ announcements }}`로 사용)

#### 예시 3: 프로필 저장 (세션 사용)

```python
def profile_view(request):
    # GET 요청: 폼 보여주기
    if request.method == "GET":
        user_context = request.session.get("user_context", {})
        return render(request, "web/profile.html", {
            "user_context": user_context,
        })
    
    # POST 요청: 데이터 저장
    if request.method == "POST":
        context = {
            "region": request.POST.get("region"),
            "age": request.POST.get("age"),
            # ...
        }
        request.session["user_context"] = context  # ← 세션에 저장
        return render(request, "web/profile.html", {"saved": True})
```

**설명**:
- `request.method`: 요청 방식 (GET=조회, POST=저장)
- `request.session`: 사용자별 데이터 저장 (로그인 없이도 사용 가능)
- `request.POST.get("region")`: 폼에서 전송된 데이터 가져오기

---

### 4.5 `web/templates/base.html` - 공통 레이아웃

**역할**: 모든 페이지에 공통으로 들어가는 부분 (사이드바, 헤더 등)

```django
<!DOCTYPE html>
<html lang="ko">
<head>
    <title>{% block title %}ZIPFIT{% endblock %}</title>
    <!-- Tailwind CDN -->
</head>
<body>
    <!-- 사이드바 -->
    <aside>...</aside>
    
    <!-- 메인 컨텐츠 -->
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

**Django 템플릿 문법**:
- `{% block title %}`: 자식 템플릿이 덮어쓸 수 있는 영역
- `{% block content %}`: 각 페이지의 고유 내용이 들어갈 영역

---

### 4.6 `web/templates/web/home.html` - 홈 페이지

**역할**: 홈 페이지의 고유 내용

```django
{% extends "base.html" %}  ← base.html을 확장 (상속)

{% block title %}홈 | ZIPFIT{% endblock %}  ← title 블록 덮어쓰기

{% block content %}  ← content 블록에 내용 추가
    <h1>홈 페이지 내용</h1>
    <p>등록된 공고: 1,247 건</p>
{% endblock %}
```

**설명**:
- `{% extends "base.html" %}`: base.html의 구조를 가져옴
- `{% block content %}`: base.html의 `{% block content %}` 부분을 이 내용으로 교체

**결과**: base.html의 사이드바 + 헤더 + 이 페이지의 고유 내용이 합쳐져서 완성됨!

---

### 4.7 `chatbot/views.py` - API 엔드포인트

**역할**: JavaScript가 호출하는 API (JSON 응답)

```python
@csrf_exempt  # ← CSRF 토큰 검증 생략 (API용)
def ask_api(request):
    if request.method == "POST":
        data = json.loads(request.body)  # ← JSON 데이터 파싱
        query = data.get("query", "")
        
        # 나중에 여기서 AI API 호출할 예정
        return JsonResponse({
            "answer": f"테스트 응답입니다. 질문: {query}",
        })
    
    return JsonResponse({"error": "POST 요청만 지원합니다."}, status=400)
```

**설명**:
- `@csrf_exempt`: CSRF 토큰 없이도 요청 허용 (API용)
- `json.loads(request.body)`: JSON 형식의 요청 데이터 파싱
- `JsonResponse()`: JSON 형식으로 응답 (JavaScript가 받을 수 있음)

---

## 5. figma14를 Django로 변환하는 방법

### 5.1 현재 상황 비교

| 항목 | figma14 (현재) | Django (목표) |
|------|---------------|---------------|
| HTML 파일 | `figma14/main.html` | `web/templates/web/home.html` |
| CSS 파일 | `figma14/css/base.css` | `web/static/css/base.css` |
| JavaScript | `<script>` 태그 안 | `web/static/js/main.js` |
| 데이터 | 하드코딩 (Mock Data) | Django views.py에서 전달 |
| URL | `main.html` (파일명) | `/` (Django URL) |

### 5.2 변환 단계별 가이드

#### Step 1: HTML 파일 이동 및 수정

**Before (figma14/main.html)**:
```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="css/base.css">
</head>
<body>
    <h1>등록된 공고: 1,247</h1>
</body>
</html>
```

**After (web/templates/web/home.html)**:
```django
{% extends "base.html" %}
{% load static %}

{% block title %}홈 - 집핏 ZIPFIT{% endblock %}

{% block content %}
    <h1>등록된 공고: {{ total_announcements }}</h1>
{% endblock %}
```

**변경 사항**:
1. `{% extends "base.html" %}`: 공통 레이아웃 사용
2. `{% load static %}`: 정적 파일 사용 선언
3. `{{ total_announcements }}`: Django 변수 사용 (하드코딩 대신)

#### Step 2: CSS/JS 파일 이동

```
figma14/css/base.css  →  web/static/css/base.css
figma14/js/main.js    →  web/static/js/main.js
```

**템플릿에서 사용**:
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<script src="{% static 'js/main.js' %}"></script>
```

#### Step 3: Mock Data를 Django views.py로 이동

**Before (figma14/main.html - 하드코딩)**:
```html
<div class="stat-number">1,247</div>
<div class="stat-number">42</div>
```

**After (web/views.py - 동적 데이터)**:
```python
def home_view(request):
    # 나중에 DB에서 가져올 예정
    stats = {
        "total_announcements": 1247,
        "new_this_week": 42,
        "total_consultations": 15823,
        "active_users": 3492,
    }
    
    return render(request, "web/home.html", {
        "stats": stats,  # ← 템플릿에 전달
    })
```

**템플릿에서 사용**:
```django
<div class="stat-number">{{ stats.total_announcements }}</div>
<div class="stat-number">{{ stats.new_this_week }}</div>
```

#### Step 4: URL 라우팅 설정

**web/urls.py에 추가**:
```python
urlpatterns = [
    path('', views.home_view, name='home'),  # ← 이미 있음
]
```

**템플릿에서 링크 사용**:
```django
<!-- Before: <a href="main.html">홈</a> -->
<!-- After: -->
<a href="{% url 'home' %}">홈</a>
```

---

## 6. API 호출 예시 (JavaScript → Django)

### 6.1 홈 페이지 통계 데이터 가져오기

#### Django 측 (web/views.py)

```python
from django.http import JsonResponse

def api_statistics(request):
    """홈 페이지 통계 API"""
    stats = {
        "total_announcements": 1247,
        "new_this_week": 42,
        "total_consultations": 15823,
        "active_users": 3492,
    }
    return JsonResponse({
        "status": "success",
        "data": stats,
    })
```

#### URL 설정 (web/urls.py)

```python
urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/statistics/', views.api_statistics, name='api_statistics'),  # ← 추가
]
```

#### JavaScript 측 (web/templates/web/home.html)

```html
{% block content %}
<div id="statistics">
    <div class="stat-number" id="total-announcements">로딩 중...</div>
    <div class="stat-number" id="new-this-week">로딩 중...</div>
</div>

<script>
    // 페이지 로드 시 API 호출
    fetch('/api/statistics/')
        .then(response => response.json())
        .then(data => {
            // 데이터 업데이트
            document.getElementById('total-announcements').textContent = 
                data.data.total_announcements;
            document.getElementById('new-this-week').textContent = 
                data.data.new_this_week;
        })
        .catch(error => {
            console.error('오류:', error);
        });
</script>
{% endblock %}
```

### 6.2 채팅 메시지 전송 (POST 요청)

#### Django 측 (chatbot/views.py)

```python
@csrf_exempt
def ask_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("user_message", "")
        user_key = data.get("user_key", "")
        
        # 나중에 여기서 AI API 호출
        ai_response = f"안녕하세요, {user_key}님! 질문: {user_message}"
        
        return JsonResponse({
            "status": "success",
            "data": {
                "ai_response": {
                    "message": ai_response,
                    "message_type": "bot",
                }
            }
        })
    
    return JsonResponse({"error": "POST만 지원"}, status=400)
```

#### JavaScript 측 (web/templates/web/chat.html)

```html
<script>
    function sendMessage() {
        const message = document.getElementById('messageInput').value;
        const userKey = '매콤한 숫사슴';  // 나중에 세션에서 가져올 예정
        
        fetch('/chatbot/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_key: userKey,
                user_message: message,
            })
        })
        .then(response => response.json())
        .then(data => {
            // AI 응답 표시
            addMessage(data.data.ai_response.message, false);
        })
        .catch(error => {
            console.error('오류:', error);
        });
    }
</script>
```

### 6.3 공고 목록 필터링 (GET 요청)

#### JavaScript 측

```javascript
function filterAnnouncements() {
    const agency = document.getElementById('agencyFilter').value;
    const type = document.getElementById('typeFilter').value;
    
    // URL 파라미터 생성
    const params = new URLSearchParams({
        agency: agency || '',
        type: type || '',
    });
    
    fetch(`/api/announcements/?${params}`)
        .then(response => response.json())
        .then(data => {
            // 공고 목록 렌더링
            renderAnnouncements(data.data.items);
        });
}
```

#### Django 측 (web/views.py)

```python
from django.http import JsonResponse

def api_announcements(request):
    """공고 목록 API"""
    # GET 파라미터 가져오기
    agency = request.GET.get("agency", "")
    type_filter = request.GET.get("type", "")
    
    # 필터링 로직 (나중에 DB 쿼리로 변경)
    announcements = [
        {"id": 1, "title": "공고 1", "agency": "LH"},
        {"id": 2, "title": "공고 2", "agency": "SH"},
    ]
    
    if agency:
        announcements = [a for a in announcements if a["agency"] == agency]
    
    return JsonResponse({
        "status": "success",
        "data": {
            "items": announcements,
            "total_count": len(announcements),
        }
    })
```

---

## 7. 실제 사용자 흐름 예시

### 시나리오: 사용자가 홈 페이지에서 통계를 보고 싶어함

```
1. 사용자가 브라우저에 "http://localhost:8000/" 입력
   ↓
2. Django가 config/urls.py 확인
   → path('', include('web.urls'))
   ↓
3. Django가 web/urls.py 확인
   → path('', views.home_view, name='home')
   ↓
4. Django가 web/views.py의 home_view 함수 실행
   → return render(request, "web/home.html")
   ↓
5. Django가 web/templates/web/home.html 렌더링
   → base.html 확장해서 완성된 HTML 생성
   ↓
6. 완성된 HTML을 사용자 브라우저로 전송
   → 사용자가 화면을 봄
   ↓
7. 브라우저가 HTML의 <script> 태그 실행
   → fetch('/api/statistics/') 호출
   ↓
8. Django가 web/urls.py 확인
   → path('api/statistics/', views.api_statistics)
   ↓
9. Django가 web/views.py의 api_statistics 함수 실행
   → return JsonResponse({"data": stats})
   ↓
10. JSON 응답을 브라우저로 전송
    → JavaScript가 데이터 받음
    ↓
11. JavaScript가 DOM 업데이트
    → 통계 숫자가 화면에 표시됨! 🎉
```

---

## 8. 핵심 정리

### Django의 3대 핵심 파일

1. **`urls.py`**: "어디로 보낼지" 결정 (교통정리)
2. **`views.py`**: "무엇을 할지" 결정 (실제 작업)
3. **`templates/*.html`**: "어떻게 보여줄지" 결정 (화면)

### 데이터 흐름

```
사용자 요청
    ↓
urls.py (라우팅)
    ↓
views.py (로직 처리)
    ↓
templates (HTML 렌더링)
    ↓
사용자에게 응답
```

### API 호출 흐름

```
JavaScript (프론트엔드)
    ↓ fetch('/api/statistics/')
urls.py (API 라우팅)
    ↓
views.py (데이터 처리)
    ↓ return JsonResponse()
JavaScript (데이터 받아서 화면 업데이트)
```

---

## 9. 다음 단계

1. **DB 연동**: 하드코딩된 데이터를 데이터베이스에서 가져오기
2. **인증 시스템**: 사용자 로그인/회원가입
3. **세션 관리**: 사용자 정보를 세션이 아닌 DB에 저장
4. **AI API 연동**: chatbot/views.py에서 실제 AI API 호출

---

## 10. 자주 묻는 질문 (FAQ)

### Q1: 왜 `web/templates/web/`처럼 중복된 폴더명이 있나요?

**A**: Django가 앱별로 템플릿을 구분하기 위함입니다.
- `web/templates/web/home.html`: web 앱의 home.html
- `chatbot/templates/chatbot/...`: chatbot 앱의 템플릿 (나중에 추가 가능)

### Q2: `{% load static %}`는 왜 필요한가요?

**A**: Django 템플릿에서 정적 파일(CSS, JS)을 사용하려면 선언이 필요합니다.

### Q3: `request.session`은 무엇인가요?

**A**: 사용자별로 데이터를 저장하는 공간입니다. 로그인 없이도 사용 가능하며, 브라우저를 닫으면 사라집니다.

### Q4: `@csrf_exempt`는 왜 필요한가요?

**A**: API 엔드포인트는 CSRF 토큰 검증을 생략하기 위함입니다. 일반 폼 제출은 필요하지만, JavaScript API 호출은 생략 가능합니다.

---

**작성일**: 2025-01-20  
**버전**: 1.0.0  
**작성자**: ZIPFIT 개발팀

