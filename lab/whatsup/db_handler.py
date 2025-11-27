from dotenv import load_dotenv
import os
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np


load_dotenv()

class DataBaseHandler():

    def __init__(self):
        self.db_host = None
        self.db_port = None
        self.db_user = None
        self.db_password = None
        self.db_name = None
        

    def __enter__(self):
        """
        with 문 시작 시 호출됩니다. DB 연결을 열고 커서를 반환합니다.
        
        Returns:
            psycopg2.Cursor: DB 작업을 수행하는 커서 객체
        """
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_name = os.getenv('DB_NAME')

        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
        except psycopg2.Error as e:
            # 연결 실패 시 사용자에게 명확히 알림
            print(f"🚨 PostgreSQL 연결 실패: {e}") 
            # 연결 객체가 생성되지 않았으므로 conn.close() 등을 건너뛰고 바로 예외 발생
            raise # 예외를 다시 발생시켜 with 블록이 시작되지 않도록 함

        self.conn.autocommit = True
        register_vector(self.conn)
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