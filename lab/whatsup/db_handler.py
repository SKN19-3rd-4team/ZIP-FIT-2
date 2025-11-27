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