# 환경 설정 FAQ

> **팀원 협의를 위한 질문 및 답변**

---

## Q1: .env 파일 위치

**질문**: root 바로 아래 있는 .env 파일을 그대로 가져다 쓰면 안되는가? 굳이 figma_django 하위 폴더에 따로 .env를 만들어야하는가?

**답변**: → **옵션 A 로 진행할 것**

### 옵션 A: Root의 .env 사용 (권장)

**장점**:
- 팀원들이 공통으로 사용하는 .env 파일 하나만 관리
- 프로젝트 간 환경 변수 공유 가능
- 중복 관리 불필요

**구현 방법**:
```python
# config/settings.py
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent  # ZIP-FIT-2 루트

# Root의 .env 파일 사용
from decouple import Config, RepositoryEnv
env_file = PROJECT_ROOT / '.env'
config = Config(RepositoryEnv(env_file)) if env_file.exists() else config()
```

### 옵션 B: 각 프로젝트별 .env 사용

**장점**:
- 프로젝트별 독립적인 환경 변수 관리
- 프로젝트 이동 시 환경 변수 함께 이동

**단점**:
- 중복 관리 필요
- 팀원 간 동기화 필요

**결론**: **옵션 A (Root의 .env 사용) 권장**
- 팀원들과 협의하여 결정
- Root에 `.env` 파일이 있다면 그것을 사용하도록 설정 가능

---

## Q2: requirements.txt 위치

**질문**: requirements.txt도 마찬가지로 root의 것을 사용할 수 있는가?

**답변**: → **옵션 A로 진행할 것**

### 옵션 A: Root의 requirements.txt 사용

**장점**:
- 팀원들이 공통으로 사용하는 의존성 관리
- 프로젝트 간 의존성 공유

**단점**:
- 프로젝트별로 다른 의존성 버전 관리 어려움

### 옵션 B: 각 프로젝트별 requirements.txt 사용 (현재 방식)

**장점**:
- 프로젝트별 독립적인 의존성 관리
- 프로젝트 이동 시 의존성 정보 함께 이동
- 버전 충돌 방지

**결론**: **옵션 B (각 프로젝트별) 권장**
- 프로젝트별로 다른 의존성 버전이 필요할 수 있음
- 하지만 팀원들과 협의하여 결정 가능

---

## Q3: .gitignore 위치

**질문**: .gitignore도 마찬가지인가?

**답변**:

### 옵션 A: Root의 .gitignore 사용

**장점**:
- 팀원들이 공통으로 사용하는 ignore 규칙
- 일관된 Git 관리

**단점**:
- 프로젝트별 특수 파일 무시 어려움

### 옵션 B: 각 프로젝트별 .gitignore 사용 (현재 방식)

**장점**:
- 프로젝트별 특수 파일 무시 가능
- 프로젝트 이동 시 ignore 규칙 함께 이동

**결론**: **옵션 B (각 프로젝트별) 권장**
- 하지만 Root의 .gitignore에 공통 규칙 추가 가능
- 두 가지 모두 사용 가능 (Git은 상위 .gitignore도 읽음)

---

## Q4: 폴더 깊이 문제

**질문**: 폴더 깊이 등 나중에 옮길 때 문제가 안되어야 함

**답변**:

**해결 방법**: 상대 경로 사용

```python
# config/settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR은 항상 프로젝트 루트(figma_django)를 가리킴

# 프로젝트가 어디로 이동하든 상대 경로로 동작
STATICFILES_DIRS = [
    BASE_DIR / 'web' / 'static',
]
```

**확인 사항**:
- ✅ 모든 경로가 `BASE_DIR` 기준 상대 경로 사용
- ✅ 절대 경로 사용하지 않음
- ✅ 하드코딩된 경로 없음

---

## 팀원 협의 필요 사항

### 1. .env 파일 위치
- [v] Root의 .env 사용할지
- [ ] 각 프로젝트별 .env 사용할지

### 2. requirements.txt 위치
- [v] Root의 requirements.txt 사용할지
- [ ] 각 프로젝트별 requirements.txt 사용할지

### 3. .gitignore 위치
- [v] Root의 .gitignore만 사용할지
- [ ] 각 프로젝트별 .gitignore도 사용할지

---

**작성일**: 2025-01-20  
**상태**: 팀원 협의 필요 ⚠️

