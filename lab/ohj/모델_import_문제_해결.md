# 모델 Import 문제 해결 및 공고 유형 필터 확인

## 문제 분석

### 1. 모델 Import 실패 문제

**원인:**
- Django 모델은 `INSTALLED_APPS`에 등록되어야 Django가 인식합니다.
- `importlib.util`로 직접 모듈을 로드하면 Django가 모델을 인식하지 못합니다.
- `zf_django.chatbot`이 `figma_django`의 `INSTALLED_APPS`에 없어서 모델을 사용할 수 없습니다.

**해결 방법:**
- Django의 `connection` 객체를 사용하여 직접 SQL 쿼리 실행
- 모델 import 없이도 DB에 접근 가능
- `figma_django/chatbot/views.py`에서 `annc_list`와 `annc_summary` 함수를 SQL 쿼리 방식으로 변경

### 2. 공고 유형 필터 문제

**우려사항:**
- `mockData.js`에서 공고 유형을 세분화했습니다:
  - 영구임대주택
  - 행복주택
  - 분양주택
  - 전세임대주택
  - 매입임대주택
  - 국민임대주택
  - 통합공공임대주택

- 실제 DB의 `annc_type` 필드 값이 이와 정확히 일치하지 않을 수 있습니다.

**해결 방법:**
- SQL 쿼리에서 `ILIKE`를 사용하여 부분 일치 검색
- 예: `annc_type ILIKE '%영구임대%'` → "영구임대주택", "영구임대", "영구임대주택 입주자 모집" 등 모두 매칭
- 프론트엔드 필터와 실제 DB 값의 차이를 자동으로 처리

## 수정 사항

### 1. `figma_django/chatbot/views.py` 수정

**변경 전:**
```python
from zf_django.chatbot.models import AnncAll
# ...
queryset = AnncAll.objects.filter(annc_type=annc_type)
```

**변경 후:**
```python
from django.db import connection
# ...
cursor.execute(
    "SELECT * FROM annc_all WHERE annc_type ILIKE %s",
    [f'%{annc_type}%']
)
```

### 2. 공고 유형 필터링 로직

**SQL 쿼리:**
```python
if annc_type and annc_type != '전체':
    # 부분 일치 검색으로 처리
    where_conditions.append("annc_type ILIKE %s")
    params.append(f'%{annc_type}%')
```

이렇게 하면:
- 프론트엔드에서 "영구임대주택"을 선택하면
- DB의 "영구임대주택", "영구임대", "영구임대주택 입주자 모집" 등이 모두 매칭됩니다.

## 마이그레이션 문제

**질문:** 마이그레이션을 실행해야 하나요?

**답변:**
- `figma_django`는 `zf_django`와 같은 PostgreSQL DB를 사용합니다.
- `zf_django`에서 이미 마이그레이션을 실행했다면, `figma_django`에서도 동일한 테이블을 사용합니다.
- 따라서 `figma_django`에서 마이그레이션을 실행할 필요는 없습니다.

**하지만:**
- Django 기본 앱들(`admin`, `auth`, `contenttypes`, `sessions`)의 마이그레이션은 필요할 수 있습니다.
- 이는 `figma_django`의 자체 기능(관리자 페이지 등)을 사용하기 위함입니다.

**권장 사항:**
- 개발 중에는 마이그레이션 경고를 무시해도 됩니다.
- 나중에 관리자 페이지를 사용하려면 마이그레이션을 실행하세요:
  ```bash
  cd figma_django
  python manage.py migrate
  ```

## 다음 단계

1. **서버 재시작**
   ```bash
   cd figma_django
   python manage.py runserver 8000
   ```

2. **터미널 로그 확인**
   - `[DEBUG] Using direct database connection for AnncAll queries` 메시지 확인
   - `[DEBUG] annc_list: total_count=2` 메시지 확인
   - `[DEBUG] annc_list: sample annc_type values: [...]` 메시지로 실제 DB의 `annc_type` 값 확인

3. **브라우저에서 테스트**
   - `http://127.0.0.1:8000/main/` → 통계 숫자 확인
   - `http://127.0.0.1:8000/list/` → 공고 목록 확인
   - 공고 유형 필터 테스트

4. **실제 DB의 `annc_type` 값 확인**
   - 서버 터미널의 `[DEBUG] annc_list: sample annc_type values` 로그 확인
   - 필요시 프론트엔드 필터 옵션 조정

