```shell

# 장고 설치
pip install django

# postgres
pip install psycopg2-binary

# 환경 변수 관리용
pip install python-decouple

# 현재경로에 config 생성
django-admin startproject config .

# 현재 경로에 app 생성
python manage.py startapp web

python manage.py startapp chatbot

pip install pgvector

```

## `setting.py` 설정

```python
# .env 파일 내용 불러옴
from decouple import config # 임포트

SECRET_KEY = config('DJANGO_SECRET_KEY')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}





```

```shell

python manage.py makemigrations chatbot

python manage.py migrate chatbot
```