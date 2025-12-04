# ZIP-FIT 파이프라인 리뷰 및 개선 문서

## 1. 개요

### 1.1 파이프라인 구조
```
PDF → LlamaParse 파싱 → 테이블 처리 → 청킹 → OpenAI 임베딩 → PostgreSQL + pgvector 저장
```

### 1.2 주요 파일 구성
| 파일 | 역할 |
|------|------|
| `config.py` | 설정 (DB, API 키, 청킹 파라미터) |
| `document_parser.py` | LlamaParse로 PDF → Markdown 변환 |
| `pdf_filter.py` | 공고 PDF 필터링 (양식 제외) |
| `table_processor.py` | 마크다운 테이블 처리 |
| `chunker.py` | 텍스트/테이블 청킹 |
| `embedder.py` | OpenAI 임베딩 생성 |
| `db_handler.py` | PostgreSQL + pgvector 연동 |
| `db_loader.py` | CSV 메타데이터 및 청크 DB 적재 |
| `pipeline.py` | 전체 오케스트레이션 |

---

## 2. 발견된 문제점 및 해결

### 2.1 페이지 번호가 모두 1로 저장되는 문제

**원인**: `document_parser.py`에서 `load_data()` 사용 시 메타데이터가 비어있음

**해결**: `get_json_result()` 사용으로 변경

```python
# 변경 전
documents = parser.load_data(str(file_path))
for doc in documents:
    page_num = doc.metadata.get('page_label', 1)  # 항상 1 반환

# 변경 후
json_result = parser.get_json_result(str(file_path))
if json_result and 'pages' in json_result[0]:
    for page_data in json_result[0]['pages']:
        page_num = page_data.get('page', 1)  # 실제 페이지 번호
        content = page_data.get('md', '')
```

**검증 결과**:
```
=== 페이지 번호 분포 ===
  페이지 1: 6개 청크
  페이지 2: 10개 청크
  ...
  페이지 49: 1개 청크
```

---

### 2.2 빈 청크 및 의미없는 청크 저장 문제

**원인**: 청크 유효성 검사 없이 모든 청크 저장

**해결**: `chunker.py`에 `is_valid_chunk()` 함수 추가

```python
def is_valid_chunk(text: str, min_size: int = MIN_CHUNK_SIZE) -> bool:
    if not text or not text.strip():
        return False

    stripped = text.strip()
    if len(stripped) < min_size:
        return False

    # 의미 없는 패턴 제외
    meaningless_patterns = [
        r'^-\s*\d+\s*-$',           # "- 8 -" 페이지 번호
        r'^#{1,6}\s*\d+\.?\s*$',    # "## 1." 단순 번호
        r'^-{3,}$',                 # "---" 구분선
        r'^\*{3,}$',                # "***" 구분선
    ]

    for pattern in meaningless_patterns:
        if re.match(pattern, stripped):
            return False
    return True
```

**설정 추가** (`config.py`):
```python
MIN_CHUNK_SIZE = 50  # 최소 청크 크기 (문자)
```

---

### 2.3 테이블 컨텍스트(table_context) NULL 문제

**원인**: 테이블 앞에 헤딩이나 관련 텍스트가 없는 경우 컨텍스트 추출 실패

**해결**: 테이블 헤더에서 컨텍스트 추출하는 2차 로직 추가

```python
def extract_context_from_table_headers(headers: List[str]) -> Optional[str]:
    """테이블 헤더에서 컨텍스트 추출"""
    if not headers:
        return None

    generic_headers = {'구분', '순번', '번호', '비고', 'No', 'NO', '순위'}
    meaningful_headers = [h for h in headers if h.strip() and h.strip() not in generic_headers]

    if not meaningful_headers:
        return None

    context_parts = meaningful_headers[:3]
    return ' / '.join(context_parts)
```

**검증 결과**:
```
=== 테이블 컨텍스트 현황 ===
  전체 테이블: 82개
  컨텍스트 있음: 82개
  컨텍스트 없음: 0개
```

---

### 2.4 테이블 자연어 변환 시 구조 손실 문제

**원인**: 복잡한 테이블(병합 셀, 다중 헤더)을 자연어로 변환하면 정보 손실 발생

**문제 예시** (자연어 변환 후):
```
신혼부부·한부모가족의 대학생, 청년(소득無)은(는) 공급형입니다.
신혼부부·한부모가족의 대학생, 청년(소득無)은(는) 공급대상입니다.
```
→ 컬럼 정렬이 틀려서 의미없는 문장 생성

**해결**: 원본 마크다운 유지 방식으로 변경

```python
def process_table_preserve_markdown(table_markdown: str, context_title: str = None) -> ProcessedTable:
    """마크다운 테이블을 원본 그대로 유지"""
    headers, rows = parse_markdown_table(table_markdown)

    if context_title:
        content = f"## {context_title}\n\n{table_markdown}"
    else:
        content = table_markdown

    return ProcessedTable(
        original_markdown=table_markdown,
        natural_text=content,
        row_texts=[],
        headers=headers,
        context_title=context_title
    )
```

---

### 2.5 테이블 분할 시 헤더 손실 문제

**원인**: 큰 테이블을 여러 청크로 분할할 때 첫 청크에만 헤더 포함

**해결**: 모든 청크에 헤더 반복 추가

```python
def chunk_table(table_text, context_title=None, max_size=MAX_TABLE_SIZE, header_lines=None):
    # 헤더 추출
    if header_lines:
        header_text = header_lines
    else:
        # 자동 추출: 헤더 행 + 구분선까지
        ...

    # 각 청크에 헤더 포함
    for line in data_lines:
        if current_size + line_size + header_size <= max_size:
            current_chunk.append(line)
        else:
            # 청크 저장 시 헤더 포함
            chunk_content = header_text + '\n' + '\n'.join(current_chunk)
            if context_title:
                chunk_content = f"## {context_title}\n\n{chunk_content}"
            chunks.append(chunk_content)
```

**검증 결과** (분할된 테이블):
```
=== 청크 1 ===
## 입주자격 테이블

| 구분 | 신청자격 | 소득기준 | 자산기준 |
|------|----------|----------|----------|
| 신혼부부 | 혼인기간 7년 이내 | ... |
| 생애최초 | 무주택 세대구성원 | ... |

=== 청크 2 ===
## 입주자격 테이블

| 구분 | 신청자격 | 소득기준 | 자산기준 |
|------|----------|----------|----------|
| 장애인 | 장애인증명서 소지자 | ... |
```
→ 각 청크에 헤더가 보존됨

---

## 3. LlamaParse 테이블 품질 문제 해결 (하이브리드 방식)

### 3.1 문제 분석

**문제**: 복잡한 테이블(병합 셀, 다중 헤더)이 마크다운으로 변환될 때 구조가 깨짐

**LlamaParse 변환 결과** (16개 컬럼으로 깨짐):
```markdown
| 공급형 | 공급대상 | | 기본 임대조건 | | | 전환가능 | 최대 전환시 | | | | | | | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | 임대보증금 | 월 임대료 | 보증금 | 계 | 계약금(5%) | 잔금(95%) | 한도액 | 임대보증금 | 월임대료 |
```
→ 병합 셀이 빈 셀로 처리되어 컬럼 정렬 불일치

### 3.2 해결: LlamaParse + Camelot 하이브리드 방식

**구현**: `camelot_table_extractor.py` 모듈 추가

```python
# Camelot으로 테이블 추출
tables = camelot.read_pdf(
    str(pdf_path),
    pages="all",
    flavor="lattice",
    copy_text=['v', 'h']  # 병합 셀 텍스트 수직/수평 복사
)
```

**핵심 기능**:
- `detect_header_rows()`: 다중 헤더 행 자동 감지
- `merge_header_rows()`: 다중 헤더를 단일 헤더로 병합
- `dataframe_to_markdown()`: DataFrame → 마크다운 변환

**document_parser.py 통합**:
```python
USE_CAMELOT_FOR_TABLES = True

def parse_pdf(file_path, external_id, use_camelot=None):
    # LlamaParse로 텍스트/테이블 추출
    ...
    # Camelot으로 테이블 대체
    if use_camelot:
        elements = replace_tables_with_camelot(file_path, elements)
```

### 3.3 개선 결과

**Camelot 변환 결과** (9개 컬럼, 99.5% 정확도):
```markdown
| 공급형 | 공급대상 | 기본 임대조건 - 임대보증금 - 계 | ... | 최대 전환시 - 월임대료 |
|---|---|---|---|---|
| 16 | 대학생,<br>청년(소득無)<br>청년(소득有)<br>고령자 | 18,020,000<br>19,080,000<br>20,140,000 | ... | 62,080<br>123,330<br>60,930 |
```

**검증 결과**:
```
추출된 테이블 수: 78개
  - Camelot 테이블: 67개 (정확도 70% 이상)
  - LlamaParse 테이블: 11개 (Camelot 추출 실패)
```

### 3.4 설정

`document_parser.py`:
```python
USE_CAMELOT_FOR_TABLES = True  # 하이브리드 모드 활성화
```

Camelot 최소 정확도: 70% (이하면 LlamaParse 테이블 사용)

---

## 4. 검색 테스트 결과

### 4.1 하이브리드 검색 테스트

**쿼리**: "신혼부부 소득기준"

**결과**:
```
--- 결과 #1 (유사도: 0.5626) ---
  출처: 화성시_행복주택_입주자격완화_예비입주자_모집공고문
  내용:
  ## 3-3. 신혼부부·한부모가족 계층

  | 구분 | 가구원수 | 일반조건 (1순위) | | 월평균소득금액 | 완화조건 (2순위) | 완화조건 (3순위) |
  |---|---|---|---|---|---|---|
  | 신혼부부·한부모가족 | 2인 | 5,957,283원 이하 | 110% | 7,040,426원 이하 | 130% | |
  | | 3인 | 7,198,649원 이하 | 100% | 8,638,379원 이하 | 120% | |
  ...

--- 결과 #2 (유사도: 0.5190) ---
  출처: 화성시_행복주택_입주자격완화_예비입주자_모집공고문
  내용:
  ## 공급대상 및 일반조건

  | 공급대상 | 일반조건 |
  |---|---|
  | 청년 | 소득이 있는 업무에 종사한 기간 5년 이내 |
  | 신혼부부 | 혼인기간 7년 이내 |
  ...
```

---

## 5. 최종 DB 현황

### 5.1 테스트 데이터 (PDF 2개)

```
announcements 테이블: 2개
document_chunks 테이블: 374개
```

### 5.2 청크 타입 분포

- 텍스트 청크: ~292개
- 테이블 청크: 82개

### 5.3 페이지 분포
- 1~49 페이지에 걸쳐 분포 (정상)

---

## 6. 설정 값 요약

### config.py
```python
# 임베딩 설정
EMBEDDING_MODEL_NAME = 'text-embedding-3-small'
EMBEDDING_DIMENSION = 1536

# 청킹 설정
MIN_CHUNK_SIZE = 50       # 최소 청크 크기 (문자)
OPTIMAL_CHUNK_SIZE = 600  # 최적 청크 크기 (토큰)
MAX_CHUNK_SIZE = 1200     # 최대 청크 크기 (토큰)
CHUNK_OVERLAP = 150       # 청크 오버랩 (토큰)
MAX_TABLE_SIZE = 3000     # 테이블 최대 크기 (토큰)

# 처리 설정
BATCH_SIZE = 10
MAX_WORKERS = 4
```

---

## 7. 참고 자료

- [LlamaParse Documentation](https://docs.llamaindex.ai/en/stable/llama_cloud/llama_parse/)
- [Camelot - Advanced Usage](https://camelot-py.readthedocs.io/en/master/user/advanced.html)
- [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)
- [img2table GitHub](https://github.com/xavctn/img2table)

---

## 8. 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2024-12-03 | 초기 파이프라인 리뷰 |
| 2024-12-03 | 페이지 번호 추출 방식 수정 (load_data → get_json_result) |
| 2024-12-03 | 청크 유효성 검사 추가 (is_valid_chunk) |
| 2024-12-03 | 테이블 컨텍스트 추출 개선 (헤더 기반 2차 추출) |
| 2024-12-03 | 테이블 원본 마크다운 유지 방식으로 변경 |
| 2024-12-03 | 테이블 청킹 시 헤더 보존 로직 추가 |
| 2025-12-03 | Camelot 기반 하이브리드 테이블 추출 구현 (`camelot_table_extractor.py`) |
| 2025-12-03 | document_parser.py에 LlamaParse + Camelot 하이브리드 모드 통합 |

---

## 9. 파일 구조

```
lab/kjm/
├── config.py                   # 설정 (DB, API 키, 청킹 파라미터)
├── document_parser.py          # LlamaParse + Camelot 하이브리드 파싱
├── camelot_table_extractor.py  # Camelot 테이블 추출 모듈 (NEW)
├── pdf_filter.py               # 공고 PDF 필터링
├── table_processor.py          # 마크다운 테이블 처리
├── chunker.py                  # 텍스트/테이블 청킹
├── embedder.py                 # OpenAI 임베딩 생성
├── db_handler.py               # PostgreSQL + pgvector 연동
├── db_loader.py                # CSV 메타데이터 및 청크 DB 적재
├── pipeline.py                 # 전체 오케스트레이션
└── PIPELINE_REVIEW.md          # 이 문서
```
