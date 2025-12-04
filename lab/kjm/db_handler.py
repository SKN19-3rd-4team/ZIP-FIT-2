"""PostgreSQL + pgvector DB 핸들러"""
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from typing import List, Dict, Optional
from datetime import date
from config import DB_CONFIG

# 한국어 조사 목록
KO_PARTICLES = ['을', '를', '이', '가', '은', '는', '의', '에', '로', '으로', '에서', '과', '와']


class DBHandler:
    """PostgreSQL 연결 Context Manager"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.conn.autocommit = True
        register_vector(self.conn)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, *args):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def strip_particles(word: str) -> str:
    """한국어 조사 제거"""
    for suffix in KO_PARTICLES:
        if word.endswith(suffix) and len(word) > len(suffix):
            return word[:-len(suffix)]
    return word


def init_tables():
    """테이블 생성 및 FTS 설정"""
    with DBHandler() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id SERIAL PRIMARY KEY, external_id VARCHAR(255) UNIQUE,
                title TEXT NOT NULL, category VARCHAR(20), region VARCHAR(100),
                notice_type VARCHAR(50), posted_date DATE, deadline DATE,
                status VARCHAR(20), url TEXT, file_name TEXT, created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id SERIAL PRIMARY KEY,
                announcement_id INTEGER REFERENCES announcements(id) ON DELETE CASCADE,
                chunk_text TEXT NOT NULL, embedding vector(1536), fts_vector tsvector,
                chunk_index INTEGER, page_number INTEGER, element_type VARCHAR(20),
                table_context TEXT, metadata JSONB, created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_fts ON document_chunks USING GIN(fts_vector);")
        cur.execute("""
            CREATE OR REPLACE FUNCTION chunk_text_to_fts_vector_trigger() RETURNS trigger AS $$
            BEGIN NEW.fts_vector := to_tsvector('simple', NEW.chunk_text); RETURN NEW; END $$ LANGUAGE plpgsql;
        """)
        cur.execute("""
            DROP TRIGGER IF EXISTS tsvector_update_trigger ON document_chunks;
            CREATE TRIGGER tsvector_update_trigger BEFORE INSERT OR UPDATE
            ON document_chunks FOR EACH ROW EXECUTE PROCEDURE chunk_text_to_fts_vector_trigger();
        """)


def drop_tables():
    """테이블 삭제"""
    with DBHandler() as cur:
        cur.execute("DROP TABLE IF EXISTS document_chunks CASCADE;")
        cur.execute("DROP TABLE IF EXISTS announcements CASCADE;")


def insert_announcement(external_id: str, title: str, **kw):
    """공고 삽입, ID 반환"""
    with DBHandler() as cur:
        cur.execute("""
            INSERT INTO announcements (external_id, title, category, region, notice_type, posted_date, deadline, status, url, file_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (external_id) DO UPDATE SET title = EXCLUDED.title, category = EXCLUDED.category, region = EXCLUDED.region
            RETURNING id;
        """, (external_id, title, kw.get('category'), kw.get('region'), kw.get('notice_type'),
              kw.get('posted_date'), kw.get('deadline'), kw.get('status'), kw.get('url'), kw.get('file_name')))
        return cur.fetchone()[0]


def insert_chunks(chunks: list):
    """청크 배치 삽입"""
    if not chunks:
        return
    with DBHandler() as cur:
        values = [(c['announcement_id'], c['chunk_text'], c['embedding'], c.get('chunk_index'),
                   c.get('page_number'), c.get('element_type'), c.get('table_context'), c.get('metadata')) for c in chunks]
        execute_values(cur, """
            INSERT INTO document_chunks (announcement_id, chunk_text, embedding, chunk_index, page_number, element_type, table_context, metadata)
            VALUES %s
        """, values)


def hybrid_search(query: str, query_embedding: List[float], top_k: int = 10, k: int = 60):
    """하이브리드 검색 (키워드 + 벡터) + RRF 재정렬

    특정 공고가 매칭되면 해당 공고의 청크도 함께 반환
    """
    with DBHandler() as cur:
        words = query.split()
        # 조사 제거된 키워드 (검색용)
        clean_words = [strip_particles(w) for w in words if len(w) >= 2]
        clean_words = [w for w in clean_words if len(w) >= 2]

        # 1단계: 공고 title 매칭 - 1개 이상 단어가 매칭되는 공고
        like_patterns = [f"%{w}%" for w in clean_words]
        matched_ann_ids = []
        if like_patterns:
            cur.execute(f"""
                SELECT id FROM announcements
                WHERE {' OR '.join(['title LIKE %s' for _ in like_patterns])}
            """, like_patterns)
            matched_ann_ids = [r[0] for r in cur.fetchall()]

        # 2단계: FTS 검색
        fts_query = ' | '.join(words + [''.join(words)])
        cur.execute("""
            SELECT id, ts_rank(fts_vector, to_tsquery('simple', %s)) as score
            FROM document_chunks WHERE fts_vector @@ to_tsquery('simple', %s)
            ORDER BY score DESC LIMIT 100;
        """, (fts_query, fts_query))
        fts_results = {row[0]: i + 1 for i, row in enumerate(cur.fetchall())}

        # 3단계: 벡터 검색
        cur.execute("""
            SELECT id FROM document_chunks
            ORDER BY embedding <=> %s::vector LIMIT 100;
        """, (query_embedding,))
        vec_results = {row[0]: i + 1 for i, row in enumerate(cur.fetchall())}

        # RRF 스코어 계산
        all_ids = set(fts_results) | set(vec_results)
        if not all_ids:
            return []

        rrf = {
            doc_id: 1.0 / (k + fts_results.get(doc_id, 1000)) + 1.0 / (k + vec_results.get(doc_id, 1000))
            for doc_id in all_ids
        }
        top_ids = [doc_id for doc_id, _ in sorted(rrf.items(), key=lambda x: x[1], reverse=True)[:top_k]]

        # 4단계: 매칭된 공고의 테이블 추가 (키워드 + 벡터 검색)
        if matched_ann_ids:
            keyword_like = [f"%{w}%" for w in clean_words]
            if keyword_like:
                like_conditions = ' OR '.join(['chunk_text LIKE %s' for _ in keyword_like])
                cur.execute(f"""
                    SELECT id FROM document_chunks
                    WHERE announcement_id = ANY(%s) AND element_type = 'table'
                    AND ({like_conditions})
                    LIMIT 15
                """, [matched_ann_ids] + keyword_like)
                keyword_table_ids = [r[0] for r in cur.fetchall()]
            else:
                keyword_table_ids = []

            # 벡터 유사도 기반 테이블 보완
            cur.execute("""
                SELECT id FROM document_chunks
                WHERE announcement_id = ANY(%s) AND element_type = 'table'
                ORDER BY embedding <=> %s::vector LIMIT 10
            """, (matched_ann_ids, query_embedding))
            vector_table_ids = [r[0] for r in cur.fetchall()]

            # 키워드 우선 + 벡터 보완 (최대 20개)
            table_ids = list(dict.fromkeys(keyword_table_ids + vector_table_ids))[:20]
            top_ids = list(dict.fromkeys(top_ids + table_ids))

        if not top_ids:
            return []

        cur.execute("""
            SELECT dc.id, dc.chunk_text, dc.element_type, dc.table_context, a.title, a.region, a.category,
                   1 - (dc.embedding <=> %s::vector) as similarity
            FROM document_chunks dc JOIN announcements a ON dc.announcement_id = a.id
            WHERE dc.id = ANY(%s) ORDER BY array_position(%s::bigint[], dc.id);
        """, (query_embedding, top_ids, top_ids))
        return cur.fetchall()


def search_announcements(
    deadline_after: Optional[date] = None,
    deadline_before: Optional[date] = None,
    category: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 20
) -> List[Dict]:
    """RDB 메타데이터 검색 - LangGraph tool용

    Args:
        deadline_after: 마감일이 이 날짜 이후인 공고
        deadline_before: 마감일이 이 날짜 이전인 공고
        category: 임대/분양
        region: 지역 (LIKE 검색)
        status: 접수중/마감 등
        keyword: 제목 키워드 (LIKE 검색)
        limit: 최대 결과 수
    """
    conditions = []
    params = []

    if deadline_after:
        conditions.append("deadline >= %s")
        params.append(deadline_after)
    if deadline_before:
        conditions.append("deadline <= %s")
        params.append(deadline_before)
    if category:
        conditions.append("category = %s")
        params.append(category)
    if region:
        conditions.append("region LIKE %s")
        params.append(f"%{region}%")
    if status:
        conditions.append("status = %s")
        params.append(status)
    if keyword:
        conditions.append("title LIKE %s")
        params.append(f"%{keyword}%")

    where_clause = " AND ".join(conditions) if conditions else "1=1"
    params.append(limit)

    with DBHandler() as cur:
        cur.execute(f"""
            SELECT id, external_id, title, category, region, notice_type,
                   posted_date, deadline, status, url
            FROM announcements
            WHERE {where_clause}
            ORDER BY deadline DESC NULLS LAST, posted_date DESC
            LIMIT %s
        """, params)

        columns = ['id', 'external_id', 'title', 'category', 'region',
                   'notice_type', 'posted_date', 'deadline', 'status', 'url']
        return [dict(zip(columns, row)) for row in cur.fetchall()]
