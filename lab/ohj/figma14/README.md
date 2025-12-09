# ZIPFIT Frontend 프로토타입 문서

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [폴더 구조](#폴더-구조)
3. [파일별 상세 설명](#파일별-상세-설명)
4. [기술 스택](#기술-스택)
5. [현재 상태 (Mock Data)](#현재-상태-mock-data)
6. [Django 연동 계획](#django-연동-계획)
7. [Templates 마이그레이션 가이드](#templates-마이그레이션-가이드)

---

## 프로젝트 개요

**ZIPFIT**은 공공주택(LH, SH, GH) 공고 정보를 AI 기반으로 분석하여 사용자에게 맞춤형 정보를 제공하는 웹 플랫폼입니다.

### 주요 기능
- 🏠 공공주택 공고 목록 조회 및 필터링
- 🤖 AI 기반 공고 상담 및 질의응답
- 👤 사용자 정보 기반 맞춤형 추천
- 📱 반응형 웹 디자인 (모바일/태블릿/데스크톱)

### 기술 제약사항
- **Frontend만 사용**: JavaScript, Bootstrap, CSS, HTML만으로 구성
- **Mock Data 기반**: 현재는 하드코딩된 데이터로 동작
- **Django 연동 예정**: 향후 Django 백엔드와 연동 예정

---

## 폴더 구조

```
figma14/
├── index.html          # 진입점 (landing.html로 리다이렉트)
├── landing.html        # 랜딩 페이지
├── user-info.html      # 사용자 정보 입력 페이지
├── main.html           # 메인 대시보드
├── chat.html           # AI 상담 채팅 페이지
├── list.html           # 공고 목록 페이지
├── css/
│   ├── base.css        # 기본 스타일 및 CSS 변수
│   ├── layout.css      # 레이아웃 (사이드바, 헤더 등)
│   └── components.css  # 컴포넌트 스타일
└── js/
    └── main.js         # 공통 JavaScript 기능
```

---

## 파일별 상세 설명

### HTML 파일

#### 1. `index.html`
- **역할**: 진입점, `landing.html`로 자동 리다이렉트
- **기능**: 메타 리프레시를 통한 페이지 이동

#### 2. `landing.html`
- **역할**: 서비스 소개 랜딩 페이지
- **주요 섹션**:
  - 히어로 섹션: 로고, 타이틀, CTA 버튼
  - Why ZIPFIT 섹션: 서비스 특징 소개 (3개 카드)
  - CTA 섹션: 시작하기 유도
  - 푸터: 저작권 및 배지
- **스타일**: 인라인 CSS 사용 (독립 페이지)
- **데이터**: 정적 콘텐츠, Mock Data 없음

#### 3. `user-info.html`
- **역할**: 사용자 정보 입력 폼
- **주요 기능**:
  - 사용자 ID 자동 생성 (랜덤 조합: 형용사 + 동물)
  - 필수 정보 입력: 나이, 희망 거주지, 신청 자격, 소득 정보 등
  - 조건부 필드: 신혼부부/다자녀 선택 시 자녀 수 필드 표시
  - 세션 스토리지 저장: `sessionStorage`에 사용자 정보 저장
- **데이터 저장 형식**:
```javascript
{
  userId: "매콤한 숫사슴",
  userAge: 28,
  userLocation: "서울특별시",
  applicationType: "청년",
  childrenCount: "0",
  incomeAmount: 3000,
  incomeType: "연봉",
  homelessPeriod: 5,
  savingsPeriod: 3,
  timestamp: "2025-01-20T10:30:00.000Z"
}
```

#### 4. `main.html`
- **역할**: 메인 대시보드 (홈)
- **주요 섹션**:
  - 히어로 섹션: 환영 메시지, 통계 카드, 기능 소개
  - 통계 그리드: 등록된 공고, 신규 공고, 누적 상담, 활성 사용자
  - 사이드바: 네비게이션, 채팅 히스토리, 사용자 정보
- **Mock Data**:
  - 사용자 이름: `sessionStorage`에서 로드
  - 통계: 하드코딩된 숫자 (1,247, 42, 15,823, 3,492)
  - 채팅 히스토리: 하드코딩된 2개 항목

#### 5. `chat.html`
- **역할**: AI 상담 채팅 인터페이스
- **주요 기능**:
  - 환영 메시지: 초기 로드 시 표시
  - 추천 질문: 4개 질문 카드 제공
  - 채팅 메시지: 사용자/AI 메시지 구분 표시
  - 로딩 애니메이션: AI 응답 대기 중 표시
  - URL 파라미터 지원: `?chat=chat1`, `?announcement=공고명`
- **Mock Data**: 하드코딩된 응답 딕셔너리
```javascript
const responses = {
  '청년 주택 공고를 알려줘': '응답 텍스트...',
  '신혼부부 특별공급 자격 조건은?': '응답 텍스트...',
  // ...
};
```

#### 6. `list.html`
- **역할**: 공고 목록 페이지
- **주요 기능**:
  - 검색: 제목 기반 실시간 필터링
  - 필터: 기관(LH/SH/GH), 유형(청년/신혼부부/행복/전세), 상태(모집중/마감/예정)
  - 공고 카드: 기관 배지, 상태 배지, 모집 기간, AI 상담 버튼
- **Mock Data**: 하드코딩된 6개 공고 카드
```javascript
// 공고 카드 데이터 구조 (data-* 속성으로 저장)
data-agency="LH" | "SH" | "GH"
data-type="청년" | "신혼부부" | "행복" | "전세"
data-status="모집 중" | "마감" | "예정"
```

### CSS 파일

#### 1. `css/base.css`
- **역할**: 기본 스타일 및 CSS 변수 정의
- **주요 내용**:
  - CSS 변수: 색상, 간격, 반경, 그림자, 전환 효과
  - 리셋 스타일: 기본 마진/패딩 제거
  - 타이포그래피: 폰트, 제목 스타일
  - 유틸리티 클래스: 텍스트 정렬, 플렉스, 간격 등
  - 스크롤바 스타일링

#### 2. `css/layout.css`
- **역할**: 레이아웃 구조 (사이드바, 메인 컨텐츠)
- **주요 컴포넌트**:
  - `.app-container`: 전체 앱 컨테이너 (Flexbox)
  - `.sidebar`: 고정 사이드바 (256px)
  - `.main-content`: 메인 컨텐츠 영역
  - `.main-header`: 상단 헤더
  - 반응형: 모바일 메뉴 토글, 오버레이

#### 3. `css/components.css`
- **역할**: 재사용 가능한 컴포넌트 스타일
- **주요 컴포넌트**:
  - 버튼: `.btn-primary`, `.btn-outline`, `.btn-gradient`
  - 채팅: `.chat-container`, `.message`, `.suggestion-card`
  - 공고 카드: `.announcement-card`, `.status-badge`
  - 배지: `.badge-lh`, `.badge-sh`, `.badge-gh`
  - 알림: `.alert`, `.toast`

### JavaScript 파일

#### 1. `js/main.js`
- **역할**: 공통 JavaScript 기능
- **주요 함수**:
  - `initMobileMenu()`: 모바일 메뉴 토글
  - `initNavigationHighlight()`: 현재 페이지 하이라이트
  - `initChatFeatures()`: 채팅 기능 초기화
  - `initSearchFilters()`: 검색/필터 기능
  - `debounce()`: 디바운스 유틸리티
  - `getCookie()`: Django CSRF 토큰 가져오기
  - `showToast()`, `showLoading()`: UI 피드백

---

## 기술 스택

### Frontend
- **HTML5**: 시맨틱 마크업
- **CSS3**: 
  - CSS Variables (Custom Properties)
  - Flexbox, Grid Layout
  - Media Queries (반응형)
- **JavaScript (ES6+)**:
  - Vanilla JavaScript (프레임워크 없음)
  - `sessionStorage` API
  - Fetch API (Django 연동 준비)
- **Bootstrap 5.3.0**: CDN 방식
- **Google Fonts**: Noto Sans KR

### 데이터 저장
- **sessionStorage**: 사용자 정보, 선택된 공고명
- **하드코딩**: 공고 목록, 채팅 응답, 통계

---

## 현재 상태 (Mock Data)

### 1. 사용자 정보
- **저장 위치**: `sessionStorage.getItem('userInfo')`
- **형식**: JSON 문자열
- **생성**: `user-info.html`에서 폼 제출 시
- **사용**: 모든 페이지에서 로드하여 표시

### 2. 채팅 응답
- **위치**: `chat.html` 내부 JavaScript
- **방식**: 질문 텍스트를 키로 하는 딕셔너리
- **로딩 시뮬레이션**: 2초 딜레이 후 응답 표시
- **예시**:
```javascript
const responses = {
  '청년 주택 공고를 알려줘': '응답 텍스트...',
  '신혼부부 특별공급 자격 조건은?': '응답 텍스트...'
};
```

### 3. 공고 목록
- **위치**: `list.html` 하드코딩
- **개수**: 6개 공고 카드
- **필터링**: 클라이언트 사이드 JavaScript로 필터링
- **데이터 구조**:
```html
<div class="announcement-card" 
     data-agency="LH" 
     data-type="청년" 
     data-status="모집 중">
  <!-- 카드 내용 -->
</div>
```

### 4. 통계 데이터
- **위치**: `main.html` 하드코딩
- **데이터**:
  - 등록된 공고: 1,247
  - 이번 주 신규: 42
  - 누적 상담: 15,823
  - 활성 사용자: 3,492

### 5. 채팅 히스토리
- **위치**: 사이드바 하드코딩
- **개수**: 2개 항목
- **기능**: 클릭 시 `chat.html?chat=chat1` 형태로 이동

---

## Django 연동 계획

### 1. API 엔드포인트 설계

#### 공고 목록 API
```javascript
// GET /api/announcements/
// Query Parameters: ?agency=LH&type=청년&status=모집중&search=고양
fetch('/api/announcements/?agency=LH&type=청년')
  .then(response => response.json())
  .then(data => {
    // data.announcements 배열을 받아서 렌더링
    renderAnnouncements(data.announcements);
  });
```

**응답 형식**:
```json
{
  "count": 6,
  "announcements": [
    {
      "id": 1,
      "title": "고양삼송 청년 행복주택",
      "agency": "LH",
      "type": "청년",
      "status": "모집 중",
      "recruitment_start": "2025-01-20",
      "recruitment_end": "2025-01-31",
      "location": "경기도 고양시 덕양구",
      "supply_count": 248,
      "website_url": "https://apply.lh.or.kr"
    }
  ]
}
```

#### AI 채팅 API
```javascript
// POST /api/chat/
fetch('/api/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    message: "청년 주택 공고를 알려줘",
    user_info: JSON.parse(sessionStorage.getItem('userInfo')),
    announcement_id: null  // 선택적
  })
})
  .then(response => response.json())
  .then(data => {
    // data.response를 채팅 메시지로 표시
    addMessage(data.response, false);
  });
```

**응답 형식**:
```json
{
  "response": "현재 모집 중인 청년 주택 공고는 다음과 같습니다:\n\n...",
  "references": [
    {
      "title": "고양삼송 청년 행복주택 공고문",
      "url": "/api/documents/1/"
    }
  ]
}
```

#### 사용자 정보 API
```javascript
// POST /api/user-info/
fetch('/api/user-info/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    user_info: JSON.parse(sessionStorage.getItem('userInfo'))
  })
})
  .then(response => response.json())
  .then(data => {
    // 서버에 저장 완료
    console.log('사용자 정보 저장 완료');
  });
```

#### 통계 API
```javascript
// GET /api/statistics/
fetch('/api/statistics/')
  .then(response => response.json())
  .then(data => {
    // data.total_announcements, data.new_this_week 등
    updateStatistics(data);
  });
```

### 2. 코드 수정 포인트

#### `chat.html` 수정
```javascript
// 기존: Mock 응답 딕셔너리
// 수정: API 호출
function sendMessageToAPI(message) {
  const userInfo = JSON.parse(sessionStorage.getItem('userInfo') || '{}');
  
  addLoadingMessage();
  
  fetch('/api/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      message: message,
      user_info: userInfo
    })
  })
    .then(response => response.json())
    .then(data => {
      removeLoadingMessage();
      addMessage(data.response, false);
    })
    .catch(error => {
      removeLoadingMessage();
      addMessage('오류가 발생했습니다. 다시 시도해주세요.', false);
    });
}
```

#### `list.html` 수정
```javascript
// 기존: 하드코딩된 공고 카드
// 수정: API에서 데이터 로드
function loadAnnouncements() {
  const params = new URLSearchParams({
    agency: document.getElementById('agencyFilter').value || '',
    type: document.getElementById('typeFilter').value || '',
    status: document.getElementById('statusFilter').value || '',
    search: document.getElementById('searchInput').value || ''
  });
  
  fetch(`/api/announcements/?${params}`)
    .then(response => response.json())
    .then(data => {
      renderAnnouncements(data.announcements);
    });
}

function renderAnnouncements(announcements) {
  const grid = document.getElementById('announcementGrid');
  grid.innerHTML = '';
  
  announcements.forEach(announcement => {
    const card = createAnnouncementCard(announcement);
    grid.appendChild(card);
  });
}
```

#### `main.html` 수정
```javascript
// 기존: 하드코딩된 통계
// 수정: API에서 로드
function loadStatistics() {
  fetch('/api/statistics/')
    .then(response => response.json())
    .then(data => {
      document.querySelector('.stat-number').textContent = data.total_announcements;
      // ...
    });
}
```

### 3. CSRF 토큰 처리
- Django 템플릿에서 `{% csrf_token %}` 사용
- JavaScript에서 `getCookie('csrftoken')` 함수로 토큰 가져오기
- 모든 POST 요청에 `X-CSRFToken` 헤더 추가

### 4. 에러 처리
```javascript
function handleAPIError(error) {
  if (error.status === 401) {
    // 인증 오류: 로그인 페이지로 이동
    window.location.href = '/login/';
  } else if (error.status === 500) {
    // 서버 오류: 사용자에게 알림
    showToast('서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'error');
  } else {
    showToast('오류가 발생했습니다.', 'error');
  }
}
```

---

## Templates 마이그레이션 가이드

### 1. 파일 구조 변경

#### 현재 구조 (figma14/)
```
figma14/
├── index.html
├── landing.html
├── user-info.html
├── main.html
├── list.html
├── chat.html
├── css/
└── js/
```

#### 목표 구조 (Django templates/)
```
zf_django/web/templates/
├── base.html              # 베이스 템플릿
├── landing.html           # 랜딩 페이지
├── user_info.html         # 사용자 정보 입력
├── main.html              # 메인 대시보드
├── list.html              # 공고 목록
├── chat.html              # AI 상담
└── partials/
    ├── sidebar.html       # 사이드바 부분 템플릿
    ├── header.html        # 헤더 부분 템플릿
    └── user_modal.html    # 사용자 정보 모달

zf_django/web/static/
├── css/
│   ├── base.css
│   ├── layout.css
│   └── components.css
└── js/
    └── main.js
```

### 2. 베이스 템플릿 생성

#### `templates/base.html`
```django
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}집핏 ZIPFIT{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 모바일 메뉴 토글 -->
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
        <!-- SVG 아이콘 -->
    </button>
    
    <!-- 사이드바 오버레이 -->
    <div class="sidebar-overlay" onclick="toggleSidebar()"></div>
    
    <div class="app-container">
        <!-- 사이드바 -->
        {% include 'partials/sidebar.html' %}
        
        <!-- 메인 컨텐츠 -->
        <main class="main-content">
            <!-- 헤더 -->
            {% include 'partials/header.html' %}
            
            <!-- 페이지 컨텐츠 -->
            {% block content %}{% endblock %}
        </main>
    </div>
    
    <!-- 사용자 정보 수정 모달 -->
    {% include 'partials/user_modal.html' %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="{% static 'js/main.js' %}"></script>
    
    <!-- CSRF Token -->
    {% csrf_token %}
    <script>
        function getCookie(name) {
            // Django CSRF 토큰 가져오기
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        // 전역 CSRF 토큰 설정
        const csrftoken = getCookie('csrftoken');
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 3. 부분 템플릿 분리

#### `templates/partials/sidebar.html`
```django
<aside class="sidebar">
    <div class="sidebar-header">
        <!-- 로고 -->
    </div>
    
    <nav class="sidebar-nav">
        <a href="{% url 'main' %}" class="nav-item {% if request.resolver_match.url_name == 'main' %}active{% endif %}">
            <!-- 홈 아이콘 -->
            <span>홈</span>
        </a>
        <a href="{% url 'chat' %}" class="nav-item {% if request.resolver_match.url_name == 'chat' %}active{% endif %}">
            <!-- AI 상담 아이콘 -->
            <span>AI 상담</span>
        </a>
        <a href="{% url 'list' %}" class="nav-item {% if request.resolver_match.url_name == 'list' %}active{% endif %}">
            <!-- 공고 목록 아이콘 -->
            <span>공고 목록</span>
        </a>
        
        <!-- 채팅 히스토리 -->
        {% if chat_history %}
        <div class="chat-history mt-3">
            {% for chat in chat_history %}
            <div class="chat-history-item" onclick="window.location.href='{% url 'chat' %}?chat={{ chat.id }}'">
                <h5>{{ chat.title }}</h5>
                <p>{{ chat.preview }}</p>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </nav>
    
    <!-- 사용자 정보 -->
    <div class="user-info" onclick="openUserEditModal()">
        <!-- 사용자 아바타 및 정보 -->
    </div>
</aside>
```

#### `templates/partials/header.html`
```django
<header class="main-header">
    <div class="header-title">
        <h1>{% block page_title %}홈{% endblock %}</h1>
        <p>{% block page_subtitle %}LH · SH · GH 공식 정보 기반{% endblock %}</p>
    </div>
    <div class="header-actions">
        <span class="badge-lh">LH</span>
        <span class="badge-sh">SH</span>
        <span class="badge-gh">GH</span>
        <button class="theme-toggle">
            <!-- 테마 토글 아이콘 -->
        </button>
    </div>
</header>
```

### 4. 페이지 템플릿 변환

#### `templates/list.html`
```django
{% extends 'base.html' %}
{% load static %}

{% block title %}공고 목록 - 집핏 ZIPFIT{% endblock %}

{% block page_title %}공고 목록{% endblock %}
{% block page_subtitle %}최신 공공주택 공고를 확인하세요{% endblock %}

{% block content %}
<!-- 필터 섹션 -->
<div class="filters-section">
    <div class="search-box">
        <input type="text" placeholder="공고를 검색하세요..." id="searchInput">
    </div>
    
    <div class="filter-group">
        <select class="filter-select" id="agencyFilter">
            <option value="">전체 기관</option>
            <option value="LH">LH 한국토지주택공사</option>
            <option value="SH">SH 서울주택도시공사</option>
            <option value="GH">GH 경기주택도시공사</option>
        </select>
        <!-- 기타 필터 -->
    </div>
</div>

<!-- 공고 그리드 -->
<div class="announcement-grid" id="announcementGrid">
    {% for announcement in announcements %}
    <div class="announcement-card" 
         data-agency="{{ announcement.agency }}" 
         data-type="{{ announcement.type }}" 
         data-status="{{ announcement.status }}">
        <div class="announcement-header">
            <div>
                <span class="agency-badge agency-{{ announcement.agency|lower }}">{{ announcement.agency }}</span>
                <span class="type-badge">{{ announcement.type }}</span>
            </div>
            <span class="status-badge status-{{ announcement.status_class }}">{{ announcement.status }}</span>
        </div>
        <h3>{{ announcement.title }}</h3>
        
        <div class="recruitment-period">
            <!-- 모집 기간 표시 -->
            <span class="recruitment-period-date">{{ announcement.recruitment_start }} ~ {{ announcement.recruitment_end }}</span>
        </div>
        
        <div class="announcement-actions">
            <button class="btn-ai-consult" onclick="goToAIConsult('{{ announcement.title }}')">
                AI 상담하기
            </button>
            <button class="btn-website" onclick="window.open('{{ announcement.website_url }}', '_blank')">
                공고문 웹페이지
            </button>
        </div>
    </div>
    {% empty %}
    <p>등록된 공고가 없습니다.</p>
    {% endfor %}
</div>
{% endblock %}

{% block extra_js %}
<script>
    // 필터링 로직 (기존과 동일)
    function filterAnnouncements() {
        // ...
    }
    
    // API 연동 (Django)
    function loadAnnouncements() {
        const params = new URLSearchParams({
            agency: document.getElementById('agencyFilter').value || '',
            type: document.getElementById('typeFilter').value || '',
            status: document.getElementById('statusFilter').value || '',
            search: document.getElementById('searchInput').value || ''
        });
        
        fetch(`{% url 'api:announcements' %}?${params}`)
            .then(response => response.json())
            .then(data => {
                renderAnnouncements(data.announcements);
            });
    }
</script>
{% endblock %}
```

### 5. 정적 파일 설정

#### `settings.py`
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'web' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

#### `urls.py`
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### 6. 마이그레이션 체크리스트

- [ ] `base.html` 생성 및 공통 구조 정의
- [ ] 사이드바, 헤더를 부분 템플릿으로 분리
- [ ] 각 HTML 파일을 Django 템플릿으로 변환
- [ ] CSS/JS 파일을 `static/` 폴더로 이동
- [ ] `{% load static %}` 및 `{% static %}` 태그 적용
- [ ] URL 라우팅 설정 (`urls.py`)
- [ ] 뷰 함수 생성 (`views.py`)
- [ ] Mock Data를 Django 모델/API로 교체
- [ ] CSRF 토큰 처리 확인
- [ ] 반응형 디자인 테스트
- [ ] 브라우저 호환성 테스트

### 7. 주의사항

1. **경로 변경**: 상대 경로(`css/base.css`) → Django 정적 파일 경로(`{% static 'css/base.css' %}`)
2. **인라인 스타일**: 페이지별 인라인 CSS는 `{% block extra_css %}`로 이동
3. **인라인 스크립트**: 페이지별 JavaScript는 `{% block extra_js %}`로 이동
4. **데이터 바인딩**: 하드코딩된 데이터를 Django 템플릿 변수로 교체
5. **URL 하드코딩**: `href="main.html"` → `href="{% url 'main' %}"`
6. **세션 스토리지**: 사용자 정보는 Django 세션 또는 데이터베이스로 마이그레이션 고려

---

## 추가 고려사항

### 성능 최적화
- CSS/JS 파일 압축 및 최소화
- 이미지 최적화 (SVG 사용 권장)
- CDN 활용 (Bootstrap, Google Fonts)

### 접근성
- ARIA 레이블 추가
- 키보드 네비게이션 지원
- 색상 대비 비율 확인

### 보안
- XSS 방지: Django 템플릿 자동 이스케이핑 활용
- CSRF 보호: 모든 POST 요청에 CSRF 토큰 포함
- 입력 검증: 클라이언트 및 서버 양쪽에서 검증

### 테스트
- 브라우저 호환성: Chrome, Firefox, Safari, Edge
- 반응형 테스트: 모바일(375px), 태블릿(768px), 데스크톱(1920px)
- 기능 테스트: 필터링, 검색, 채팅, 모달 등

---

## 참고 자료

- [Django 템플릿 문서](https://docs.djangoproject.com/en/stable/topics/templates/)
- [Django 정적 파일 관리](https://docs.djangoproject.com/en/stable/howto/static-files/)
- [Bootstrap 5 문서](https://getbootstrap.com/docs/5.3/)
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/ko/docs/Web/JavaScript)

---

**작성일**: 2025-01-20  
**버전**: 1.0.0  
**작성자**: ZIPFIT 개발팀

