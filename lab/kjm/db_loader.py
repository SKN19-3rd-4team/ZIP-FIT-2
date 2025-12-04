"""DB 로더 - CSV 메타데이터 및 청크 적재"""
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from config import LEASE_CORE_CSV, LEASE_META_CSV, SALE_CORE_CSV, SALE_META_CSV
from db_handler import DBHandler, insert_announcement, insert_chunks
from chunker import Chunk


def parse_date(date_str: str) -> Optional[datetime]:
    """날짜 파싱"""
    if not date_str or pd.isna(date_str):
        return None
    for fmt in ['%Y-%m-%d', '%Y.%m.%d', '%Y/%m/%d', '%Y%m%d']:
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except ValueError:
            continue
    return None


def load_csv_metadata() -> Dict[str, Dict]:
    """CSV에서 공고 메타데이터 로드"""
    metadata = {}

    # 임대
    if LEASE_META_CSV.exists():
        for _, row in pd.read_csv(LEASE_META_CSV).iterrows():
            ext_id = str(row.get('ID', ''))  # 이미 LH_lease_xxx 형식
            metadata[ext_id] = {
                'title': row.get('공고명', ''), 'category': '임대', 'region': row.get('지역', ''),
                'notice_type': row.get('유형', ''), 'posted_date': parse_date(row.get('게시일', '')),
                'deadline': parse_date(row.get('마감일', '')), 'status': row.get('상태', ''), 'url': row.get('URL', '')
            }
    if LEASE_CORE_CSV.exists():
        for _, row in pd.read_csv(LEASE_CORE_CSV).iterrows():
            ext_id = str(row.get('ID', ''))  # 이미 LH_lease_xxx 형식
            if ext_id in metadata:
                metadata[ext_id]['file_name'] = row.get('파일명', '')
            else:
                metadata[ext_id] = {'title': row.get('파일명', ''), 'category': '임대', 'file_name': row.get('파일명', '')}

    # 분양
    if SALE_META_CSV.exists():
        for _, row in pd.read_csv(SALE_META_CSV).iterrows():
            ext_id = str(row.get('ID', ''))  # 이미 LH_sale_xxx 형식
            metadata[ext_id] = {
                'title': row.get('공고명', ''), 'category': '분양', 'region': row.get('지역', ''),
                'notice_type': row.get('유형', ''), 'posted_date': parse_date(row.get('게시일', '')),
                'deadline': parse_date(row.get('마감일', '')), 'status': row.get('상태', ''), 'url': row.get('URL', '')
            }
    if SALE_CORE_CSV.exists():
        for _, row in pd.read_csv(SALE_CORE_CSV).iterrows():
            ext_id = str(row.get('ID', ''))  # 이미 LH_sale_xxx 형식
            if ext_id in metadata:
                metadata[ext_id]['file_name'] = row.get('파일명', '')
            else:
                metadata[ext_id] = {'title': row.get('파일명', ''), 'category': '분양', 'file_name': row.get('파일명', '')}

    return metadata


def load_announcement_to_db(external_id: str, metadata: Dict) -> int:
    """공고 메타데이터 DB 삽입"""
    return insert_announcement(
        external_id=external_id,
        title=metadata.get('title', ''),
        category=metadata.get('category'),
        region=metadata.get('region'),
        notice_type=metadata.get('notice_type'),
        posted_date=metadata.get('posted_date'),
        deadline=metadata.get('deadline'),
        status=metadata.get('status'),
        url=metadata.get('url'),
        file_name=metadata.get('file_name')
    )


def load_chunks_to_db(chunks: List[Chunk], announcement_id: int):
    """청크 DB 삽입"""
    chunk_data = []
    for c in chunks:
        emb = c.metadata.get('embedding')
        if emb is None:
            continue
        chunk_data.append({
            'announcement_id': announcement_id, 'chunk_text': c.text, 'embedding': emb,
            'chunk_index': c.chunk_index, 'page_number': c.page_number, 'element_type': c.element_type,
            'table_context': c.table_context,
            'metadata': json.dumps({k: v for k, v in c.metadata.items() if k != 'embedding'}, ensure_ascii=False)
        })
    if chunk_data:
        insert_chunks(chunk_data)


def get_announcement_id(external_id: str) -> Optional[int]:
    """external_id로 announcement_id 조회"""
    with DBHandler() as cur:
        cur.execute("SELECT id FROM announcements WHERE external_id = %s", (external_id,))
        result = cur.fetchone()
        return result[0] if result else None
