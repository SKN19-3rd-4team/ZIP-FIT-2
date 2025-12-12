# DB 필드 확인 가이드

## 1. Django Shell을 사용한 DB 필드 확인

### 방법 1: Django Shell 사용 (권장)

```bash
# 가상환경 활성화
conda activate zipfit_env

# Django Shell 실행
cd zf_django
python manage.py shell
```

Django Shell에서 다음 명령어 실행:

```python
from chatbot.models import AnncAll

# 첫 번째 공고 조회
annc = AnncAll.objects.first()

# 필드 값 확인
print(f"annc_id: {annc.annc_id}")
print(f"annc_title: {annc.annc_title}")
print(f"annc_pblsh_dt: {annc.annc_pblsh_dt}")
print(f"annc_deadline_dt: {annc.annc_deadline_dt}")
print(f"annc_status: {annc.annc_status}")
print(f"annc_type: {annc.annc_type}")
print(f"annc_dtl_type: {annc.annc_dtl_type}")
print(f"annc_url: {annc.annc_url}")

# 모든 공고의 상태 값 확인
statuses = AnncAll.objects.values_list('annc_status', flat=True).distinct()
print(f"고유한 annc_status 값들: {list(statuses)}")

# 모든 공고의 유형 값 확인
types = AnncAll.objects.values_list('annc_type', flat=True).distinct()
print(f"고유한 annc_type 값들: {list(types)}")

dtl_types = AnncAll.objects.values_list('annc_dtl_type', flat=True).distinct()
print(f"고유한 annc_dtl_type 값들: {list(dtl_types)}")
```

### 방법 2: DBeaver 사용

1. DBeaver 실행
2. PostgreSQL 연결
3. 다음 SQL 쿼리 실행:

```sql
-- 첫 번째 공고의 모든 필드 확인
SELECT 
    annc_id,
    annc_title,
    annc_pblsh_dt,
    annc_deadline_dt,
    annc_status,
    annc_type,
    annc_dtl_type,
    annc_url,
    created_dttm
FROM annc_all
LIMIT 5;

-- 고유한 상태 값 확인
SELECT DISTINCT annc_status 
FROM annc_all 
ORDER BY annc_status;

-- 고유한 유형 값 확인
SELECT DISTINCT annc_type 
FROM annc_all 
ORDER BY annc_type;

-- 고유한 상세 유형 값 확인
SELECT DISTINCT annc_dtl_type 
FROM annc_all 
ORDER BY annc_dtl_type;
```

## 2. 필드 의미 확인

### annc_pblsh_dt (게시일)
- **의미**: 공고가 게시된 날짜
- **확인 필요**: 이 필드가 "공고일"인지 "접수 시작일"인지 확인
- **크롤러 코드 확인**: `zf_crawler/src/crawler/lh.py`에서 `post_date_str`로 설정됨

### annc_deadline_dt (마감일)
- **의미**: 공고 마감일 또는 접수 종료일
- **확인 필요**: 이 필드가 "접수 종료일"인지 확인
- **크롤러 코드 확인**: `zf_crawler/src/crawler/lh.py`에서 `cols[6]`로 설정됨

### annc_status (공고 상태)
- **확인 필요**: DB에 저장된 값이 프론트엔드 필터 값과 일치하는지 확인
- **예상 값**: "공고중", "접수중", "마감", "공고예정", "정정공고중" 등

### annc_type vs annc_dtl_type
- **annc_type**: 공고 유형 (예: "임대", "분양")
- **annc_dtl_type**: 공고 유형 상세 (예: "영구임대", "행복주택")
- **확인 필요**: 프론트엔드에서 어떤 필드를 사용해야 하는지 확인

## 3. 실제 데이터 확인 예시

사용자가 언급한 공고들:

### 공고 1: [정정공고]양주회천 A25BL 영구임대주택 입주자 모집공고
- 실제 공고일: 2025.11.27
- 실제 접수기간: 2025.12.15 ~ 2025.12.19
- DB에서 확인:
```sql
SELECT annc_pblsh_dt, annc_deadline_dt, annc_status, annc_type, annc_dtl_type
FROM annc_all
WHERE annc_title LIKE '%양주회천%';
```

### 공고 2: 양주시, 동두천시 행복주택 상시모집
- 실제 공고일: 2025.05.28
- 실제 접수기간: 2025.06.19 ~ 2025.12.31
- DB에서 확인:
```sql
SELECT annc_pblsh_dt, annc_deadline_dt, annc_status, annc_type, annc_dtl_type
FROM annc_all
WHERE annc_title LIKE '%양주시%동두천시%';
```

## 4. 확인 후 조치 사항

### annc_pblsh_dt가 "공고일"인 경우
- 접수 시작일을 별도로 저장하는 필드가 있는지 확인 필요
- 없으면 크롤러에서 접수 시작일을 추출하여 저장하도록 수정 필요

### annc_pblsh_dt가 "접수 시작일"인 경우
- 현재 로직 수정 불필요
- `getRecruitmentPeriod` 함수가 올바르게 작동함

### annc_status 값이 프론트엔드와 다른 경우
- 백엔드에서 매핑 로직 추가 필요
- 또는 프론트엔드에서 매핑 로직 추가 필요

### annc_type vs annc_dtl_type
- 프론트엔드에서 `annc_dtl_type`을 사용하도록 수정 필요
- 또는 백엔드에서 `annc_dtl_type`을 `annc_type`으로 매핑 필요

## 결과 공유

- cmd 결과 공유
```cmd
annc_id: 1
annc_title: 양주시, 동두천시 행복주택 상시모집[선착순동호지정, 입주자격완화, 선계약후검증]
annc_pblsh_dt: 2025.05.28
annc_deadline_dt: 2025.12.31
annc_status: 공고중
annc_type: 임대
annc_dtl_type: 행복주택
annc_url: https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018161&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=10
고유한 annc_status 값들: ['공고중']
고유한 annc_type 값들: ['임대']
고유한 annc_dtl_type 값들: ['영구임대', '행복주택']
```

- DBeaver 결과 공유, 공고1


|annc_pblsh_dt|	annc_deadline_dt|	annc_status|	annc_type|	annc_dtl_type|
|---|---|---|---|---|
|2025.12.02|	2025.12.19|	공고중|	임대|	영구임대|

- DBeaver 결과 공유, 공고2


|annc_pblsh_dt|	annc_deadline_dt|	annc_status|	annc_type|	annc_dtl_type|
|---|---|---|---|---|
|2025.05.28|	2025.12.31|	공고중|	임대|	행복주택|

## 공유한 결과를 바탕으로 최적의 문제 해결 방안을 제공 바람.