# 서버 실행 FAQ

> **자주 묻는 질문**: 여러 Django 프로젝트를 동시에 실행하는 방법

---

## ❓ 질문: 같은 포트에서 두 개의 서버를 실행할 수 있나요?

### 답변: **아니요, 불가능합니다**

**이유**:
- 포트는 하나의 프로세스만 사용할 수 있습니다
- `zf_django`와 `figma_django` 모두 기본적으로 포트 8000을 사용합니다
- 같은 포트에서 두 서버를 실행하려고 하면 **"Port 8000 is already in use"** 오류가 발생합니다

---

## ✅ 해결 방법

### 방법 1: 기존 서버 종료 후 새 서버 실행 (권장)

**장점**: 
- 포트 충돌 없음
- 리소스 절약
- 간단함

**단계**:
```bash
# 1. 기존 서버 종료 (Ctrl + C)
# 2. figma_django 폴더로 이동
cd figma_django

# 3. 가상환경 활성화 (필요시)
conda activate zipfit_env

# 4. 새 서버 실행
python manage.py runserver
```

---

### 방법 2: 다른 포트로 실행 (두 서버 동시 실행)

**장점**:
- 두 서버를 동시에 실행 가능
- 각각 다른 프로젝트 테스트 가능

**단계**:

#### 터미널 1 (zf_django - 기존 유지)
```bash
# zf_django 폴더에서
cd zf_django
python manage.py runserver 8000
# 접속: http://127.0.0.1:8000/
```

#### 터미널 2 (figma_django - 새로 실행)
```bash
# figma_django 폴더로 이동
cd figma_django

# 가상환경 활성화 (필요시)
conda activate zipfit_env

# 다른 포트로 실행
python manage.py runserver 8001
# 접속: http://127.0.0.1:8001/
```

**접속 URL**:
- `zf_django`: http://127.0.0.1:8000/
- `figma_django`: http://127.0.0.1:8001/

---

## 🔍 현재 상황 확인

### 현재 실행 중인 서버 확인

**Windows PowerShell에서**:
```powershell
# 포트 8000을 사용하는 프로세스 확인
netstat -ano | findstr :8000
```

**결과 예시**:
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       12345
```

**프로세스 종료** (필요시):
```powershell
# PID가 12345인 경우
taskkill /PID 12345 /F
```

---

## 📋 권장 워크플로우

### 시나리오 1: figma_django만 테스트할 때
```bash
# 1. 기존 서버 종료 (Ctrl + C)
# 2. figma_django로 이동 및 실행
cd figma_django
python manage.py runserver
```

### 시나리오 2: 두 프로젝트를 동시에 비교할 때
```bash
# 터미널 1: zf_django (포트 8000)
cd zf_django
python manage.py runserver 8000

# 터미널 2: figma_django (포트 8001)
cd figma_django
python manage.py runserver 8001
```

---

## ⚠️ 주의사항

1. **포트 충돌**: 같은 포트를 사용하면 오류 발생
2. **가상환경**: 각 프로젝트의 가상환경이 다를 수 있음
3. **데이터베이스**: 각 프로젝트는 독립적인 데이터베이스 사용

---

## 💡 팁

### Cursor에서 새 터미널 열기
- **Ctrl + `** (백틱) 또는
- **터미널 메뉴** → **새 터미널**

### 포트 변경이 필요한 경우
```bash
# 포트 8002로 실행
python manage.py runserver 8002

# 접속: http://127.0.0.1:8002/
```

---

**작성일**: 2025-12-10  
**최종 업데이트**: 2025-12-10

