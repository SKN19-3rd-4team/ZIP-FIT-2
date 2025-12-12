# Git 병합 및 크롤러 업데이트 가이드

## 1. 현재 상황 분석

### 변경된 파일 확인
우리가 수정한 파일들:
- `zf_django/config/settings.py`: 설정 통합
- `zf_django/config/urls.py`: URL 라우팅 수정
- `zf_django/web/urls.py`: 프론트엔드 URL 추가
- `zf_django/web/views.py`: 뷰 함수 추가
- `zf_django/chatbot/views.py`: API 엔드포인트 수정
- `zf_django/chatbot/urls.py`: API URL 수정
- `zf_django/web/templates/web/*.html`: 프론트엔드 템플릿
- `zf_django/web/static/js/*.js`: 프론트엔드 JavaScript
- `zf_django/web/static/css/*.css`: 프론트엔드 CSS

### 팀원이 수정한 파일들 (예상)
- `zf_crawler/`: 크롤러 로직 수정
- `zf_django/chatbot/models.py`: 모델 수정 가능성
- `zf_django/chatbot/migrations/`: 마이그레이션 파일 추가 가능성
- 기타 백엔드 로직

## 2. Git 병합 전략

### 옵션 1: Git Pull 및 병합 (권장)

```bash
# 1. 현재 변경사항 커밋 (필요시)
git status
git add .
git commit -m "프론트엔드 통합 및 API 수정"

# 2. 원격 저장소에서 최신 코드 가져오기
git fetch origin

# 3. 현재 브랜치 확인
git branch

# 4. 원격 저장소의 변경사항 확인
git log HEAD..origin/main  # 또는 origin/master, origin/develop 등

# 5. 병합 실행
git pull origin main  # 또는 master, develop 등

# 6. 충돌 발생 시 해결
# 충돌 파일 확인
git status

# 충돌 파일 수정 후
git add <충돌해결한파일>
git commit -m "병합 충돌 해결"
```

### 옵션 2: Git Merge 사용

```bash
# 1. 현재 변경사항 커밋
git add .
git commit -m "프론트엔드 통합 및 API 수정"

# 2. 원격 저장소 가져오기
git fetch origin

# 3. 병합 실행
git merge origin/main  # 또는 master, develop 등

# 4. 충돌 해결
# 충돌 파일 수정 후
git add <충돌해결한파일>
git commit -m "병합 충돌 해결"
```

### 옵션 3: 새 브랜치에서 작업 (가장 안전)

```bash
# 1. 현재 변경사항 커밋
git add .
git commit -m "프론트엔드 통합 및 API 수정"

# 2. 새 브랜치 생성
git checkout -b frontend-integration-backup

# 3. 원래 브랜치로 돌아가기
git checkout main  # 또는 master, develop 등

# 4. 원격 저장소에서 최신 코드 가져오기
git pull origin main

# 5. 새 브랜치의 변경사항 병합
git merge frontend-integration-backup

# 6. 충돌 해결
```

## 3. 예상되는 충돌 및 해결 방법

### 충돌 가능성이 높은 파일들

#### 1. `zf_django/chatbot/models.py`
**충돌 원인**: 팀원이 모델 필드를 추가하거나 수정했을 수 있음

**해결 방법**:
```python
# 충돌 마커 확인
<<<<<<< HEAD
# 우리가 추가한 코드
=======
# 팀원이 추가한 코드
>>>>>>> origin/main

# 두 변경사항을 모두 유지하도록 수정
```

#### 2. `zf_django/config/settings.py`
**충돌 원인**: 설정 값이 다를 수 있음

**해결 방법**:
- 두 설정을 모두 확인하고 통합
- 환경 변수 사용 권장

#### 3. `zf_django/chatbot/views.py`
**충돌 원인**: API 로직이 다를 수 있음

**해결 방법**:
- 두 버전의 로직을 비교
- 더 최신이거나 더 완전한 로직 선택
- 필요시 두 로직 통합

### 충돌 해결 후 확인 사항

1. **마이그레이션 확인**:
```bash
cd zf_django
python manage.py makemigrations
python manage.py migrate
```

2. **서버 실행 테스트**:
```bash
python manage.py runserver
```

3. **API 테스트**:
- `http://127.0.0.1:8000/api/docs` 접속 확인
- 각 API 엔드포인트 테스트

## 4. 크롤러 업데이트 및 실행

### 크롤러 업데이트 확인

1. **크롤러 코드 확인**:
```bash
cd zf_crawler
# 변경사항 확인
git log --oneline -10
```

2. **크롤러 의존성 확인**:
```bash
# requirements.txt 확인
cat requirements.txt

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 크롤러 실행

1. **Jupyter Notebook 실행**:
```bash
cd zf_crawler
jupyter notebook
```

2. **크롤링.ipynb 열기 및 실행**:
- 각 셀을 순서대로 실행
- 에러 발생 시 확인 및 수정

3. **데이터 확인**:
```bash
# Django Shell에서 확인
cd ../zf_django
python manage.py shell

# 공고 개수 확인
from chatbot.models import AnncAll
print(AnncAll.objects.count())
```

## 5. 우리가 수정한 부분 확인 및 재적용

### 확인해야 할 파일들

1. **API 엔드포인트**:
   - `zf_django/chatbot/views.py`: `annc_list` 함수에 `annc_pblsh_dt`, `annc_deadline_dt` 추가 확인
   - `zf_django/chatbot/urls.py`: URL 패턴 확인

2. **프론트엔드 설정**:
   - `zf_django/config/settings.py`: `STATICFILES_DIRS`, `TEMPLATES` 설정 확인
   - `zf_django/config/urls.py`: URL 라우팅 확인

3. **프론트엔드 파일들**:
   - `zf_django/web/templates/web/*.html`: 템플릿 파일 확인
   - `zf_django/web/static/js/*.js`: JavaScript 파일 확인
   - `zf_django/web/static/css/*.css`: CSS 파일 확인

### 재적용이 필요한 경우

팀원의 변경사항으로 인해 우리가 수정한 부분이 덮어씌워진 경우:

1. **백업에서 복원**:
```bash
# 우리가 수정한 파일들 백업 (병합 전에 해야 함)
git diff HEAD origin/main > our_changes.patch

# 병합 후 변경사항 재적용
git apply our_changes.patch
```

2. **수동으로 재적용**:
- 변경사항을 문서화해두고 수동으로 재적용
- `lab/ohj/` 폴더의 문서 참고

## 6. 체크리스트

### Git 병합 전
- [ ] 현재 변경사항 커밋
- [ ] 백업 브랜치 생성 (선택사항)
- [ ] 변경사항 문서화

### Git 병합 중
- [ ] 원격 저장소에서 최신 코드 가져오기
- [ ] 병합 실행
- [ ] 충돌 파일 확인 및 해결

### Git 병합 후
- [ ] 마이그레이션 실행
- [ ] 서버 실행 테스트
- [ ] API 엔드포인트 테스트
- [ ] 프론트엔드 페이지 테스트

### 크롤러 실행
- [ ] 크롤러 의존성 설치
- [ ] 크롤러 실행
- [ ] 데이터 확인 (30개 정도)
- [ ] DB 필드 값 확인

### 우리 변경사항 재확인
- [ ] API 엔드포인트 확인
- [ ] 프론트엔드 설정 확인
- [ ] 프론트엔드 파일 확인
- [ ] 필요시 재적용

## 7. 문제 발생 시 대응

### 마이그레이션 오류
```bash
# 마이그레이션 파일 삭제 후 재생성 (주의: 데이터 손실 가능)
python manage.py migrate chatbot zero
python manage.py makemigrations
python manage.py migrate
```

### 서버 실행 오류
- 에러 메시지 확인
- 설정 파일 확인
- 의존성 확인

### API 오류
- API 문서 확인 (`/api/docs`)
- 로그 확인
- 데이터베이스 연결 확인

