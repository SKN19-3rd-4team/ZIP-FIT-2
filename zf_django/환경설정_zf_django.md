```shell

pip install -r requirements.txt
```

```shell

# 도커 설치
docker run -d `
-e POSTGRES_USER=zf_admin `
-e POSTGRES_PASSWORD=zf_pwd1 `
-e POSTGRES_DB=zf_db `
--name zf_db_container `
-p 5432:5432 `
pgvector/pgvector:pg17

# 도커내의 데이터 접근
docker exec -it zf_db_container psql -U zf_admin -d zf_db

# 도커 확장 설치되었는지 확인하여 없으면 설치
CREATE EXTENSION IF NOT EXISTS vector;
```

```shell
#------------------------------------------------------------
# 최초 환경 설정, github에서 소스 받은 경우 실행 할 필요 없음
#------------------------------------------------------------

# 현재경로에 config 생성
django-admin startproject config .
# 현재 경로에 app 생성
python manage.py startapp web
python manage.py startapp chatbot
```

```shell
#------------------------------------------------------------
# ✅ 필독 마이그레이션 필독 ✅
# 무조건 에러남 당황하지 말고 아래 순서대로
#------------------------------------------------------------

python manage.py migrate chatbot

#------------------------------------------------------------
# 에러 케이스 1
#------------------------------------------------------------
# psycopg2.errors.UndefinedObject: type "vector" does not exist
# LINE 1: ...T NULL, "page_num" smallint NOT NULL, "embedding" vector(153...
#------------------------------------------------------------
# 해결책
#------------------------------------------------------------
# 도커 확장 설치되었는지 확인하여 없으면 설치
CREATE EXTENSION IF NOT EXISTS vector;
#------------------------------------------------------------


#------------------------------------------------------------
# 에러 케이스 2
#------------------------------------------------------------
# psycopg2.errors.UndefinedColumn: column "fts_vector" does not exist
#------------------------------------------------------------
# 해결책
#------------------------------------------------------------
zf_django/chatbot/migrations # 로 접근

0006_add_docchunks_fts_vector_trigger.py # 파일의

# 이 부분 주석 해제 후 `python manage.py migrate chatbot` 명령어 실행
--ALTER TABLE doc_chunks
--ADD COLUMN IF NOT EXISTS fts_vector tsvector;

이후 다시 주석 처리

manage.py migrate chatbot 0007_docchunks_fts_vector --fake

python manage.py migrate chatbot

#------------------------------------------------------------



```




```shell
#------------------------------------------------------------
# 최초 환경 설정, github에서 소스 받은 경우 실행 할 필요 없음
#------------------------------------------------------------

# 장고 설치
pip install django
# postgres
pip install psycopg2-binary
# 환경 변수 관리용
pip install python-decouple
# 
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