import datetime
from psycopg2 import extras
from typing import List, Dict, Any, Optional

# 상위 모듈에서 DataBaseHandler Base 클래스를 임`포트
# (from ..db_handler import DataBaseHandler 도 가능하지만, 
#  현재 __init__.py 설정을 고려하여 from database import DataBaseHandler로 가정)
from database.db_handler import DataBaseHandler 


class AnncQrRepository(DataBaseHandler):
    TABLE_NAME_LH_TEMP = "annc_lh_temp"
    TABLE_NAME_ANNC_ALL = "annc_all"
    COLUMNS_LH_TEMP = [
        'annc_id','annc_url',
        'corp_cd',
        'annc_type','annc_dtl_type',
        'annc_pblsh_dt','annc_deadline_dt',
        'annc_status','service_status'
    ]
    COLUMNS_ANNC_ALL = [
        "batch_id", "batch_seq", "annc_url", "batch_status", "batch_start_dttm", 
        "annc_type", "annc_dtl_type", "annc_region",
        "annc_pblsh_dt", "annc_deadline_dt",
        "annc_status", "lh_pan_id", "lh_ais_tp_cd", 
        "lh_upp_ais_tp_cd", "lh_ccr_cnnt_sys_ds_cd", "lh_ls_sst"
    ]

    def __init__(self):
        super().__init__()

    def get_announcements_merge_target(self, batch_id: str, annc_type_list: tuple|list=('임대','분양'), annc_status: Optional[str]=None):


        try:
            with self as db:

                return_columns = ','.join(['alt.' + col_name for col_name in self.COLUMNS_ANNC_ALL])

                sql_query = f"""
                    select distinct *
                    from (
                        select {return_columns}
                        from {self.TABLE_NAME_LH_TEMP} alt
                        where alt.batch_id = %s
                            and not exists(
                                select *
                                from {self.TABLE_NAME_ANNC_ALL} aa
                                where aa.annc_url = alt.annc_url
                            )
                            and alt.annc_type in %s
                            and (%s is null or alt.annc_status = %s)
                        union all
                        select {return_columns}
                        from {self.TABLE_NAME_LH_TEMP} alt
                            join {self.TABLE_NAME_ANNC_ALL} aa on alt.annc_url = aa.annc_url
                        where alt.batch_id = %s
                            and (alt.annc_pblsh_dt != aa.annc_pblsh_dt
                            or alt.annc_deadline_dt != aa.annc_deadline_dt
                            or alt.annc_status != aa.annc_status)
                            and alt.annc_type in %s
                            and (%s is null or alt.annc_status = %s)
                            
                    ) a
                    order by batch_seq asc;
                """
                params = (
                    batch_id, tuple(annc_type_list), annc_status, annc_status,
                    batch_id, tuple(annc_type_list), annc_status, annc_status
                )


                return db.execute_query(sql_query, params, fetch_one=False)
        except Exception as e:
            print(f"공고 조회 실패: {e}")
            raise

        

        