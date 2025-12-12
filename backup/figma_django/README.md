# figma_django 프로젝트

> **figma14 프론트엔드를 Django로 변환한 프로젝트**

## 프로젝트 개요

- **원본**: `figma14/` 폴더의 HTML/CSS/JS 프로토타입
- **목표**: Django 템플릿 시스템으로 변환 및 API 연동
- **최종 목표**: `zf_django` 폴더에 병합

## 페이지 구성

1. **landing.html** - 랜딩 페이지 (데이터 연동 없음)
2. **user_info.html** - 사용자 정보 입력 (세션 저장)
3. **main.html** - 메인 대시보드 (통계 API 연동)
4. **chat.html** - AI 채팅 인터페이스 (채팅 API 연동)
5. **list.html** - 공고 목록 (공고 목록 API 연동)

## 환경 설정

### 1. 가상환경 생성

```bash
conda create -n zipfit_env python=3.12
conda activate zipfit_env
conda install -c conda-forge camelot-py
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 참고하여 `.env` 파일을 생성하세요.

```bash
# .env 파일 생성 (직접 생성 필요)
DJANGO_SECRET_KEY=your-secret-key
DB_HOST=localhost
DB_PORT=5432
DB_USER=zf_admin
DB_PASSWORD=zf_pwd1
DB_NAME=zf_db
API_BASE_URL=http://localhost:8000
```

### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 5. 개발 서버 실행

```bash
python manage.py runserver
```

## 프로젝트 구조

```
figma_django/
├── config/          # Django 프로젝트 설정
├── web/             # 웹 페이지 앱
│   ├── utils.py     # 유틸리티 함수 (사용자 ID, 세션 키 생성)
│   ├── views.py     # 뷰 함수
│   ├── urls.py      # URL 라우팅
│   └── templates/   # 템플릿 파일
└── chatbot/         # 챗봇 API 앱
```

## 기술 결정 사항

자세한 내용은 `lab/ohj/개발_시작_가이드.md` 참고

- **사용자 ID 생성**: 25개 형용사 × 25개 동물 = 625가지 조합
- **세션 키 관리**: Django 세션에 저장 (서버 측 관리)
- **채팅 추천 질문**: 하드코딩 유지
- **공고 비교 테이블**: 프론트엔드에서 처리

## 개발 단계

- [x] Phase 0: 프로젝트 기본 구조 설정
- [ ] Phase 1: 기본 구조 설정 (템플릿 폴더, base.html 등)
- [ ] Phase 2: 정적 페이지 구현
- [ ] Phase 3: API 연동 (Mock 데이터)
- [ ] Phase 4: 실제 API 연동
- [ ] Phase 5: 고급 기능

## 참고 문서

- `lab/ohj/개발_시작_가이드.md` - 개발 가이드
- `lab/ohj/환경설정_체크리스트.md` - 환경 설정 체크리스트
- `lab/ohj/20251210_dev_01.txt` - 원본 요구사항 문서

