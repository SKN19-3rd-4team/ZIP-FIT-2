# Jupyter Notebook 가상환경 설정 가이드

> **Jupyter Notebook에서 올바른 가상환경 사용하기**

---

## 🔍 문제 상황

**증상**:
- `No module named 'dotenv'` 오류 발생
- 커널 재시작해도 해결되지 않음

**원인**:
- Jupyter Notebook이 시스템 Python을 사용하고 있음
- 가상환경이 Jupyter Notebook에 등록되지 않음

---

## ✅ 해결 방법

### 방법 1: Jupyter Notebook에 가상환경 커널 등록 (권장)

**1단계: ipykernel 설치**
```bash
conda activate zipfit_env  # 또는 zf2_back
pip install ipykernel
```

**2단계: 가상환경을 Jupyter 커널로 등록**
```bash
python -m ipykernel install --user --name zipfit_env --display-name "Python (zipfit_env)"
```

**3단계: Jupyter Notebook에서 커널 선택**
- Jupyter Notebook 실행
- 상단 메뉴: `Kernel` → `Change Kernel` → `Python (zipfit_env)` 선택

---

### 방법 2: Jupyter Notebook을 가상환경에서 실행

**1단계: 가상환경 활성화**
```bash
conda activate zipfit_env
```

**2단계: Jupyter Notebook 실행**
```bash
jupyter notebook
```

**확인 방법**:
- Jupyter Notebook 첫 셀에서 실행:
```python
import sys
print(sys.executable)
# 출력이 가상환경 경로여야 함 (예: C:\Users\...\anaconda3\envs\zipfit_env\python.exe)
```

---

### 방법 3: 필요한 패키지 직접 설치

**현재 사용 중인 Python 환경에 설치**
```bash
# 현재 Python 경로 확인
python -c "import sys; print(sys.executable)"

# 해당 경로의 pip로 설치
python -m pip install python-dotenv
```

---

## 🔍 현재 Python 환경 확인

**Jupyter Notebook에서 확인**:
```python
import sys
print("Python 경로:", sys.executable)
print("Python 버전:", sys.version)

# dotenv 모듈 확인
try:
    import dotenv
    print("✅ dotenv 모듈 사용 가능")
except ImportError:
    print("❌ dotenv 모듈 없음")
```

---

## 📝 체크리스트

### Jupyter Notebook 설정
- [ ] 가상환경 활성화 확인
- [ ] `ipykernel` 설치 확인
- [ ] 가상환경 커널 등록 확인
- [ ] Jupyter Notebook에서 올바른 커널 선택

### 패키지 설치
- [ ] `python-dotenv` 설치 확인
- [ ] 올바른 Python 환경에 설치 확인

### .env 파일
- [ ] `.env` 파일 위치 확인 (Root: `C:\SKN_19\ZIP-FIT-2\.env`)
- [ ] 환경 변수 값 확인

---

## ⚠️ 주의 사항

### 1. .env 파일 위치
- `.env` 파일은 프로젝트 루트(`C:\SKN_19\ZIP-FIT-2\.env`)에 있어야 함
- `load_dotenv()`는 기본적으로 현재 디렉토리와 상위 디렉토리에서 `.env` 파일을 찾음

### 2. DJANGO_SECRET_KEY 주석 처리
- `.env` 파일에서 `DJANGO_SECRET_KEY`가 주석 처리되어 있어도 `dotenv` 모듈 오류와는 무관함
- `dotenv` 모듈 자체를 찾지 못하는 것이 문제

### 3. 여러 Python 환경
- 시스템에 여러 Python 환경이 있을 수 있음
- Jupyter Notebook이 어떤 Python을 사용하는지 확인 필요

---

## 💡 빠른 해결 방법

**즉시 해결하려면**:

1. **Jupyter Notebook 셀에서 실행**:
```python
import sys
!{sys.executable} -m pip install python-dotenv
```

2. **커널 재시작**:
- `Kernel` → `Restart Kernel`

3. **다시 테스트**:
```python
from dotenv import load_dotenv
load_dotenv()
print("✅ dotenv 로드 성공")
```

---

**작성일**: 2025-01-20  
**상태**: Jupyter Notebook 가상환경 설정 가이드 작성 완료

