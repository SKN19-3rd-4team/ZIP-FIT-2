"""PDF 파싱 → 청킹 → 임베딩 → DB 적재 파이프라인"""
import argparse
import re
from pathlib import Path
from tqdm import tqdm
from config import LEASE_PDF_DIR, SALE_PDF_DIR
from db_handler import init_tables, drop_tables, DBHandler, hybrid_search
from document_parser import parse_pdf
from chunker import create_chunks_from_elements
from embedder import embed_chunks, embed_text
from db_loader import load_csv_metadata, load_announcement_to_db, load_chunks_to_db, get_announcement_id


def extract_external_id(filename: str, category: str) -> str:
    """파일명에서 external_id 추출 (예: LH_lease_272)"""
    # (LH_lease_272)_ 또는 (LH_sale_123)_ 패턴에서 ID 추출
    pattern = rf'\(LH_{category}_(\d+)\)'
    match = re.search(pattern, filename)
    if match:
        return f"LH_{category}_{match.group(1)}"
    # 패턴 매칭 실패 시 파일명 전체 사용 (fallback)
    return f"LH_{category}_{Path(filename).stem}"


def get_pdf_list(category: str = 'all'):
    """PDF 파일 목록 조회 (공고문만 필터링)"""
    pdfs = []
    if category in ['lease', 'all'] and LEASE_PDF_DIR.exists():
        for f in LEASE_PDF_DIR.glob('*공고*.pdf'):
            ext_id = extract_external_id(f.name, 'lease')
            pdfs.append((ext_id, f))
    if category in ['sale', 'all'] and SALE_PDF_DIR.exists():
        for f in SALE_PDF_DIR.glob('*공고*.pdf'):
            ext_id = extract_external_id(f.name, 'sale')
            pdfs.append((ext_id, f))
    return pdfs


def process_pdf(external_id: str, file_path: Path, metadata: dict, skip_existing: bool = True):
    """단일 PDF 처리"""
    try:
        if skip_existing and get_announcement_id(external_id):
            return 0

        parsed = parse_pdf(file_path, external_id)
        if not parsed.elements:
            return 0

        chunks = create_chunks_from_elements(parsed.elements, external_id)
        if not chunks:
            return 0

        embed_chunks(chunks)
        ann_id = load_announcement_to_db(external_id, metadata)
        load_chunks_to_db(chunks, ann_id)
        return len(chunks)
    except Exception as e:
        print(f"오류: {external_id} - {e}")
        return None


def run_pipeline(category: str = 'all', limit: int = None, skip_existing: bool = True, reset_db: bool = False):
    """전체 파이프라인 실행"""
    print("=" * 50)
    print("ZIP-FIT DB 구축 파이프라인")
    print("=" * 50)

    if reset_db:
        drop_tables()
    init_tables()

    metadata_map = load_csv_metadata()
    pdf_list = get_pdf_list(category)
    if limit:
        pdf_list = pdf_list[:limit]

    print(f"처리할 PDF: {len(pdf_list)}개")

    success, fail, total = 0, 0, 0
    for ext_id, path in tqdm(pdf_list, desc="처리 중"):
        meta = metadata_map.get(ext_id, {'title': path.name})
        result = process_pdf(ext_id, path, meta, skip_existing)
        if result is not None:
            success += 1
            total += result
        else:
            fail += 1

    print(f"\n완료: 성공 {success}, 실패 {fail}, 총 청크 {total}개")

    with DBHandler() as cur:
        cur.execute("SELECT COUNT(*) FROM announcements")
        ann = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM document_chunks")
        chunks = cur.fetchone()[0]
    print(f"DB 상태: announcements {ann}개, chunks {chunks}개")


def test_search(query: str, top_k: int = 10):
    """검색 테스트"""
    print(f"\n쿼리: {query}")
    return hybrid_search(query, embed_text(query), top_k=top_k)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ZIP-FIT DB 구축')
    parser.add_argument('--category', default='all', choices=['lease', 'sale', 'all'])
    parser.add_argument('--limit', type=int)
    parser.add_argument('--reset', action='store_true')
    parser.add_argument('--no-skip', action='store_true')
    parser.add_argument('--test-search', type=str)
    args = parser.parse_args()

    if args.test_search:
        for i, row in enumerate(test_search(args.test_search)):
            print(f"\n#{i+1}: {row[4]} - {row[1][:200]}...")
    else:
        run_pipeline(args.category, args.limit, not args.no_skip, args.reset)
