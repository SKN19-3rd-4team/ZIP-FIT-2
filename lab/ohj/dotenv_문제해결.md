# dotenv 모듈 오류 해결 가이드

> **Jupyter Notebook에서 `No module named 'dotenv'` 오류 해결**

---

## 🔍 문제 분석

### 오류 원인
1. **Jupyter Notebook이 다른 Python 환경 사용**
   - 시스템 Python 사용 중
   - 가상환경이 Jupyter에 등록되지 않음

2. **`.env` 파일 위치와는 무관**
   - `.env` 파일이 없어도 `dotenv` 모듈은 import 가능해야 함
   - `.env` 파일이 없으면 환경 변수만 로드되지 않을 뿐

---

## ✅ 해결 방법

### 방법 1: Jupyter Notebook 셀에서 직접 설치 (가장 빠름)

**크롤링.ipynb 첫 번째 셀에 추가**:
```python
# dotenv 모듈 설치 (한 번만 실행)
import sys
import subprocess

try:
    import dotenv
    print("✅ dotenv 모듈 이미 설치됨")
except ImportError:
    print("📦 dotenv 모듈 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    print("✅ dotenv 모듈 설치 완료")
    import importlib
    importlib.reload(sys.modules.get('dotenv', None))
```

**그 다음 셀에서**:
```python
from dotenv import load_dotenv
load_dotenv()
print("✅ dotenv 로드 성공")
```

---

### 방법 2: .env 파일 위치 확인

**`.env` 파일은 프로젝트 루트에 있어야 함**:
```
C:\SKN_19\ZIP-FIT-2\.env  ← 여기에 있어야 함
```

**`.env` 파일 내용 예시**:
```env
# Django Secret Key
DJANGO_SECRET_KEY=django-insecure-0#z1rbplff)#c)84_zcg^5ex#p(j)ibh*g%%_dfpai(s9@^tf@

# PostgreSQL Database 설정
DB_HOST=localhost
DB_PORT=5432
DB_USER=zf_admin
DB_PASSWORD=zf_pwd1
DB_NAME=zf_db

# API 설정
API_BASE_URL=http://localhost:8000
```

**주의**: `DJANGO_SECRET_KEY`가 주석 처리되어 있어도 `dotenv` 모듈 오류와는 무관합니다.

---

### 방법 3: Jupyter Notebook 가상환경 설정

**터미널에서 실행**:
```bash
conda activate zipfit_env
pip install ipykernel python-dotenv
python -m ipykernel install --user --name zipfit_env --display-name "Python (zipfit_env)"
```

**Jupyter Notebook에서**:
- `Kernel` → `Change Kernel` → `Python (zipfit_env)` 선택

---

## 🔍 현재 상태 확인

**Jupyter Notebook 셀에서 실행**:
```python
import sys
print("Python 경로:", sys.executable)
print("Python 버전:", sys.version)

# dotenv 모듈 확인
try:
    import dotenv
    print("✅ dotenv 모듈 사용 가능")
    print("dotenv 경로:", dotenv.__file__)
except ImportError as e:
    print("❌ dotenv 모듈 없음:", e)
    print("현재 Python:", sys.executable)
```

---

## 📝 크롤링.ipynb 수정 예시

**첫 번째 셀 (환경 변수 로드 전에 추가)**:
```python
# ============================================
# 0. 환경 설정 및 패키지 설치 확인
# ============================================
import sys
import subprocess
import os
from pathlib import Path

# dotenv 모듈 설치 확인 및 설치
try:
    import dotenv
    print("✅ dotenv 모듈 사용 가능")
except ImportError:
    print("📦 dotenv 모듈 설치 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv", "-q"])
    import dotenv
    print("✅ dotenv 모듈 설치 완료")

# .env 파일 위치 확인
project_root = Path.cwd().parent if Path.cwd().name == 'zf_crawler' else Path.cwd()
env_file = project_root / '.env'

if env_file.exists():
    print(f"✅ .env 파일 발견: {env_file}")
else:
    print(f"⚠️ .env 파일 없음: {env_file}")
    print("환경 변수는 시스템 환경 변수에서 로드됩니다.")

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv(env_file if env_file.exists() else None)

print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"프로젝트 루트: {project_root}")
```

---

## ⚠️ 주의 사항

### 1. .env 파일 위치
- `.env` 파일은 **프로젝트 루트** (`C:\SKN_19\ZIP-FIT-2\.env`)에 있어야 함
- `zf_crawler` 폴더에 있을 필요 없음
- `load_dotenv()`는 상위 디렉토리도 자동으로 검색함

### 2. DJANGO_SECRET_KEY 주석 처리
- `.env` 파일에서 `DJANGO_SECRET_KEY`가 주석 처리되어 있어도 `dotenv` 모듈 오류와는 무관
- `dotenv` 모듈 자체를 찾지 못하는 것이 문제

### 3. Jupyter Notebook 커널
- Jupyter Notebook이 어떤 Python을 사용하는지 확인 필요
- 가상환경이 제대로 등록되지 않았을 수 있음

---

## 💡 빠른 해결 (권장)

**크롤링.ipynb 첫 번째 셀에 다음 코드 추가**:
```python
import sys
!{sys.executable} -m pip install python-dotenv -q
```

**그 다음 셀**:
```python
from dotenv import load_dotenv
load_dotenv()
```

**커널 재시작 후 테스트**

---

**작성일**: 2025-01-20  
**상태**: dotenv 모듈 오류 해결 가이드 작성 완료

