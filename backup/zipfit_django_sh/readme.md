zipfit/
│
├── manage.py
│
├── config/                        ← Django 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py                ← Tailwind CDN 모드라 추가 설정 거의 없음
│   ├── urls.py                    ← web/, chatbot/ URL 연결
│   ├── wsgi.py
│   └── asgi.py
│
├── web/                           ← 웹 화면(UI) 전용 app
│   ├── __init__.py
│   ├── urls.py                    ← home / chat / profile / announcements 등
│   ├── views.py                   ← 세션 기반 저장 + 공고 목록 + 챗 UI
│   ├── static/                    ← 이미지, JS 등 정적 파일 필요 시
│   ├── templates/
│   │   ├── base.html              ← 공통 레이아웃 (사이드바, 헤더 포함)
│   │   └── web/
│   │       ├── home.html          ← 홈 화면
│   │       ├── chat.html          ← 챗 UI (말풍선 + 즐겨찾기 포함)
│   │       ├── announcements.html ← 공고 목록 페이지
│   │       └── profile.html       ← 맞춤정보 입력(세션 저장)
│   └── tests.py
│
├── chatbot/                       ← LangGraph/LangChain API 전용 app
│   ├── __init__.py
│   ├── urls.py                    ← API endpoint /chatbot/ask/
│   ├── views.py                   ← LLM 호출
│   ├── models.py                  ← DB 저장 시 필요(지금은 비어 있어도 됨)
│   ├── migrations/
│   └── apps.py
│
└── requirements.txt
