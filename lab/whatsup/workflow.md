## postgre sql 설치

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

## anaconda 환경 설치

```shell
conda create -n zf2_back python=3.12

pip install psycopg2-binary pgvector
```