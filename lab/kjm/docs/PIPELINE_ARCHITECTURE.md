# ZIP-FIT RAG 파이프라인 아키텍처

## 개요

LH 임대/분양 공고문 PDF를 처리하여 PostgreSQL + pgvector 기반 RAG 시스템을 구축하는 파이프라인입니다.

```
PDF 파일 → 파싱 → 청킹 → 임베딩 → DB 저장
                                    ↓
                    사용자 쿼리 → 하이브리드 검색 → 결과 반환
```

---

## Part 1: 데이터 적재 파이프라인

### 1.1 전체 흐름

```
pipeline.py (오케스트레이션)
    │
    ├─→ document_parser.py (PDF 파싱)
    │       └─→ camelot_table_extractor.py (테이블 추출)
    │
    ├─→ chunker.py (청킹)
    │
    ├─→ embedder.py (임베딩)
    │
    └─→ db_loader.py → db_handler.py (DB 저장)
```

### 1.2 PDF 파싱 (document_parser.py)

#### 하이브리드 파싱 전략

LlamaParse + Camelot 조합으로 최적의 결과를 얻습니다.

```python
def parse_pdf(file_path: Path, external_id: str, use_camelot: bool = True) -> ParsedDocument:
    # 1. LlamaParse로 마크다운 변환
    parser = LlamaParse(result_type="markdown")
    json_result = parser.get_json_result(str(file_path))

    # 2. 페이지별 요소 추출
    for page in json_result[0]['pages']:
        elements.extend(_extract_elements(content, page_num))

    # 3. Camelot으로 테이블 대체 (정확도 향상)
    if use_camelot:
        elements = _replace_with_camelot(file_path, elements)
```

#### 요소 타입 분류

마크다운을 3가지 요소로 분류합니다:

| 타입 | 식별 방법 | 예시 |
|------|-----------|------|
| `heading` | `#`으로 시작 | `## 입주자격` |
| `table` | `\|`로 시작하는 행들 | 마크다운 테이블 |
| `text` | 나머지 | 일반 문단 |

```python
def _extract_elements(markdown: str, page_number: int) -> list:
    for line in markdown.split('\n'):
        if line.startswith('#'):           # → heading
        elif line.strip().startswith('|'): # → table
        else:                              # → text
```

#### Camelot 테이블 대체 로직

```python
def _replace_with_camelot(file_path: Path, elements: list) -> list:
    camelot_tables = extract_tables_by_page(file_path)

    for elem in elements:
        if elem.element_type == 'table':
            # Camelot 테이블이 있고 정확도 70% 이상이면 대체
            if ct.accuracy >= 70.0:
                result.append(ParsedElement(ct.markdown, 'table', page))
```

**Camelot 사용 이유:**
- LlamaParse는 복잡한 병합 셀 처리에 약함
- Camelot은 PDF 테이블 구조를 더 정확하게 인식
- 정확도 70% 미만은 LlamaParse 결과 유지

### 1.3 테이블 추출 (camelot_table_extractor.py)

#### 헤더 행 감지

LH 문서에 특화된 키워드 기반 헤더 감지:

```python
header_keywords = {
    '구분', '항목', '유형', '자격', '기준', '요건', '내용', '순번', '번호',
    '순위', '단지', '주소', '면적', '세대', '신청', '접수', '서류', '일정',
    '기간', '대상', '조건', '공급', '타입', '호수', '층', '금액', '비고'
}

def detect_header_rows(df: pd.DataFrame) -> int:
    for i in range(min(4, len(df))):  # 최대 4행까지 검사
        row_text = ' '.join(str(v) for v in df.iloc[i].tolist())
        # 숫자가 절반 이상이면 데이터 행
        if numbers > len(row_values) // 2:
            break
        # 키워드 포함 시 헤더로 판단
        if any(kw in row_text for kw in header_keywords):
            header_count = i + 1
```

#### 다중 헤더 병합

```python
def merge_header_rows(df: pd.DataFrame, num_header_rows: int) -> List[str]:
    # 여러 헤더 행을 " - "로 연결
    # 예: ["구분", "소득기준"] → "구분 - 소득기준"
```

---

### 1.4 청킹 (chunker.py)

#### 설정값 (config.py)

```python
MIN_CHUNK_SIZE = 50       # 최소 청크 크기 (문자)
OPTIMAL_CHUNK_SIZE = 600  # 최적 청크 크기 (토큰)
MAX_CHUNK_SIZE = 1200     # 최대 청크 크기 (토큰)
CHUNK_OVERLAP = 150       # 청크 오버랩 (토큰)
MAX_TABLE_SIZE = 3000     # 테이블 최대 크기 (토큰)
```

#### 토큰 수 추정

한글 특성을 고려한 추정:

```python
def count_tokens(text: str) -> int:
    words = len(text.split())
    korean_chars = len(re.findall(r'[가-힣]', text))
    return words + korean_chars // 2  # 한글 2자 = 1토큰
```

#### 텍스트 청킹 전략

```
1. 문단 분리 (\n\n 기준)
2. 각 문단이 chunk_size 이내면 누적
3. 초과 시 현재 청크 저장 후 새 청크 시작
4. 오버랩: 이전 청크의 마지막 문단 유지
5. 큰 문단은 문장 단위로 추가 분할
```

```python
def split_text_into_chunks(text: str, chunk_size: int = 600, overlap: int = 150):
    paragraphs = re.split(r'\n\s*\n', text)

    for para in paragraphs:
        if para_size > chunk_size:
            # 큰 문단 → 문장 단위 분할
            chunks.extend(_split_by_sentences(para, chunk_size))
        elif current_size + para_size <= chunk_size:
            current_chunk.append(para)
        else:
            # 오버랩 처리
            if overlap > 0 and count_tokens(current_chunk[-1]) <= overlap:
                current_chunk = [current_chunk[-1], para]
```

#### 테이블 청킹

테이블은 헤더를 보존하면서 데이터 행 단위로 분할:

```python
def chunk_table(table_text: str, context_title: str = None, max_size: int = 3000):
    # 1. <br> 태그 정리
    table_text = clean_table_text(table_text)

    # 2. 컨텍스트 자동 추출 (없으면)
    if not context_title:
        context_title = extract_table_context(table_text)

    # 3. 작은 테이블은 그대로 반환
    if count_tokens(table_text) <= max_size:
        return [f"## {context_title}\n\n{table_text}"]

    # 4. 큰 테이블: 헤더 + 데이터 행 조합으로 분할
    header_text = '\n'.join(lines[:separator_idx + 1])
    for line in data_lines:
        if current_size + line_size + header_size <= max_size:
            current_chunk.append(line)
        else:
            chunks.append(header_text + '\n' + '\n'.join(current_chunk))
```

**테이블 분할 예시:**

원본 (3500 토큰):
```
| 구분 | 면적 | 세대수 |
|------|------|--------|
| A동 | 59㎡ | 100 |
| B동 | 74㎡ | 80 |
... (100개 행)
```

분할 결과:
```
청크 1:                    청크 2:
| 구분 | 면적 | 세대수 |   | 구분 | 면적 | 세대수 |
|------|------|--------|   |------|------|--------|
| A동 | 59㎡ | 100 |       | C동 | 84㎡ | 60 |
| B동 | 74㎡ | 80 |        | D동 | 114㎡ | 40 |
... (50개 행)              ... (50개 행)
```

#### 테이블 컨텍스트 자동 추출

```python
def extract_table_context(table_text: str) -> Optional[str]:
    # 방법 1: 헤더 셀에서 추출
    cells = first_line.split('|')
    return ' / '.join(key_cells[:3])  # 예: "구분 / 소득기준 / 자산기준"

    # 방법 2: 키워드 매칭
    TABLE_CONTEXT_KEYWORDS = [
        '소득', '자산', '면적', '임대', '보증금', '월세',
        '자격', '기준', '조건', '일정', '서류'
    ]
    keywords = [kw for kw in TABLE_CONTEXT_KEYWORDS if kw in table_text[:500]]
    return ' / '.join(keywords[:3])
```

#### 요소 → 청크 변환

```python
def create_chunks_from_elements(elements: List, document_id: str = None) -> List[Chunk]:
    current_heading = None

    for i, elem in enumerate(elements):
        if elem.element_type == 'heading':
            current_heading = elem.content  # 다음 요소에 붙임

        elif elem.element_type == 'table':
            # 1. metadata에 있으면 사용
            context = elem.metadata.get('context_title')

            # 2. 직전 heading 사용
            if not context:
                context = current_heading

            # 3. 컨텍스트가 없거나 너무 일반적이면 앞 요소에서 추출
            generic_contexts = ['소득', '자산', '면적', '임대', '보증금', ...]
            if not context or context in generic_contexts:
                found = _find_context_from_previous(elements, i)
                if found:
                    context = found

            for tc in chunk_table(elem.content, context):
                chunks.append(Chunk(tc, ..., 'table', context))
            current_heading = None  # 사용 후 초기화

        elif elem.element_type == 'text':
            text = f"## {current_heading}\n\n{elem.content}" if current_heading else elem.content
            for tc in split_text_into_chunks(text):
                chunks.append(Chunk(tc, ..., 'text'))
```

#### 테이블 컨텍스트 자동 추출 (앞 요소에서)

테이블의 컨텍스트가 없거나 일반적인 경우, 앞 요소들에서 제목을 찾습니다:

```python
def _find_context_from_previous(elements: List, current_idx: int, lookback: int = 5) -> Optional[str]:
    """테이블 앞 요소들에서 컨텍스트(제목/단지명 등) 추출

    heading이나 짧은 text 요소에서 의미있는 제목을 찾음
    """
    for j in range(current_idx - 1, max(-1, current_idx - lookback - 1), -1):
        prev = elements[j]
        content = prev.content.strip()

        # 페이지 번호나 무의미한 내용 무시
        if re.match(r'^-?\s*\d+\s*-?$', content):
            continue

        # heading은 무조건 사용
        if prev.element_type == 'heading':
            return content

        # 짧은 텍스트(100자 이하)는 제목일 가능성이 높음
        if prev.element_type == 'text' and len(content) <= 100:
            # page_header 태그 제거
            clean = re.sub(r'<page_header>([^<]+)</page_header>', r'\1', content)
            clean = clean.strip()
            if clean and len(clean) >= 3:
                return clean

    return None
```

**추출 예시:**
- 테이블 앞에 "화성봉담2 A-6블록" 텍스트 → 컨텍스트로 사용
- 테이블 앞에 "화성상리 1블록" 헤딩 → 컨텍스트로 사용
- 일반적인 "소득 / 임대 / 보증금" 대신 구체적인 단지명이 컨텍스트가 됨

---

### 1.5 임베딩 (embedder.py)

#### 모델 설정

```python
# OpenAI text-embedding-3-small
# 차원: 1536
# 특징: 빠르고 저렴, 한국어 지원

def get_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model="text-embedding-3-small")
```

#### 배치 임베딩

```python
def embed_chunks(chunks: List[Chunk]) -> List[Chunk]:
    texts = [c.text for c in chunks]
    embeddings = get_model().embed_documents(texts)

    for chunk, emb in zip(chunks, embeddings):
        chunk.metadata['embedding'] = emb  # 1536차원 벡터
    return chunks
```

---

### 1.6 DB 저장 (db_handler.py, db_loader.py)

#### 테이블 스키마

```sql
-- 공고 메타데이터
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,  -- LH_lease_272
    title TEXT NOT NULL,
    category VARCHAR(20),             -- 임대/분양
    region VARCHAR(100),
    notice_type VARCHAR(50),
    posted_date DATE,
    deadline DATE,
    status VARCHAR(20),
    url TEXT,
    file_name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 문서 청크
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    announcement_id INTEGER REFERENCES announcements(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(1536),           -- pgvector
    fts_vector tsvector,              -- Full-Text Search
    chunk_index INTEGER,
    page_number INTEGER,
    element_type VARCHAR(20),         -- text/table
    table_context TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 인덱스

```sql
-- 벡터 검색용 HNSW 인덱스
CREATE INDEX idx_chunks_embedding ON document_chunks
    USING hnsw (embedding vector_cosine_ops);

-- Full-Text Search용 GIN 인덱스
CREATE INDEX idx_chunks_fts ON document_chunks
    USING GIN(fts_vector);
```

#### FTS 자동 업데이트 트리거

```sql
CREATE FUNCTION chunk_text_to_fts_vector_trigger() RETURNS trigger AS $$
BEGIN
    NEW.fts_vector := to_tsvector('simple', NEW.chunk_text);
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER tsvector_update_trigger
    BEFORE INSERT OR UPDATE ON document_chunks
    FOR EACH ROW EXECUTE PROCEDURE chunk_text_to_fts_vector_trigger();
```

**`simple` 설정 사용 이유:**
- 한국어는 형태소 분석 없이 공백 기준 토큰화
- 복잡한 언어 처리 없이 빠른 검색

---

## Part 2: 검색 파이프라인

### 2.1 하이브리드 검색 개요

```
사용자 쿼리
    │
    ├─→ FTS 검색 (키워드 매칭)
    │
    ├─→ 벡터 검색 (의미 유사도)
    │
    └─→ RRF 재정렬 (순위 융합)
           │
           └─→ 테이블 보강 (공고 매칭 시)
                  │
                  └─→ 최종 결과
```

### 2.2 hybrid_search 함수 상세

```python
def hybrid_search(query: str, query_embedding: List[float], top_k: int = 10, k: int = 60):
```

#### Step 1: 공고 title 매칭

쿼리 키워드가 1개 이상 포함된 공고를 식별 (조사 제거 후 검색):

```python
words = query.split()
# 조사 제거된 키워드 (검색용)
clean_words = [strip_particles(w) for w in words if len(w) >= 2]
clean_words = [w for w in clean_words if len(w) >= 2]

like_patterns = [f"%{w}%" for w in clean_words]

# 1개 이상 키워드 매칭되는 공고 선별
SELECT id FROM announcements
WHERE title LIKE %s OR title LIKE %s ...

matched_ann_ids = [r[0] for r in cur.fetchall()]
```

**예시:** 쿼리 "화성시 공고의 임대보증금은 얼마야?"
- "화성시" → 조사 제거 후 "화성시" 매칭 → 해당 공고 선택
- 이전에는 2개 이상 매칭이 필요했으나, 특정 지역/단지명 검색을 위해 1개 이상으로 완화

#### Step 2: FTS 검색

```python
fts_query = ' | '.join(words + [''.join(words)])  # OR 조건 + 붙여쓰기

SELECT id, ts_rank(fts_vector, to_tsquery('simple', %s)) as score
FROM document_chunks
WHERE fts_vector @@ to_tsquery('simple', %s)
ORDER BY score DESC
LIMIT 100
```

**FTS 쿼리 예시:**
- 입력: "소득 기준"
- 변환: `"소득 | 기준 | 소득기준"` (붙여쓰기 포함)

#### Step 3: 벡터 검색

```python
SELECT id FROM document_chunks
ORDER BY embedding <=> %s::vector  -- 코사인 거리
LIMIT 100
```

#### Step 4: RRF (Reciprocal Rank Fusion) 재정렬

두 검색 결과를 순위 기반으로 융합:

```python
# k = 60 (RRF 상수)
rrf_score = 1/(k + fts_rank) + 1/(k + vec_rank)
```

**RRF 계산 예시:**

| 문서 | FTS 순위 | 벡터 순위 | RRF 스코어 |
|------|----------|-----------|------------|
| A | 1 | 5 | 1/61 + 1/65 = 0.032 |
| B | 10 | 1 | 1/70 + 1/61 = 0.031 |
| C | 3 | 3 | 1/63 + 1/63 = 0.032 |

→ 둘 다 상위권인 문서가 높은 점수

#### Step 5: 테이블 보강

공고가 매칭되면 해당 공고의 테이블도 추가:

```python
if matched_ann_ids:
    # 1. 키워드 기반 테이블 검색
    clean_words = [strip_particles(w) for w in words]  # 조사 제거

    SELECT id FROM document_chunks
    WHERE announcement_id = ANY(%s)
      AND element_type = 'table'
      AND (chunk_text LIKE '%소득%' OR chunk_text LIKE '%기준%')
    LIMIT 15

    # 2. 벡터 유사도 기반 보완
    SELECT id FROM document_chunks
    WHERE announcement_id = ANY(%s) AND element_type = 'table'
    ORDER BY embedding <=> %s::vector
    LIMIT 10

    # 키워드 우선 + 벡터 보완 (최대 20개)
    table_ids = keyword_table_ids + vector_table_ids
```

**조사 제거 함수:**

```python
KO_PARTICLES = ['을', '를', '이', '가', '은', '는', '의', '에', '로', '으로', '에서', '과', '와']

def strip_particles(word: str) -> str:
    for suffix in KO_PARTICLES:
        if word.endswith(suffix) and len(word) > len(suffix):
            return word[:-len(suffix)]
    return word
```

- "소득기준을" → "소득기준"
- "자격조건에" → "자격조건"

#### Step 6: 결과 반환

```python
SELECT dc.id, dc.chunk_text, dc.element_type, dc.table_context,
       a.title, a.region, a.category,
       1 - (dc.embedding <=> %s::vector) as similarity
FROM document_chunks dc
JOIN announcements a ON dc.announcement_id = a.id
WHERE dc.id = ANY(%s)
ORDER BY array_position(%s::bigint[], dc.id)  -- RRF 순위 유지
```

---

### 2.3 RDB 메타데이터 검색 (search_announcements)

LangGraph 확장을 위한 RDB 필터링 검색:

```python
def search_announcements(
    deadline_after: Optional[date] = None,   # 마감일 이후
    deadline_before: Optional[date] = None,  # 마감일 이전
    category: Optional[str] = None,          # 임대/분양
    region: Optional[str] = None,            # 지역 (LIKE)
    status: Optional[str] = None,            # 접수중/마감
    keyword: Optional[str] = None,           # 제목 검색
    limit: int = 20
) -> List[Dict]:
```

**사용 예시:**

```python
# 마감 안 된 공고
search_announcements(deadline_after=date.today(), status='접수중')

# 서울 임대 공고
search_announcements(category='임대', region='서울')
```

---

## Part 3: 파일 구조

```
lab/kjm/
├── config.py                    # 설정값 (DB, 청킹 파라미터)
├── pipeline.py                  # 메인 오케스트레이션
│
├── document_parser.py           # PDF → 요소 파싱
├── camelot_table_extractor.py   # 테이블 추출
│
├── chunker.py                   # 텍스트/테이블 청킹
├── embedder.py                  # OpenAI 임베딩
│
├── db_handler.py                # DB 연결, 검색 함수
├── db_loader.py                 # 메타데이터/청크 적재
│
└── data/
    ├── LH_lease_서울.경기/      # 임대 PDF
    ├── LH_sale_서울.경기/       # 분양 PDF
    └── *.csv                    # 메타데이터 CSV
```

---

## Part 4: 실행 방법

```bash
# 전체 파이프라인 실행 (DB 리셋)
python pipeline.py --reset

# 20개 PDF만 처리
python pipeline.py --limit 20

# 기존 데이터 유지하며 추가
python pipeline.py

# 검색 테스트
python pipeline.py --test-search "화성시 행복주택 소득기준"
```

---

## Part 5: 성능 특성

| 항목 | 값 |
|------|-----|
| PDF 1개당 처리 시간 | ~30초 (LlamaParse + Camelot) |
| 평균 청크 수/PDF | 150-200개 |
| 임베딩 차원 | 1536 |
| FTS 설정 | simple (공백 기준) |
| 벡터 인덱스 | HNSW (코사인 거리) |
| 검색 응답 시간 | <500ms |
