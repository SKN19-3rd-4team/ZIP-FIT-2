from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0005_alter_anncall_created_dttm_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                -- 1) 컬럼이 없으면 생성 (모델에도 정의되어 있음)
                --ALTER TABLE doc_chunks
                --ADD COLUMN IF NOT EXISTS fts_vector tsvector;

                -- 2) GIN 인덱스 생성
                CREATE INDEX IF NOT EXISTS idx_doc_chunks_fts
                ON doc_chunks USING GIN (fts_vector);

                -- 3) 트리거 함수 정의
                CREATE OR REPLACE FUNCTION doc_chunks_fts_trigger() RETURNS trigger AS $$
                BEGIN
                    NEW.fts_vector := to_tsvector('simple', NEW.chunk_text);
                    RETURN NEW;
                END
                $$ LANGUAGE plpgsql;

                -- 4) 트리거 재생성
                DROP TRIGGER IF EXISTS doc_chunks_fts_update ON doc_chunks;

                CREATE TRIGGER doc_chunks_fts_update
                BEFORE INSERT OR UPDATE ON doc_chunks
                FOR EACH ROW EXECUTE PROCEDURE doc_chunks_fts_trigger();
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS doc_chunks_fts_update ON doc_chunks;
                DROP FUNCTION IF EXISTS doc_chunks_fts_trigger();
                DROP INDEX IF EXISTS idx_doc_chunks_fts;
                -- 필요 시 컬럼까지 제거하려면 아래 주석을 해제
                -- ALTER TABLE doc_chunks DROP COLUMN IF EXISTS fts_vector;
            """,
        ),
    ]
