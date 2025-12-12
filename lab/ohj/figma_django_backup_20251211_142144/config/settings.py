"""
Django settings for figma_django project.

Generated based on zipfit_django structure.
"""
from pathlib import Path
from decouple import Config, RepositoryEnv  # 환경 변수 관리

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent  # ZIP-FIT-2 루트

# -------------------
# Environment Variables (.env 파일 위치 선택)
# -------------------
# 옵션 1: Root의 .env 파일 사용 (팀원 협의 필요)
root_env_file = PROJECT_ROOT / '.env'
project_env_file = BASE_DIR / '.env'

if root_env_file.exists():
    # Root의 .env 파일이 있으면 사용
    config = Config(RepositoryEnv(str(root_env_file)))
elif project_env_file.exists():
    # 프로젝트 내 .env 파일 사용
    config = Config(RepositoryEnv(str(project_env_file)))
else:
    # .env 파일이 없을 경우 기본값 사용
    from decouple import config

# 옵션 2: 프로젝트 내 .env 파일만 사용하려면 아래 주석 해제
# from decouple import config

# -------------------
# Security Settings
# -------------------
try:
    SECRET_KEY = config('DJANGO_SECRET_KEY')
except:
    # .env 파일이 없을 경우 기본값 (개발용)
    SECRET_KEY = 'django-insecure-dev-key-change-in-production'
    print("⚠️  Warning: .env file not found. Using default SECRET_KEY.")

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
    'django.contrib.postgres',  # PostgreSQL 확장

    # REST Framework
    'rest_framework',
    'drf_spectacular',  # API 문서화

    # 우리의 앱들
    'web',
    'chatbot',
    
    # zf_django 앱 추가 (모델 사용을 위해)
    # zf_django의 chatbot 앱을 사용하여 AnncAll 모델 접근
    # 주의: zf_django.chatbot이 INSTALLED_APPS에 있어야 Django가 모델을 인식함
    # 하지만 zf_django는 별도 프로젝트이므로, sys.path를 통해 모델을 직접 사용
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
# Database
# -------------------
# PostgreSQL 사용 (zf_django와 동일한 데이터베이스 사용)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# pgvector 확장 사용 시, migrate 전에 수동으로 DB에서 실행:
# CREATE EXTENSION IF NOT EXISTS vector;

# -------------------
# Password Validation
# -------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# -------------------
# Internationalization
# -------------------
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

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

# -------------------
# REST Framework Settings
# -------------------
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ZIPFIT API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# -------------------
# API Settings
# -------------------
try:
    API_BASE_URL = config('API_BASE_URL', default='http://localhost:8000')
except:
    API_BASE_URL = 'http://localhost:8000'

