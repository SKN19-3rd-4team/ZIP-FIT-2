from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'change-me-in-production'
DEBUG = True

ALLOWED_HOSTS = ['*']


# -------------------
# INSTALLED_APPS
# -------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 우리의 앱들
    'web',
    'chatbot',
]


# -------------------
# Middleware
# -------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',   # ★ 세션 기반 유저정보 사용
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]


ROOT_URLCONF = 'config.urls'


# -------------------
# Templates
# -------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'web' / 'templates',  # ★ web 템플릿 폴더 연결
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'config.wsgi.application'


# -------------------
# Database (PostgreSQL + pgvector)
# -------------------
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'zf_db',
#         'USER': 'zf_admin',
#         'PASSWORD': 'zf_pwd1',
#         'HOST': 'localhost',   # Docker 컨테이너라면 '127.0.0.1' 또는 서비스명
#         'PORT': '5432',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

# pgvector 확장 사용 시, migrate 전에 수동으로 DB에서 실행:
# CREATE EXTENSION IF NOT EXISTS vector;


# -------------------
# Static Files
# -------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'web' / 'static',
]


# -------------------
# Session Settings (세션 사용자 정보 저장용)
# -------------------
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7일
SESSION_SAVE_EVERY_REQUEST = True

