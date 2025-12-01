import os
import time
import uuid
import psycopg2
from psycopg2 import extras
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from typing import Optional

# .env 파일 로드는 한번만 수행합니다.
load_dotenv()


## 🛠️ DataBaseHandler: 연결 관리 (Context Manager)
# 이 클래스는 순수하게 DB 연결, 커서 생성, 트랜잭션(커밋/롤백) 관리 역할만 담당합니다.
class DataBaseHandler:

    def __init__(self):
        # 환경 변수에서 기본값 로드 (필요하다면)
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.conn = None
        self.cursor = None

    def set_connection(self, autocommit=True):
        """커넥션 생성 및 초기화."""
        try:
            if not self.conn or self.conn.closed:
                self.conn = psycopg2.connect(
                    host=self.db_host,
                    port=self.db_port,
                    database=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                )
            self.conn.autocommit = autocommit
            # pgvector 사용 등록
            register_vector(self.conn)
            return self.conn

        except psycopg2.Error as e:
            print(f"🚨 PostgreSQL 연결 실패: {e}")
            raise  # 예외를 다시 발생시켜 with 블록이 시작되지 않도록 함

    def __enter__(self):
        """with 문 시작 시 호출됩니다. DB 연결을 열고 커서를 반환합니다."""
        # set_connection 호출 시 autocommit=True가 기본값이나, __exit__에서 commit/rollback을 위해 False로 설정합니다.
        # 기존 코드에서 autocommit=True로 설정되어 있었으므로, 그 로직을 유지하면서 트랜잭션 관리를 위해 conn.autocommit = False 설정을 제거했습니다.
        # 만약 with 블록에서 트랜잭션 관리를 원한다면 set_connection(autocommit=False)로 변경하고 __exit__의 commit/rollback을 활성화해야 합니다.
        self.set_connection(autocommit=True)
        self.cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )  # 딕셔너리 형태로 데이터를 가져오기 위해 RealDictCursor 사용 추천
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        """with 문 종료 시 호출됩니다. 커밋 또는 롤백 후 연결을 닫습니다."""
        if self.conn:
            if exc_type:
                # autocommit=True일 경우 rollback은 효과가 없지만 안전을 위해 유지
                print(f"오류 발생: {exc_value}. 롤백을 시도합니다.")
                self.conn.rollback()
            else:
                # autocommit=True일 경우 commit은 효과가 없지만 안전을 위해 유지
                try:
                    self.conn.commit()
                except Exception as e:
                    print(f"커밋 오류 발생: {e}")

            if self.cursor:
                self.cursor.close()
            # 연결을 닫습니다.
            self.conn.close()


## 🚀 ZipFitDBHandler: 비즈니스/데이터 처리 로직 전담
# 이 클래스는 테이블 정의 및 데이터 삽입/병합 등 실제 DB 작업 로직을 담당합니다.
class ZipFitDBHandler(DataBaseHandler):

    def __init__(self):
        # DataBaseHandler의 __init__을 호출하여 DB 연결 정보를 초기화합니다.
        super().__init__()

    def sample(self, batch_status, batch_id, batch_seq_list):
        self.set_connection()
        self.cursor = self.conn.cursor()

        try:
            pass
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback()  # 에러 발생 시 롤백
        finally:
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()

    # --- 테이블 생성 로직 ---
    def set_default_tables(self, drop=False, sample_data=False):
        """기본 테이블 생성 (ANNC_LH_TEMP, ANNC_ALL, ANNC_FILES, DOC_CHUNKS)"""
        try:
            # 트랜잭션 관리를 위해 autocommit=False로 연결
            self.set_connection(autocommit=False)
            self.cursor = self.conn.cursor()

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
                        FOREIGN KEY (ANNC_ID) REFERENCES ANNC_ALL (ANNC_ID)
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
                        EMBEDDING VECTOR(1024), 
                        METADATA JSONB, 
                        PRIMARY KEY (CHUNK_ID), -- FILE_ID, ANNC_ID를 포함하지 않도록 수정 (일반적인 VEC DB 패턴)
                        FOREIGN KEY (FILE_ID, ANNC_ID) REFERENCES ANNC_FILES (FILE_ID, ANNC_ID)
                    );
                    """,
                    None,  # 벡터 데이터 샘플은 복잡하여 주석 처리 유지
                ),
            ]

            print(f"drop: {drop}, sample_data: {sample_data}")

            for title, table_name, create_query, insert_query in queries_execute:
                if drop:
                    # DROP TABLE IF EXISTS ANNC_LH_TEMP; 는 너무 구체적이므로 테이블명 변수 사용
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
                    print(f"👎 table {title}-[{table_name}] dropped (CASCADE)")

                self.cursor.execute(create_query)
                print(f"✅ table {title}-[{table_name}] created")

                if sample_data and insert_query:
                    self.cursor.execute(insert_query)
                    print(f"✨ table {table_name} sample data inserted")

            self.conn.commit()  # 트랜잭션 커밋
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback()  # 에러 발생 시 롤백
        finally:
            # set_connection에서 conn이 생성되었으므로, 여기서 커서/연결을 닫습니다.
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()

    # --- 데이터 삽입/병합 로직 ---
    def bulk_merge_lh(self, data_list, batch_size=100):

        self.set_connection()
        self.cursor = self.conn.cursor()

        try:

            # print('쿼리 생성')
            # 로직 구현
            # ...
            merge_query_template = """
            merge into annc_all as target using (
                values {values_sql_placeholder}
            ) as source (
                annc_url,
                annc_type,
                annc_dtl_type,
                annc_region,
                annc_pblsh_dt,
                annc_deadline_dt,
                annc_status
            ) on (target.annc_url = source.annc_url) -- annc_url을 기준으로 일치 여부 확인
            -- 일치하는 행이 있으면 update
            when matched then
            update
            set annc_type = source.annc_type,
                annc_dtl_type = source.annc_dtl_type,
                annc_status = source.annc_status,
                annc_pblsh_dt = source.annc_pblsh_dt,
                annc_deadline_dt = source.annc_deadline_dt,
                service_status = 'PROCESSING'
                when not matched then
            insert (
                    annc_url,
                    corp_cd,
                    annc_type,
                    annc_dtl_type,
                    annc_region,
                    annc_pblsh_dt,
                    annc_deadline_dt,
                    annc_status,
                    service_status
                )
            values (
                    source.annc_url,
                    'LH',
                    source.annc_type,
                    source.annc_dtl_type,
                    source.annc_region,
                    source.annc_pblsh_dt,
                    source.annc_deadline_dt,
                    source.annc_status,
                    'PROCESSING'
                );
            """

            print("시작")
            for i in range(0, len(data_list), batch_size):
                batch_list = data_list[i : i + batch_size]

                values_to_insert = [
                    (
                        item["annc_url"],
                        item["annc_type"],
                        item["annc_dtl_type"],
                        item["annc_region"],
                        item["annc_pblsh_dt"],
                        item["annc_deadline_dt"],
                        item["annc_status"],
                    )
                    for item in batch_list
                ]

                # print(values_to_insert)

                # Psycopg를 사용하여 VALUES 구문을 안전하게 생성
                # 예: ('url1', 'LH', ...), ('url2', 'LH', ...)
                value_placeholders = (
                    "(" + ", ".join(["%s"] * len(values_to_insert[0])) + ")"
                )

                # 모든 VALUES 튜플을 합친 단일 SQL 문자열 생성
                values_sql = ", ".join([value_placeholders] * len(values_to_insert))

                # 최종 쿼리에 VALUES 구문 삽입
                final_query = merge_query_template.replace(
                    "{values_sql_placeholder}", values_sql
                )

                # 모든 청크 데이터의 값을 단일 리스트로 펼치기 (flat list)
                flat_values = [val for row in values_to_insert for val in row]

                # 쿼리 실행
                self.cursor.execute(final_query, flat_values)
                print(f"✅ {i}부터 {i + batch_size - 1}까지 {batch_size}건 MERGE 완료.")

        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback()  # 에러 발생 시 롤백
        finally:
            # set_connection에서 conn이 생성되었으므로, 여기서 커서/연결을 닫습니다.
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()

    def bulk_insert_lh_temp(self, data_list):

        is_succed = False
        new_uuid = ""

        # DataBaseHandler의 with 구문을 상속받아 사용합니다.
        # with self.conn.cursor() as self.cursor: 대신 with self.cursor: 사용 (더 간결한 사용을 위해 __enter__ / __exit__ 수정 가능)
        try:
            # set_connection(autocommit=True)를 직접 호출하여 트랜잭션 자동 커밋 모드로 연결합니다.
            self.set_connection(autocommit=True)
            self.cursor = self.conn.cursor()

            insert_query = """
                INSERT INTO ANNC_LH_TEMP (
                        BATCH_ID,
                        BATCH_SEQ,
                        ANNC_URL,
                        batch_status,
                        BATCH_START_DTTM,
                        BATCH_END_DTTM,
                        ANNC_TYPE,
                        ANNC_DTL_TYPE,
                        ANNC_REGION,
                        ANNC_PBLSH_DT,
                        ANNC_DEADLINE_DT,
                        ANNC_STATUS,
                        LH_PAN_ID,
                        LH_AIS_TP_CD,
                        LH_UPP_AIS_TP_CD,
                        LH_CCR_CNNT_SYS_DS_CD,
                        LH_LS_SST
                    )
                VALUES %s
            """

            new_uuid = str(uuid.uuid4())
            current_dttm = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime()
            )  # 시작 시간 기록을 위해 추가

            processed_data = []
            for idx, item in enumerate(data_list, 1):
                # data_list의 요소가 ANNC_URL부터 시작한다고 가정
                new_row = (
                    new_uuid,  # BATCH_ID
                    idx,  # BATCH_SEQ
                    item[0],  # ANNC_URL
                    "READY",  # batch_status (고정)
                    current_dttm,  # BATCH_START_DTTM (현재 시간)
                    None,  # BATCH_END_DTTM (NULL)
                    item[1],  # ANNC_TYPE
                    item[2],  # ANNC_DTL_TYPE
                    item[3],  # ANNC_REGION
                    item[4],  # ANNC_PBLSH_DT
                    item[5],  # ANNC_DEADLINE_DT
                    item[6],  # ANNC_STATUS
                    item[7],  # LH_PAN_ID
                    item[8],  # LH_AIS_TP_CD
                    item[9],  # LH_UPP_AIS_TP_CD
                    item[10],  # LH_CCR_CNNT_SYS_DS_CD
                    item[11],  # LH_LS_SST
                )
                processed_data.append(new_row)

            start_time = time.time()

            # extras.execute_values를 사용하여 벌크 삽입 실행
            extras.execute_values(self.cursor, insert_query, processed_data)

            # autocommit=True 이므로 conn.commit()이 필요 없지만, 명시적으로 호출해도 무방합니다.
            # self.conn.commit()

            end_time = time.time()
            print(f"✅ Psycopg2 벌크 삽입 성공! {len(data_list)}개 데이터 삽입 완료.")
            print(f"   소요 시간: {end_time - start_time:.4f} 초")

            is_succed = True

            # print(f" 완료")

        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback()  # 에러 발생 시 롤백
        finally:
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()

            return is_succed, new_uuid

    def get_lh_temp(self, uuid, status, dictionay=False):
        self.set_connection(autocommit=True)
        self.cursor = (
            self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if dictionay
            else self.conn.cursor()
        )

        sql_query = """
            select alt.batch_id,
                alt.batch_seq,
                alt.annc_url,
                alt.batch_status,
                alt.batch_start_dttm,
                alt.batch_end_dttm,
                alt.annc_type,
                alt.annc_dtl_type,
                alt.annc_region,
                alt.annc_pblsh_dt,
                alt.annc_deadline_dt,
                alt.annc_status,
                alt.lh_pan_id,
                alt.lh_ais_tp_cd,
                alt.lh_upp_ais_tp_cd,
                alt.lh_ccr_cnnt_sys_ds_cd,
                alt.lh_ls_sst
            from annc_lh_temp alt
            where alt.batch_id = %s
            and alt.batch_status = %s
        """

        self.cursor.execute(sql_query, (uuid, status))  # 👈 파라미터 바인딩

        return self.cursor.fetchall()

    def get_lh_temp_for_batch(self, uuid, dictionay=False):
        self.set_connection(autocommit=True)
        self.cursor = (
            self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if dictionay
            else self.conn.cursor()
        )

        # 1. 쿼리 내에서 변수가 들어갈 자리에 플레이스홀더(일반적으로 %s 또는 ?)를 사용합니다.
        # PostgreSQL/MySQL 등: %s 사용
        sql_query = """
            select distinct *
            from (
                select alt.batch_id,
                    alt.batch_seq,
                    alt.annc_url,
                    alt.batch_status,
                    alt.batch_start_dttm,
                    alt.batch_end_dttm,
                    alt.annc_type,
                    alt.annc_dtl_type,
                    alt.annc_region,
                    alt.annc_pblsh_dt,
                    alt.annc_deadline_dt,
                    alt.annc_status,
                    alt.lh_pan_id,
                    alt.lh_ais_tp_cd,
                    alt.lh_upp_ais_tp_cd,
                    alt.lh_ccr_cnnt_sys_ds_cd,
                    alt.lh_ls_sst
                from annc_lh_temp alt
                where alt.batch_id = %s
                    and not exists(
                        select *
                        from annc_all aa
                        where aa.annc_url = alt.annc_url
                    )
                    and alt.annc_type not in ('기타')
                union all
                select alt.batch_id,
                    alt.batch_seq,
                    alt.annc_url,
                    alt.batch_status,
                    alt.batch_start_dttm,
                    alt.batch_end_dttm,
                    alt.annc_type,
                    alt.annc_dtl_type,
                    alt.annc_region,
                    alt.annc_pblsh_dt,
                    alt.annc_deadline_dt,
                    alt.annc_status,
                    alt.lh_pan_id,
                    alt.lh_ais_tp_cd,
                    alt.lh_upp_ais_tp_cd,
                    alt.lh_ccr_cnnt_sys_ds_cd,
                    alt.lh_ls_sst
                from annc_lh_temp alt
                    join annc_all aa on alt.annc_url = aa.annc_url
                where alt.batch_id = %s
                    and (alt.annc_pblsh_dt != aa.annc_pblsh_dt
                    or alt.annc_pblsh_dt != aa.annc_pblsh_dt
                    or alt.annc_status != aa.annc_status)
                    and alt.annc_type not in ('기타')
                    
            ) a
        """

        # 2. execute()의 두 번째 인수에 튜플 형태로 변수를 전달합니다.
        # 플레이스홀더 순서대로 변수(uuid)를 나열합니다.
        self.cursor.execute(sql_query, (uuid, uuid))  # 👈 파라미터 바인딩

        return self.cursor.fetchall()

    def set_batch_status(self, batch_status, batch_id, batch_seq_list):
        self.set_connection()
        self.cursor = self.conn.cursor()

        update_query = """
            update annc_lh_temp
            set batch_status = %s
            where batch_id = %s
            and batch_seq in %s
        """

        try:


            params = (batch_status, batch_id, tuple(batch_seq_list))

            self.cursor.execute(update_query, params)

        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback()  # 에러 발생 시 롤백
        finally:
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()

    def get_annc_all(
        self,
        corp_cd,
        annc_url: Optional[str] = None,
        annc_status: Optional[str] = None,
        annc_type: Optional[str] = None,
        dictionay: Optional[bool] = False,
    ):
        self.set_connection()
        self.cursor = (
            self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if dictionay
            else self.conn.cursor()
        )

        sql_query = """
            select *
            from annc_all
            where corp_cd = %s
            and (%s IS NULL OR annc_url = %s)
            and (%s IS NULL OR annc_status = %s)
            and (%s IS NULL OR annc_type = %s)
            """

        self.cursor.execute(sql_query, (corp_cd, annc_url, annc_url, annc_status, annc_status, annc_type, annc_type))  # 👈 파라미터 바인딩

        return self.cursor.fetchall()
    

    def remove_annc_file(self, annc_id: Optional[int]|Optional[list]):
        self.set_connection()
        self.cursor = self.conn.cursor()

        update_query = """
            delete from annc_files
            where annc_id in %s
        """

        annc_id_list = (annc_id) if type(annc_id) == int else tuple(annc_id)

        try:

            params = (annc_id_list)

            self.cursor.execute(update_query, params)
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback() # 에러 발생 시 롤백
        finally:
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()


    def insert_annc_file(self, annc_files):
        self.set_connection()
        self.cursor = self.conn.cursor()

        insert_query = """
            insert into annc_files
            (
                file_id,
                annc_id,
                file_name,
                file_type,
                file_path,
                file_ext,
                file_size
            )
            values %s
        """

        try:

            extras.execute_values(self.cursor, insert_query, annc_files)
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Psycopg2 DB 에러 발생: {error}")
            if self.conn:
                self.conn.rollback() # 에러 발생 시 롤백
        finally:
            if self.conn:
                if self.cursor and not self.cursor.closed:
                    self.cursor.close()
                if not self.conn.closed:
                    self.conn.close()
