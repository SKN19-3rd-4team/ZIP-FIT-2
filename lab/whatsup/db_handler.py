from dotenv import load_dotenv
import os, time
import psycopg2
from psycopg2 import extras
from pgvector.psycopg2 import register_vector
import numpy as np
import uuid



load_dotenv()

class DataBaseHandler():

    def __init__(self):
        self.db_host = None
        self.db_port = None
        self.db_user = None
        self.db_password = None
        self.db_name = None
        self.conn = None

    def set_connection(self, autocommit=True):
        """
        커넥션 생성
        """
        self.db_host = self.db_host if self.db_host else os.getenv('DB_HOST')
        self.db_port = self.db_port if self.db_port else os.getenv('DB_PORT')
        self.db_user = self.db_user if self.db_user else os.getenv('DB_USER')
        self.db_password = self.db_password if self.db_password else os.getenv('DB_PASSWORD')
        self.db_name = self.db_name if self.db_name else os.getenv('DB_NAME')

        try:
            if not self.conn:
                self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            self.conn.autocommit = True
            register_vector(self.conn)

        except psycopg2.Error as e:
            # 연결 실패 시 사용자에게 명확히 알림
            print(f"🚨 PostgreSQL 연결 실패: {e}") 
            # 연결 객체가 생성되지 않았으므로 conn.close() 등을 건너뛰고 바로 예외 발생
            raise # 예외를 다시 발생시켜 with 블록이 시작되지 않도록 함


    def set_default_tables(self, drop=False, sample_data=False):
        try:
            self.set_connection(False)
            self.cursor = self.conn.cursor()


            queries_execute = []

            queries_execute.append(
                (
                    "LH 공고 크롤링 배치",
                    "ANNC_LH_TEMP",
                    """
                    CREATE TABLE IF NOT EXISTS ANNC_LH_TEMP (
                        BATCH_ID UUID NOT NULL,               -- 배치 ID (UUID 타입)
                        BATCH_SEQ INT NOT NULL,               -- 배치 SEQ
                        ANNC_URL TEXT,                        -- 공고 URL (TEXT 타입)
                        BATCH_STATUS_CD VARCHAR(10),          -- 배치 상태 코드 (VARCHAR(10))
                        BATCH_START_DTTM TIMESTAMPTZ,         -- 배치 등록 시간 (TIMESTAMPTZ 타입, 시간대 포함)
                        BATCH_END_DTTM TIMESTAMPTZ,           -- 배치 완료 시간 (TIMESTAMPTZ 타입, 시간대 포함)
                        ANNC_TYPE VARCHAR(50),                -- 공고 유형 (VARCHAR(50))
                        ANNC_REGION VARCHAR(50),              -- 지역 (VARCHAR(50))
                        ANNC_PBLSH_DT VARCHAR(50),            -- 게시일 (VARCHAR(50))
                        ANNC_DEADLINE_DT VARCHAR(50),         -- 마감일 (VARCHAR(50))
                        ANNC_STATUS VARCHAR(20),              -- 공고 상태 (VARCHAR(20))
                        LH_PAN_ID VARCHAR(50),                -- 공고 식별 ID (VARCHAR(50))
                        LH_AIS_TP_CD VARCHAR(10),             -- 공고 유형 코드 (VARCHAR(10))
                        LH_UPP_AIS_TP_CD VARCHAR(10),         -- 상위 공고 유형 코드 (VARCHAR(10))
                        LH_CCR_CNNT_SYS_DS_CD VARCHAR(10),    -- 연계 시스템 구분 코드 (VARCHAR(10))
                        LH_LS_SST VARCHAR(50),                -- 목록 상의 상태/순서 (VARCHAR(50)),
                        PRIMARY KEY (BATCH_ID, BATCH_SEQ)     -- 기본 키: BATCH_ID와 BATCH_SEQ의 복합 키
                    );
                    """,
                    None
                )
            )

            queries_execute.append(
                (
                    "공고 전체 테이블",
                    "ANNC_ALL",
                    """
                    CREATE TABLE IF NOT EXISTS ANNC_ALL (
                        ANNC_ID BIGSERIAL PRIMARY KEY,      -- 공고 ID (BIGSERIAL, 기본 키)
                        ANNC_URL TEXT,                      -- 공고 URL (TEXT)
                        CORP_CD VARCHAR(10),                -- 공사 코드 (VARCHAR(10))
                        ANNC_TYPE VARCHAR(50),              -- 공고 유형 (VARCHAR(50))
                        ANNC_REGION VARCHAR(50),            -- 지역 (VARCHAR(50))
                        ANNC_PBLSH_DT VARCHAR(50),          -- 게시일 (VARCHAR(50))
                        ANNC_DEADLINE_DT VARCHAR(50),       -- 마감일 (VARCHAR(50))
                        ANNC_STATUS VARCHAR(20),            -- 공고 상태 (VARCHAR(20))
                        SERVICE_STATUS VARCHAR(20)          -- 서비스 상태 (VARCHAR(20))
                    );
                    """,                    
                    """
                    INSERT INTO ANNC_ALL (
                        ANNC_URL, CORP_CD, ANNC_TYPE, ANNC_REGION, ANNC_PBLSH_DT, ANNC_DEADLINE_DT, ANNC_STATUS, SERVICE_STATUS
                    ) VALUES (
                        'http://annc.co.kr/1001', 'LH', '주택공급', '전국', '2025-11-01', '2025-12-31', '진행중', 'Y'
                    );
                    """
                )
            )


            queries_execute.append(
                (
                    "공고 파일",
                    "ANNC_FILES",
                    """
                    CREATE TABLE IF NOT EXISTS ANNC_FILES (
                        FILE_ID BIGSERIAL,                  -- 공고 파일 ID (BIGSERIAL)
                        ANNC_ID BIGSERIAL,                  -- 공고 ID (BIGSERIAL, ANNC_ALL 참조)
                        FILE_NAME VARCHAR(500),             -- 공고 파일명 (VARCHAR(500))
                        FILE_TYPE VARCHAR(10),              -- 공고 파일 유형 (VARCHAR(10))
                        FILE_PATH VARCHAR(2000),            -- 공고 파일 경로 (VARCHAR(2000))
                        FILE_EXT VARCHAR(10),               -- 공고 파일 확장자 (VARCHAR(10))
                        FILE_SIZE INT,                      -- 공고 파일 사이즈 (INT)
                        IS_VECTORIZED BOOLEAN,              -- 임베딩 완료 (BOOLEAN)
                        PRIMARY KEY (FILE_ID, ANNC_ID),     -- 복합 기본 키
                        FOREIGN KEY (ANNC_ID) REFERENCES ANNC_ALL (ANNC_ID)
                    );
                    """,
                    """
                    INSERT INTO ANNC_FILES (
                        ANNC_ID, FILE_NAME, FILE_TYPE, FILE_PATH, FILE_EXT, FILE_SIZE, IS_VECTORIZED
                    ) VALUES (
                        1, -- ANNC_ALL 테이블에 삽입된 공고의 ID (예: 1)
                        '2025년 주택공급 공고문.pdf', '공고', '/data/annc/1/file.pdf', 'pdf', 102400, FALSE
                    );
                    """
                )
            )


            queries_execute.append(
                (
                    "공고 파일 청크 벡터",
                    "DOC_CHUNKS",
                    """
                    CREATE TABLE IF NOT EXISTS DOC_CHUNKS (
                        CHUNK_ID BIGSERIAL,                 -- 청크 ID (BIGSERIAL)
                        FILE_ID BIGSERIAL,                  -- 공고 파일 ID (BIGSERIAL, ANNC_FILES 참조)
                        ANNC_ID BIGSERIAL,                  -- 공고 ID (BIGSERIAL, ANNC_FILES 참조)
                        CHUNK_TEXT TEXT,                    -- 청크 텍스트 (TEXT)
                        PAGE_NUM SMALLINT,                  -- 페이지 번호 (SMALLINT)
                        EMBEDDING VECTOR(1024),             -- 임베딩 벡터 (VECTOR(1024))
                        METADATA JSONB,                     -- 메타데이터 (JSONB)
                        PRIMARY KEY (CHUNK_ID, FILE_ID, ANNC_ID), -- 복합 기본 키
                        FOREIGN KEY (FILE_ID, ANNC_ID) REFERENCES ANNC_FILES (FILE_ID, ANNC_ID)
                    );
                    """,
                    None
                    # """
                    # INSERT INTO DOC_CHUNKS (
                    #     FILE_ID, ANNC_ID, CHUNK_TEXT, PAGE_NUM, EMBEDDING, METADATA
                    # ) VALUES (
                    #     1, -- ANNC_FILES 테이블에 삽입된 파일 ID (예: 1)
                    #     1, -- ANNC_ALL 테이블에 삽입된 공고 ID (예: 1)
                    #     '청크 1: 주택 공급에 대한 자세한 규정은 다음과 같습니다.',
                    #     1,
                    #     '[0.1, 0.2, 0.3, ..., 0.9, 1.0]', -- 1024차원 벡터의 간략한 예시
                    #     '{"source": "paragraph_1", "category": "rule"}'::jsonb
                    # );
                    # """
                )
            )

            print(f'drop: {drop}, sample_data: {sample_data}')

            for title, table_name, create_query, insert_query in queries_execute:
                if drop:
                    self.cursor.execute(f"DROP TABLE IF EXISTS ANNC_LH_TEMP;")
                    print(f"👎 table {title}-[{table_name}] dropped")
                
                self.cursor.execute(create_query)
                print(f"✅ table {title}-[{table_name}] created")

                if sample_data and insert_query:
                    self.cursor.execute(insert_query)


            self.conn.commit()
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback() # 에러 발생 시 롤백
        finally:
            if self.conn:
                self.cursor.close()
                self.conn.close() 

    def bulk_merge_lh(self, data_list, batch_size=100):
        ...
    
    def bulk_insert_lh_temp(self, data_list):

        is_succed = False
        new_uuid = ""

        try:
            self.set_connection()
            self.cursor = self.conn.cursor()

            insert_query = """
                INSERT INTO ANNC_LH_TEMP (BATCH_ID, BATCH_SEQ, ANNC_URL, BATCH_STATUS_CD, BATCH_START_DTTM, BATCH_END_DTTM, ANNC_TYPE, ANNC_REGION, ANNC_PBLSH_DT, ANNC_DEADLINE_DT, ANNC_STATUS, LH_PAN_ID, LH_AIS_TP_CD, LH_UPP_AIS_TP_CD, LH_CCR_CNNT_SYS_DS_CD, LH_LS_SST)
                VALUES %s
            """

            new_uuid = str(uuid.uuid4())

            data_list = [
                (new_uuid, idx, *item)
                for idx, item in enumerate(data_list, 1)
            ]

            processed_data = []
            for item in data_list:
                new_row = (
                    item[0],  # BATCH_ID
                    item[1],  # BATCH_SEQ
                    item[2],  # ANNC_URL
                    'READY',  # BATCH_STATUS_CD (고정)
                    None,     # BATCH_START_DTTM (고정)
                    None,     # BATCH_END_DTTM (고정 - NULL)
                    item[3],  # ANNC_TYPE
                    item[4],  # ANNC_REGION
                    item[5],  # ANNC_PBLSH_DT
                    item[6],  # ANNC_DEADLINE_DT
                    item[7],  # ANNC_STATUS
                    item[8],  # LH_PAN_ID
                    item[9],  # LH_AIS_TP_CD
                    item[10], # LH_UPP_AIS_TP_CD
                    item[11], # LH_CCR_CNNT_SYS_DS_CD
                    item[12]  # LH_LS_SST
                )
                processed_data.append(new_row)

            start_time = time.time()
        
            # 3. execute_many()를 사용하여 벌크 삽입 실행
            # 이 함수가 내부적으로 네트워크 왕복 횟수를 최소화하여 빠르게 처리합니다.
            extras.execute_values(self.cursor, insert_query, processed_data)
            
            # 4. 트랜잭션 커밋
            self.conn.commit()
            
            end_time = time.time()
            print(f"✅ Psycopg2 벌크 삽입 성공! {len(data_list)}개 데이터 삽입 완료.")
            print(f"   소요 시간: {end_time - start_time:.4f} 초")

            is_succed = True

        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback() # 에러 발생 시 롤백
        finally:
            if self.conn:
                self.cursor.close()
                self.conn.close()
            return is_succed, new_uuid



    def __enter__(self):
        """
        with 문 시작 시 호출됩니다. DB 연결을 열고 커서를 반환합니다.
        
        Returns:
            psycopg2.Cursor: DB 작업을 수행하는 커서 객체
        """

        self.set_connection()
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        with 문 종료 시 호출됩니다. 커밋 또는 롤백 후 연결을 닫습니다.
        Args:
        exc_type, exc_value, traceback: 발생한 예외 정보
        """
        if exc_type:
            print(f"오류 발생: {exc_value}. 롤백을 수행합니다.")
            self.conn.rollback()
        else:
            # 오류가 없으면 변경 사항을 커밋합니다.
            self.conn.commit()

        # 연결을 닫습니다.
        if self.conn:
            self.conn.close()

class DatabaseExecuteSamples:
    """
    DataBaseHandler를 사용하여 PostgreSQL에서 CRUD 및 JOIN 작업을 수행하는
    샘플 메서드를 모아 놓은 클래스입니다.
    """

    def create_tables(self):
        """문서 및 작성자 테이블을 생성합니다."""
        print("--- 1. 테이블 생성 시작 ---")
        try:
            with DataBaseHandler() as cursor:
                # authors 테이블 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS authors (
                        author_id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE
                    );
                """)

                # documents 테이블 생성 (pgvector의 vector(3) 타입 사용)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        doc_id SERIAL PRIMARY KEY,
                        author_id INTEGER REFERENCES authors(author_id),
                        title VARCHAR(255) NOT NULL,
                        content TEXT,
                        vector vector(3) 
                    );
                """)
                print("테이블 'authors' 및 'documents' 생성 완료.")
        except Exception as e:
            print(f"테이블 생성 오류: {e}")

    # ---

    def insert_data(self):
        """샘플 데이터를 삽입하고 벡터를 저장합니다."""
        print("\n--- 2. 데이터 삽입 시작 ---")
        # 예시 벡터 데이터 (차원은 3으로 가정)
        vector_data_1 = np.array([0.1, 0.2, 0.3])
        vector_data_2 = np.array([0.4, 0.5, 0.6])

        try:
            with DataBaseHandler() as cursor:
                # 작성자 데이터 삽입
                cursor.execute(
                    "INSERT INTO authors (name, email) VALUES (%s, %s) RETURNING author_id;",
                    ('김지수', 'jisoo@example.com')
                )
                # 삽입된 author_id를 가져옴
                author_id_1 = cursor.fetchone()[0] 

                cursor.execute(
                    "INSERT INTO authors (name, email) VALUES (%s, %s) RETURNING author_id;",
                    ('박현우', 'hyeonwoo@example.com')
                )
                author_id_2 = cursor.fetchone()[0]
                
                # 문서 데이터 삽입 (벡터 데이터 포함)
                cursor.execute(
                    "INSERT INTO documents (author_id, title, content, vector) VALUES (%s, %s, %s, %s);",
                    (author_id_1, '파이썬 Context Manager', 'DB 연결 관리의 효율성', vector_data_1)
                )
                cursor.execute(
                    "INSERT INTO documents (author_id, title, content, vector) VALUES (%s, %s, %s, %s);",
                    (author_id_2, '벡터 검색 개요', 'pgvector의 작동 방식에 대한 설명', vector_data_2)
                )
                print(f"작성자 2명 및 문서 2개 삽입 완료.")
        except Exception as e:
            print(f"데이터 삽입 오류: {e}")
            
    # ---

    def select_query(self, doc_title):
        """특정 제목의 문서를 조회합니다."""
        print(f"\n--- 3. SELECT 쿼리: '{doc_title}' ---")
        try:
            with DataBaseHandler() as cursor:
                cursor.execute(
                    "SELECT doc_id, title, content FROM documents WHERE title = %s;",
                    (doc_title,)
                )
                result = cursor.fetchone()
                if result:
                    print(f"조회 결과: ID={result[0]}, 제목={result[1]}, 내용={result[2]}")
                else:
                    print(f"'{doc_title}' 문서를 찾을 수 없습니다.")
        except Exception as e:
            print(f"조회 오류: {e}")

    # ---

    def join_query(self):
        """JOIN 쿼리로 문서와 작성자 정보를 함께 조회합니다."""
        print("\n--- 4. JOIN 쿼리 (문서 + 작성자) ---")
        try:
            with DataBaseHandler() as cursor:
                cursor.execute("""
                    SELECT 
                        d.title, 
                        a.name AS author_name,
                        a.email 
                    FROM documents d
                    JOIN authors a ON d.author_id = a.author_id;
                """)
                
                results = cursor.fetchall()
                for row in results:
                    print(f"제목: {row[0]}, 작성자: {row[1]}, 이메일: {row[2]}")
        except Exception as e:
            print(f"JOIN 쿼리 오류: {e}")

    # ---

    def update_query(self, doc_title, new_content):
        """특정 문서의 내용을 수정합니다."""
        print(f"\n--- 5. UPDATE 쿼리: '{doc_title}' ---")
        try:
            with DataBaseHandler() as cursor:
                cursor.execute(
                    "UPDATE documents SET content = %s WHERE title = %s;",
                    (new_content, doc_title)
                )
                print(f"'{doc_title}' 문서 내용이 '{new_content}'로 수정되었습니다.")
        except Exception as e:
            print(f"업데이트 오류: {e}")

    # ---

    def delete_query(self, doc_title):
        """특정 제목의 문서를 삭제합니다."""
        print(f"\n--- 6. DELETE 쿼리: '{doc_title}' ---")
        try:
            with DataBaseHandler() as cursor:
                cursor.execute(
                    "DELETE FROM documents WHERE title = %s;",
                    (doc_title,)
                )
                print(f"'{doc_title}' 문서가 삭제되었습니다.")
        except Exception as e:
            print(f"삭제 오류: {e}")

    # ---

    def drop_tables(self):
        """예제 테이블을 모두 삭제합니다."""
        print("\n--- 7. 테이블 삭제 시작 ---")
        try:
            with DataBaseHandler() as cursor:
                # 외래 키 제약 조건 때문에 documents를 먼저 삭제
                cursor.execute("DROP TABLE IF EXISTS documents;")
                cursor.execute("DROP TABLE IF EXISTS authors;")
                print("테이블 'documents' 및 'authors' 삭제 완료.")
        except Exception as e:
            print(f"테이블 삭제 오류: {e}")