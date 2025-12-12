# 집핏 (ZIPFIT) - 공공주택 정보 플랫폼

HTML, CSS, JavaScript, Bootstrap으로 구현한 공공주택 정보 플랫폼입니다.  
Django 프로젝트에서 템플릿으로 사용할 수 있도록 설계되었습니다.

## 📁 프로젝트 구조

```
zipfit/
├── index.html              # 진입점 (landing.html로 리다이렉트)
├── landing.html            # 1. 랜딩 페이지 ⭐ 시작 페이지
├── user-info.html          # 2. 사용자 정보 입력 페이지
├── main.html               # 3. 메인 홈 페이지 (빠른 메뉴)
├── chat.html               # 4. AI 상담 페이지
├── list.html               # 5. 공고 목록 페이지
├── css/
│   ├── base.css           # 기본 스타일 (변수, 리셋, 유틸리티)
│   ├── layout.css         # 레이아웃 (사이드바, 헤더)
│   └── components.css     # 컴포넌트 스타일
├── js/
│   └── main.js            # 공통 JavaScript
└── README.md              # 프로젝트 설명서
```

## 🚀 빠른 시작

### 1. 로컬에서 실행하기

#### 방법 A: 브라우저에서 직접 열기
```bash
# landing.html 파일을 더블클릭하거나
open landing.html
# Windows: start landing.html
```

#### 방법 B: Python 로컬 서버 (권장)
```bash
# Python 3
python -m http.server 8000

# 브라우저에서
http://localhost:8000/landing.html
```

#### 방법 C: VS Code Live Server
1. VS Code에서 Live Server 확장 프로그램 설치
2. `landing.html` 우클릭 → "Open with Live Server"

### 2. 페이지 탐색 순서

1. **landing.html** → 랜딩 페이지 (첫 시작)
   - "시작하기" 버튼 → user-info.html로 이동
   - "더 알아보기" 버튼 → 같은 페이지 내 Why ZIPFIT 섹션으로 스크롤
   - "무료로 시작하기" 버튼 → user-info.html로 이동

2. **user-info.html** → 사용자 정보 입력
   - 필수 정보 입력 후 세션 저장
   - 저장 완료 후 main.html로 자동 이동

3. **main.html** → 메인 홈 (빠른 메뉴)
   - 6개의 메뉴 카드로 서비스 접근

4. **chat.html** → AI 상담
   - 4개의 추천 질문
   - 실시간 채팅 시뮬레이션

5. **list.html** → 공고 목록
   - 검색 및 필터링 (기관별, 유형별)
   - 6개의 예시 공고 카드

## 📄 페이지 상세 설명

### 1. landing.html - 랜딩 페이지 ⭐

**역할:** Figma 디자인과 동일한 첫 방문자 환영 페이지

**특징:**
- 그라디언트 배경과 블러 효과
- 로고 + "나에게 딱 맞는 집, ZIPFIT" 슬로건
- 2개의 CTA 버튼:
  - 시작하기 (user-info.html로 이동)
  - 더 알아보기 (Why ZIPFIT 섹션으로 스크롤)
- Why ZIPFIT 섹션 (3개의 특징 카드)
- "지금 바로 시작하세요" CTA 섹션
- 푸터 (LH, SH, GH 배지)

**구현 사항:**
- ✅ Figma 디자인 완전 재현
- ✅ 부드러운 스크롤 효과
- ✅ 반응형 디자인

### 2. user-info.html - 사용자 정보 입력 페이지

**역할:** 맞춤형 추천을 위한 사용자 정보 수집

**특징:**
- 집핏 로고 및 설명
- 입력 폼:
  - 이름 (필수)
  - 나이 (필수)
  - 거주지 (필수, 17개 시도 선택)
  - 결혼 여부 (필수)
  - 소득 분위 (필수, 1~5분위)
  - 무주택 기간 (선택)
  - 청약 가입 기간 (선택)
- 실시간 유효성 검사
- SessionStorage에 저장

**구현 사항:**
- ✅ 완전한 폼 입력 기능
- ✅ 세션 저장 및 불러오기
- ✅ 유효성 검사 및 에러 메시지
- ✅ 저장 후 main.html로 자동 이동
- ✅ 깔끔한 폼 디자인

### 3. main.html - 메인 홈 페이지

**역할:** 서비스 허브 (빠른 메뉴)

**특징:**
- 사이드바 네비게이션 (공통)
- 사용자 정보 표시 (세션에서 불러옴)
- 6개의 메뉴 카드:
  1. AI 상담 (chat.html)
  2. 공고 목록 (list.html)
  3. 자격 조회 (준비 중)
  4. 신청 현황 (준비 중)
  5. 커뮤니티 (준비 중)
  6. 저장한 공고 (준비 중)

**구현 사항:**
- ✅ 3열 그리드 레이아웃
- ✅ 호버 애니메이션
- ✅ 사용자 정보 동적 표시
- ✅ 반응형 디자인

### 4. chat.html - AI 상담 페이지

**역할:** AI 기반 주택 상담 시뮬레이션

**특징:**
- 4개의 추천 질문 카드:
  - "청년 주택 공고를 알려줘"
  - "신혼부부 특별공급 자격 조건은?"
  - "LH 청약 신청 방법 알려줘"
  - "소득 3분위에 해당하는 주택은?"
- 실시간 채팅 인터페이스
- 사용자 메시지 + AI 응답
- 메시지 입력 및 전송

**구현 사항:**
- ✅ 추천 질문 클릭 시 자동 질문
- ✅ AI 응답 시뮬레이션 (1초 지연)
- ✅ 사용자 정보 기반 맞춤형 응답
- ✅ 스크롤 자동 이동
- ✅ 깔끔한 메시지 UI

### 5. list.html - 공고 목록 페이지

**역할:** 공공주택 공고 검색 및 목록

**특징:**
- 검색창 (키워드 검색)
- 필터:
  - 기관별 (LH, SH, GH)
  - 유형별 (청년, 신혼부부, 행복, 전세)
- 6개의 예시 공고 카드:
  - 고양삼송 청년 행복주택 (LH)
  - 강남 신혼부부 매입임대 (SH)
  - 판교 청년 전세임대 (GH)
  - 인천 검단 행복주택 (LH, 접수 예정)
  - 마포 전세임대주택 (SH)
  - 광교 신혼부부 특별공급 (LH)

**구현 사항:**
- ✅ 실시간 검색 필터링
- ✅ 기관별/유형별 필터
- ✅ 2열 그리드 레이아웃
- ✅ 접수 상태 표시 (모집 중, 접수 예정)
- ✅ 상세보기 버튼

## 🎨 CSS 구조

### base.css
- **CSS 변수:** 색상, 간격, 그림자 등
- **리셋 스타일**
- **유틸리티 클래스:** `.d-flex`, `.gap-md`, `.mt-2` 등

### layout.css
- **앱 레이아웃:** `.app-container`, `.sidebar`, `.main-content`
- **반응형:** 태블릿/모바일 대응
- **사이드바:** 네비게이션, 채팅 히스토리, 사용자 정보

### components.css
- **버튼:** `.btn`, `.btn-primary`, `.btn-gradient`
- **카드:** `.card`, `.menu-card`, `.announcement-card`
- **폼:** `.form-input`, `.form-select`
- **채팅:** `.chat-container`, `.message`
- **배지:** `.badge`, `.badge-success`

## 🎯 CSS 변수 사용법

```css
/* CSS 파일에서 */
.custom-element {
  color: var(--primary-green);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}
```

### 주요 변수

**색상:**
- `--primary-green`: #009966
- `--primary-green-light`: #00a63e
- `--zinc-900`, `--zinc-700`, `--zinc-200` (회색 계열)

**간격:**
- `--spacing-sm`: 8px
- `--spacing-md`: 16px
- `--spacing-lg`: 24px

**둥근 모서리:**
- `--radius-sm`: 8px
- `--radius-md`: 10px
- `--radius-lg`: 14px

## 🔧 JavaScript 기능

### main.js 제공 기능

1. **모바일 메뉴:** 자동 토글
2. **네비게이션 하이라이트:** 현재 페이지 표시
3. **채팅 기능:** 추천 질문 클릭, 메시지 전송
4. **검색/필터:** 디바운스 적용
5. **Django 연동:** CSRF 토큰, AJAX 예제

## 🔄 Django 통합 가이드

### 1. 파일 배치

```
your_django_project/
├── templates/
│   ├── landing.html
│   ├── user_info.html
│   ├── main.html
│   ├── chat.html
│   └── list.html
└── static/
    ├── css/
    │   ├── base.css
    │   ├── layout.css
    │   └── components.css
    └── js/
        └── main.js
```

### 2. 템플릿 변환 예시

```html
<!-- HTML 파일 상단 -->
{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <!-- ... -->
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    <link rel="stylesheet" href="{% static 'css/layout.css' %}">
    <link rel="stylesheet" href="{% static 'css/components.css' %}">
</head>

<!-- ... -->

<!-- 하단 -->
<script src="{% static 'js/main.js' %}"></script>
```

### 3. URL 변경

```html
<!-- 기존 -->
<a href="main.html">홈으로</a>

<!-- Django -->
<a href="{% url 'main' %}">홈으로</a>
```

### 4. AJAX 요청 예시

```javascript
// main.js에서 제공
fetch('/api/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')  // main.js 함수 사용
  },
  body: JSON.stringify({ message: '...' })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📱 반응형 디자인

### 브레이크포인트
- **Desktop:** > 1024px (3열 그리드)
- **Tablet:** 768px ~ 1024px (2열 그리드, 사이드바 축소)
- **Mobile:** < 768px (1열 그리드, 사이드바 숨김 + 토글)

### 모바일 대응
- 사이드바 숨김 → 햄버거 메뉴로 토글
- 그리드 1열 전환
- 터치 친화적인 버튼 크기

## 🎯 주요 기능

### ✅ 완성된 기능
- [x] 페이지 네비게이션
- [x] 반응형 레이아웃
- [x] 사이드바 토글 (모바일)
- [x] 채팅 추천 질문
- [x] 검색 입력
- [x] 필터 선택

### 🔜 Django에서 구현할 기능
- [ ] 사용자 인증
- [ ] 채팅 메시지 저장
- [ ] 공고 데이터베이스 연동
- [ ] 검색/필터 API
- [ ] 프로필 수정

## 🛠️ 커스터마이징

### 색상 변경

`css/base.css` 파일 수정:

```css
:root {
  --primary-green: #YOUR_COLOR;
  --primary-green-light: #YOUR_COLOR_LIGHT;
}
```

### 레이아웃 변경

`css/layout.css` 파일 수정:

```css
.sidebar {
  width: 280px; /* 기본 256px */
}
```

### 컴포넌트 스타일

`css/components.css` 파일에 새 컴포넌트 추가:

```css
.my-component {
  /* 스타일 */
}
```

## 📝 코드 규칙

### CSS 클래스 네이밍
- **BEM 스타일:** `.component__element--modifier`
- **시맨틱:** `.menu-card`, `.chat-message`
- **유틸리티:** `.d-flex`, `.gap-md`

### JavaScript 함수 네이밍
- **camelCase:** `initMobileMenu()`, `sendMessage()`
- **접두사:**
  - `init`: 초기화 함수
  - `show/hide`: UI 표시/숨김
  - `get/set`: 값 조회/설정

## 🐛 문제 해결

### Q: 스타일이 적용되지 않아요
**A:** CSS 파일 경로를 확인하세요.
```html
<!-- 상대 경로 -->
<link rel="stylesheet" href="css/base.css">

<!-- 로컬 서버 필요 시 -->
python -m http.server 8000
```

### Q: 사이드바가 모바일에서 안 보여요
**A:** JavaScript가 로드되었는지 확인하세요.
```html
<script src="js/main.js"></script>
```

### Q: 페이지 이동이 안 돼요
**A:** 파일 이름과 경로를 확인하세요.
```html
<a href="main.html">  <!-- ✅ 올바름 -->
<a href="index.html"> <!-- ❌ 잘못됨 -->
```

## 📊 브라우저 지원

- ✅ Chrome (최신)
- ✅ Firefox (최신)
- ✅ Safari (최신)
- ✅ Edge (최신)
- ⚠️ IE11 (일부 CSS 기능 미지원)

## 📞 Django 예제 코드

### views.py
```python
from django.shortcuts import render

def landing(request):
    return render(request, 'landing.html')

def main(request):
    return render(request, 'main.html')

def chat(request):
    return render(request, 'chat.html')

def announcement_list(request):
    # announcements = Announcement.objects.all()
    return render(request, 'list.html')

def user_info(request):
    return render(request, 'user_info.html')
```

### urls.py
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('main/', views.main, name='main'),
    path('chat/', views.chat, name='chat'),
    path('list/', views.announcement_list, name='list'),
    path('user/', views.user_info, name='user_info'),
]
```

## 🙏 감사의 말

- **Bootstrap 5.3** - UI 프레임워크
- **Google Fonts** - Noto Sans KR
- **Figma** - 디자인 원본

## 📄 라이센스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

**제작:** Figma → HTML/CSS/JavaScript 변환  
**최종 수정:** 2025년 1월  
**연락처:** GitHub Issues로 문의해주세요