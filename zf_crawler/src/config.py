"""
ZIP-FIT 프로젝트 설정 파일
임대/분양 공고문 기반 RAG 챗봇을 위한 DB 구축 설정
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 경로 설정
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
DATA_DIR = CURRENT_DIR / "data"

# PDF 파일 경로
LEASE_PDF_DIR = DATA_DIR / "LH_lease_서울.경기"
SALE_PDF_DIR = DATA_DIR / "LH_sale_서울.경기"

# CSV 파일 경로
LEASE_CORE_CSV = DATA_DIR / "lh_lease_notices-download_core.csv"
LEASE_META_CSV = DATA_DIR / "lh_lease_notices_eng_core.csv"
SALE_CORE_CSV = DATA_DIR / "lh_sale_notices-download_core.csv"
SALE_META_CSV = DATA_DIR / "lh_sale_notices_eng_core.csv"

# DB 설정 (psycopg2 호환)
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'dbname': os.getenv('DB_NAME')
}

# API 키
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 임베딩 설정
EMBEDDING_MODEL_NAME = 'text-embedding-3-small'
EMBEDDING_DIMENSION = 1536

# 청킹 설정
MIN_CHUNK_SIZE = 50       # 최소 청크 크기 (문자) - 이보다 짧으면 필터링
OPTIMAL_CHUNK_SIZE = 600  # 최적 청크 크기 (토큰)
MAX_CHUNK_SIZE = 1200     # 최대 청크 크기 (토큰)
CHUNK_OVERLAP = 150       # 청크 오버랩 (토큰)
MAX_TABLE_SIZE = 3000     # 테이블 최대 크기 (토큰)

# 처리 설정
BATCH_SIZE = 10
MAX_WORKERS = 4

# 테이블 컨텍스트 추출용 키워드
TABLE_CONTEXT_KEYWORDS = [
    '소득', '자산', '면적', '임대', '보증금', '월세',
    '자격', '기준', '조건', '일정', '서류'
]
