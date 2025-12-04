# ZIP-FIT RAG 파이프라인

LH 임대/분양 공고문 PDF를 파싱하여 PostgreSQL + pgvector 기반 RAG 시스템을 구축하는 파이프라인입니다.

## 아키텍처

```
PDF 파일 → 파싱 (Unstructured) → 청킹 → 임베딩 (OpenAI) → PostgreSQL + pgvector
                                                              ↓
                                          하이브리드 검색 (FTS + 벡터 + RRF)
                                                              ↓
                                                    LLM (GPT-4o-mini)
```

## 파일 구조

```
lab/kjm/
├── config.py              # 경로 설정
├── pipeline.py            # 메인 파이프라인
├── document_parser.py     # PDF 파싱 (Unstructured 기반)
├── chunker.py             # 텍스트 청킹
├── embedder.py            # OpenAI 임베딩
├── db_handler.py          # PostgreSQL 연결 및 검색
├── db_loader.py           # CSV 메타데이터 및 DB 적재
├── chatbot_test.ipynb     # 챗봇 테스트 노트북
└── data/                  # PDF 및 CSV 데이터 (gitignore)
```

## 설치 및 설정

### 1. 환경 변수 (.env)

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zipfit
DB_USER=postgres
DB_PASSWORD=yourpassword
```

### 2. 의존성 설치

```bash
pip install psycopg2-binary pgvector python-dotenv pandas tqdm
pip install langchain langchain-openai
pip install unstructured[pdf]  # PDF 파싱
```

### 3. PostgreSQL + pgvector 설정

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## 사용법

### 파이프라인 실행

```bash
# 전체 파이프라인 실행 (기존 데이터 유지, 새 PDF만 처리)
python pipeline.py

# DB 리셋 후 전체 재처리
python pipeline.py --reset

# 카테고리별 처리
python pipeline.py --category lease   # 임대만
python pipeline.py --category sale    # 분양만

# 테스트 (일부만 처리)
python pipeline.py --limit 5

# 검색 테스트
python pipeline.py --test-search "서울 오류 행복주택 면적"
```

### 챗봇 테스트

`chatbot_test.ipynb` 노트북에서 대화형 테스트 가능:

```python
from chatbot_test import ask

ask("서울 오류 행복주택 신청자격 알려줘")
ask("화성시 공고의 임대조건은?")
```

## DB 스키마

### announcements (공고 메타데이터)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | PK |
| external_id | VARCHAR(255) | 고유 ID (예: LH_lease_272) |
| title | TEXT | 공고명 |
| category | VARCHAR(20) | 임대/분양 |
| region | VARCHAR(100) | 지역 |
| notice_type | VARCHAR(50) | 유형 (국민임대, 행복주택 등) |
| posted_date | DATE | 게시일 |
| deadline | DATE | 마감일 |
| status | VARCHAR(20) | 상태 |
| url | TEXT | 원본 URL |
| file_name | TEXT | PDF 파일명 |

### document_chunks (문서 청크)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | SERIAL | PK |
| announcement_id | INTEGER | FK → announcements |
| chunk_text | TEXT | 청크 텍스트 |
| embedding | vector(1536) | OpenAI 임베딩 |
| fts_vector | tsvector | 전문 검색 벡터 |
| chunk_index | INTEGER | 청크 순서 |
| page_number | INTEGER | 페이지 번호 |
| element_type | VARCHAR(20) | text/table/heading |
| table_context | TEXT | 테이블 컨텍스트 (헤딩) |
| metadata | JSONB | 추가 메타데이터 |

## 하이브리드 검색 로직

`hybrid_search()` 함수는 4단계로 검색을 수행합니다:

### 1단계: 공고 제목 매칭
- 쿼리 단어가 2개 이상 공고 제목에 매칭되면 해당 공고 우선
- 예: "서울 오류 행복주택" → "서울오류행복주택" 공고 매칭

### 2단계: FTS (Full-Text Search)
- PostgreSQL의 `tsvector`/`tsquery` 사용
- 한국어는 'simple' 설정 (형태소 분석 없음)

### 3단계: 벡터 검색
- OpenAI 임베딩 기반 코사인 유사도
- pgvector의 HNSW 인덱스 사용

### 4단계: RRF (Reciprocal Rank Fusion)
- FTS와 벡터 검색 결과를 RRF로 통합
- 공고가 매칭된 경우 해당 공고의 테이블 청크 추가 포함

### 검색 최적화

**문제**: "서울 오류 행복주택 면적" 쿼리 시 면적 테이블이 검색되지 않음

**원인**:
- 긴 쿼리의 임베딩은 특정 테이블과 벡터 유사도가 낮음
- 공고명이 쿼리에 포함되면 토픽 키워드의 영향력 감소

**해결책**:
1. 공고 제목 매칭 시 해당 공고의 테이블 청크 우선 포함
2. 쿼리 키워드(조사 제거)로 테이블 LIKE 검색
3. 키워드 매칭 테이블 15개 + 벡터 유사도 테이블 10개 = 최대 20개

```python
# 조사 제거 로직
suffixes = ['을', '를', '이', '가', '은', '는', '의', '에', '로', '으로', '에서', '과', '와']
# "면적을" → "면적", "공고의" → "공고"
```

## CSV 메타데이터 매핑

### 문제
- CSV ID: `LH_lease_8` (이미 형식화됨)
- PDF 파일명: `(LH_lease_272)_[정정공고]화성시_행복주택...pdf`

### 해결
1. **db_loader.py**: CSV ID를 그대로 사용 (prefix 중복 제거)
2. **pipeline.py**: PDF 파일명에서 정규식으로 ID 추출

```python
# 파일명에서 ID 추출
pattern = r'\(LH_lease_(\d+)\)'
# "(LH_lease_272)_..." → "LH_lease_272"
```

## 성능 고려사항

### 토큰 제한
- GPT-4o-mini 컨텍스트: 128K 토큰
- 검색 결과 제한: 최대 ~25개 청크 (~18K 토큰)

### 인덱스
```sql
-- 벡터 검색 (HNSW)
CREATE INDEX idx_chunks_embedding ON document_chunks
USING hnsw (embedding vector_cosine_ops);

-- 전문 검색 (GIN)
CREATE INDEX idx_chunks_fts ON document_chunks USING GIN(fts_vector);
```

## 테이블 처리 개선

### 1. `<br>` 태그 정리

PDF 파싱 시 테이블 셀 내 줄바꿈이 `<br>` 태그로 변환되는 문제 해결:

```python
# chunker.py - clean_table_text()
def clean_table_text(text: str) -> str:
    # <br> 태그를 공백으로 변환
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
    # 연속 공백 정리
    text = re.sub(r'  +', ' ', text)
    return text
```

**적용 전**: `신청자격<br>및<br>입주자 선정방법`
**적용 후**: `신청자격 및 입주자 선정방법`

### 2. 테이블 컨텍스트 자동 추출

테이블에 컨텍스트(제목)가 없는 경우 자동으로 추출:

```python
# chunker.py - extract_table_context()
def extract_table_context(table_text: str) -> Optional[str]:
    # 1. 마크다운 테이블 헤더에서 추출
    # | 주택명 | 면적 | 보증금 | → "주택명 / 면적 / 보증금"

    # 2. 테이블 내용에서 키워드 추출
    important_terms = ['소득', '자산', '면적', '임대', '보증금', '월세', '자격', '기준', '조건', '일정', '서류']
    # → "면적 / 임대 / 보증금"
```

**활용**:
- DB의 `table_context` 컬럼에 저장
- 검색 결과에서 LLM이 테이블 의미 파악에 활용
- 청크 텍스트 앞에 `## {context}` 헤더로 추가

**예시**:
```
## 면적 / 임대 / 보증금

| 주택명 | 전용면적 | 임대보증금 | 월임대료 |
|--------|----------|------------|----------|
| 36A    | 36㎡     | 12,900     | 129      |
```

## 알려진 제한사항

1. **한국어 형태소 분석**: PostgreSQL FTS는 한국어 형태소 분석을 지원하지 않아 'simple' 설정 사용
2. **테이블 파싱**: PDF의 복잡한 테이블은 파싱 품질이 떨어질 수 있음
3. **임베딩 비용**: OpenAI 임베딩 API 호출 비용 발생

## 향후 개선 방향

- [ ] 한국어 형태소 분석기 통합 (예: mecab)
- [x] 테이블 `<br>` 태그 정리
- [x] 테이블 컨텍스트 자동 추출
- [ ] 테이블 파싱 개선 (Camelot 등)
- [ ] 캐싱 레이어 추가
- [ ] 스트리밍 응답 지원
