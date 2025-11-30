select distinct *
from (
        select alt.batch_id,
            alt.batch_seq,
            alt.annc_url,
            alt.batch_status_cd,
            alt.batch_start_dttm,
            alt.batch_end_dttm,
            alt.annc_type,
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
        where alt.batch_id = 'e4413166-2496-4f85-ac13-bac176e40ef0'
            and not exists(
                select *
                from annc_all aa
                where aa.annc_url = alt.annc_url
            )
        union all
        select alt.batch_id,
            alt.batch_seq,
            alt.annc_url,
            alt.batch_status_cd,
            alt.batch_start_dttm,
            alt.batch_end_dttm,
            alt.annc_type,
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
        where alt.annc_pblsh_dt != aa.annc_pblsh_dt
            or alt.annc_pblsh_dt != aa.annc_pblsh_dt
    ) a