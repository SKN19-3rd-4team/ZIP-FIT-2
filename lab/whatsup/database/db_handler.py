import os
import psycopg2
from psycopg2 import extras, OperationalError
from pgvector.psycopg2 import register_vector
from typing import Optional, List, Dict, Any

# load_dotenv() 는 클래스 외부에서 실행되었다고 가정

class DataBaseHandler():
    """
    PostgreSQL 데이터베이스 연결을 관리하고 쿼리 실행을 위한 Context Manager를 제공
    """

    def __init__(self):
        # 환경 변수에서 DB 정보 로드
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT", "5432") # 기본값 설정
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.conn = None

    def __enter__(self):
        """Context Manager 시작 시 연결 설정"""
        self.make_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context Manager 종료 시 자원 정리 및 트랜잭션 처리"""
        if self.conn:
            if exc_type is None:
                # 예외가 없으면 커밋
                self.conn.commit()
            else:
                # 예외가 발생하면 롤백
                self.conn.rollback()
                # 예외를 다시 발생시켜 상위 호출자에게 알림
                raise exc_val
            
            self.conn.close()
            self.conn = None
        
    def make_connection(self):
        """DB 연결을 생성하고 pgvector를 등록"""
        if self.conn and not self.conn.closed:
            return self.conn

        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
            )
            # pgvector를 등록
            register_vector(self.conn)
            
        except psycopg2.Error as e:
            # 연결 실패 시 명확하게 오류 발생
            print(f"DB 연결 실패: {e}")
            raise OperationalError(f"데이터베이스 연결 오류: {e}")

    def execute_query(self, query: str, params: Optional[tuple] = None, fetch_one: bool = False) -> List[Dict[str, Any]]:
        """
        쿼리를 실행하고 결과를 반환합니다.
        DML/DDL (fetch_one=False) 및 SELECT (fetch_one=True/False) 모두 사용 가능.
        """
        # Context Manager의 __enter__가 호출되었다고 가정 (self.conn이 존재)
        if not self.conn or self.conn.closed:
            raise OperationalError("연결이 닫혀있거나 초기화되지 않았습니다. 'with' 구문을 사용하세요.")

        try:
            # DictCursor를 사용하여 결과를 딕셔너리로 받음
            with self.conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(query, params)
                
                # SELECT 쿼리인 경우 결과 반환
                if cur.description: 
                    if fetch_one:
                        result = cur.fetchone()
                        return [dict(result)] if result else []
                    else:
                        return [dict(row) for row in cur.fetchall()]
                
                # DML/DDL (INSERT, UPDATE 등)의 경우 변경된 row 수 반환
                else:
                    print(f"쿼리 실행 완료. 영향 받은 행 수: {cur.rowcount}")
                    return []

        except psycopg2.Error as e:
            # 쿼리 실행 중 오류가 나면 롤백은 __exit__이 처리
            print(f"쿼리 실행 오류: {e}")
            raise

    def set_default_tables(self, drop=False, sample_data=False):
        """기본 테이블 생성 (ANNC_LH_TEMP, ANNC_ALL, ANNC_FILES, DOC_CHUNKS)"""

        queries_execute = [
            # (설명, 테이블명, CREATE 쿼리, INSERT 쿼리)
            (
                "LH 공고 크롤링 배치",
                "ANNC_LH_TEMP",
                """
                CREATE TABLE IF NOT EXISTS ANNC_LH_TEMP (
                    BATCH_ID UUID NOT NULL, 
                    BATCH_SEQ INT NOT NULL, 
                    ANNC_URL TEXT, 
                    batch_status VARCHAR(10), 
                    BATCH_START_DTTM TIMESTAMPTZ, 
                    BATCH_END_DTTM TIMESTAMPTZ, 
                    ANNC_TYPE VARCHAR(50), 
                    ANNC_DTL_TYPE VARCHAR(20), 
                    ANNC_REGION VARCHAR(50), 
                    ANNC_PBLSH_DT VARCHAR(50), 
                    ANNC_DEADLINE_DT VARCHAR(50), 
                    ANNC_STATUS VARCHAR(20), 
                    LH_PAN_ID VARCHAR(50), 
                    LH_AIS_TP_CD VARCHAR(10), 
                    LH_UPP_AIS_TP_CD VARCHAR(10), 
                    LH_CCR_CNNT_SYS_DS_CD VARCHAR(10), 
                    LH_LS_SST VARCHAR(50), 
                    PRIMARY KEY (BATCH_ID, BATCH_SEQ)
                );
                """,
                None,
            ),
            (
                "공고 전체 테이블",
                "ANNC_ALL",
                """
                CREATE TABLE IF NOT EXISTS ANNC_ALL (
                    ANNC_ID BIGSERIAL PRIMARY KEY, 
                    ANNC_URL TEXT UNIQUE, 
                    CORP_CD VARCHAR(10), 
                    ANNC_TYPE VARCHAR(50), 
                    ANNC_DTL_TYPE VARCHAR(20), 
                    ANNC_REGION VARCHAR(50), 
                    ANNC_PBLSH_DT VARCHAR(50), 
                    ANNC_DEADLINE_DT VARCHAR(50), 
                    ANNC_STATUS VARCHAR(20), 
                    SERVICE_STATUS VARCHAR(20)
                );
                """,
                """
                INSERT INTO ANNC_ALL (
                        ANNC_URL,
                        CORP_CD,
                        ANNC_TYPE,
                        ANNC_DTL_TYPE,
                        ANNC_REGION,
                        ANNC_PBLSH_DT,
                        ANNC_DEADLINE_DT,
                        ANNC_STATUS,
                        SERVICE_STATUS
                    )
                VALUES (
                        'http://annc.co.kr/1001',
                        'LH',
                        '주택공급',
                        '임대',
                        '전국',
                        '2025-11-01',
                        '2025-12-31',
                        '진행중',
                        'Y'
                    ) ON CONFLICT (ANNC_URL) DO NOTHING;
                """,  # 중복 삽입 방지를 위해 ON CONFLICT 추가
            ),
            (
                "공고 파일",
                "ANNC_FILES",
                """
                CREATE TABLE IF NOT EXISTS ANNC_FILES (
                    FILE_ID BIGSERIAL, 
                    ANNC_ID BIGSERIAL, 
                    FILE_NAME VARCHAR(500), 
                    FILE_TYPE VARCHAR(10), 
                    FILE_PATH VARCHAR(2000) UNIQUE, 
                    FILE_EXT VARCHAR(10), 
                    FILE_SIZE INT, 
                    PRIMARY KEY (FILE_ID, ANNC_ID), 
                    FOREIGN KEY (ANNC_ID) REFERENCES ANNC_ALL (ANNC_ID) ON DELETE CASCADE
                );
                """,
                """
                INSERT INTO ANNC_FILES (
                        ANNC_ID,
                        FILE_NAME,
                        FILE_TYPE,
                        FILE_PATH,
                        FILE_EXT,
                        FILE_SIZE
                    )
                VALUES (
                        (SELECT ANNC_ID FROM ANNC_ALL WHERE ANNC_URL = 'http://annc.co.kr/1001'),
                        '2025년 주택공급 공고문.pdf',
                        '공고',
                        '/data/annc/1/file.pdf',
                        'pdf',
                        102400
                    ) ON CONFLICT (FILE_PATH) DO NOTHING;
                """,  # ANNC_ID를 조회하여 삽입하는 방식으로 변경, 중복 삽입 방지를 위해 ON CONFLICT 추가
            ),
            (
                "공고 파일 청크 벡터",
                "DOC_CHUNKS",
                """
                CREATE TABLE IF NOT EXISTS DOC_CHUNKS (
                    CHUNK_ID BIGSERIAL, 
                    FILE_ID BIGSERIAL, 
                    ANNC_ID BIGSERIAL, 
                    CHUNK_TEXT TEXT, 
                    PAGE_NUM SMALLINT, 
                    EMBEDDING VECTOR(1536), 
                    METADATA JSONB, 
                    PRIMARY KEY (CHUNK_ID), -- FILE_ID, ANNC_ID를 포함하지 않도록 수정 (일반적인 VEC DB 패턴)
                    FOREIGN KEY (FILE_ID, ANNC_ID) REFERENCES ANNC_FILES (FILE_ID, ANNC_ID) ON DELETE CASCADE
                );
                """,
                None,  # 벡터 데이터 샘플은 복잡하여 주석 처리 유지
            ),
        ]

        try:
            with self as db:
                with db.conn.cursor() as cur:                
                    for title, table_name, create_query, insert_query in queries_execute:
                        
                        if drop:
                            # DROP TABLE IF EXISTS ANNC_LH_TEMP; 는 너무 구체적이므로 테이블명 변수 사용
                            cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                            print(f"👎 table {title}-[{table_name}] dropped (CASCADE)")

                        cur.execute(create_query)
                        print(f"✅ table {title}-[{table_name}] created")

                        if sample_data and insert_query:
                            cur.execute(insert_query)
                            print(f"✨ table {table_name} sample data inserted")

            

        except Exception as e:
            print(f"테이블 생성 실패: {e}")
            raise

            