# 모델 Import 질문 답변

## 질문 1: merge 후 문제 해결 여부

**답변: 네, merge 후에는 문제가 자연스럽게 해결됩니다.**

**이유:**
- `figma_django`를 `zf_django`로 merge하면 `'chatbot'` 앱이 하나만 존재합니다.
- Django가 `zf_django/chatbot/models.py`만 로드하므로 모듈 충돌이 없습니다.
- `INSTALLED_APPS`에 `'chatbot'`이 하나만 등록되므로 Django가 올바른 모델을 로드합니다.

**merge 후 예상 구조:**
```
zf_django/
  chatbot/
    models.py  # AnncAll, AnncLhTemp 등 모든 모델 포함
  config/
    settings.py  # INSTALLED_APPS = [..., 'chatbot', ...]
```

## 질문 2: 절대 경로 방식이 merge 후에도 문제없는지

**답변: merge 후에는 이 코드를 제거해도 됩니다.**

**이유:**
- merge 후에는 `from chatbot.models import AnncAll`로 직접 import 가능합니다.
- 절대 경로 방식은 임시 해결책입니다.
- merge 후에는 일반적인 Django 방식으로 사용할 수 있습니다.

**merge 후 코드:**
```python
# merge 후에는 이렇게 간단하게 사용 가능
from chatbot.models import AnncAll
```

## 질문 3: 이전에는 왜 문제가 없었는지

**가능한 이유들:**

1. **이전에는 `AnncLhTemp` 모델이 없었을 수 있습니다.**
   - `zf_django/chatbot/models.py`에 `AnncLhTemp`가 추가되기 전에는 문제가 없었을 수 있습니다.

2. **이전에는 다른 방식으로 import했을 수 있습니다.**
   - 예: `zf_django`의 `INSTALLED_APPS`에 `'chatbot'`을 추가했거나
   - 예: 다른 경로 설정을 사용했을 수 있습니다.

3. **이전에는 Django 설정이 다르게 되어 있었을 수 있습니다.**
   - `figma_django/config/settings.py`의 `INSTALLED_APPS` 설정이 달랐을 수 있습니다.

**확인 방법:**
- 이전에 작동했던 코드나 설정을 확인해보면 정확한 이유를 알 수 있습니다.

## 질문 4: 지금도 같은 오류가 나오는 것 같다

**현재 문제:**
```
RuntimeError: Model class zf_django_chatbot_models.AnncLhTemp doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
```

**원인:**
- `zf_django/chatbot/models.py`를 직접 로드하면 파일 안의 모든 모델(`AnncLhTemp`, `AnncAll` 등)이 로드됩니다.
- `AnncLhTemp`가 먼저 정의되어 있고, Django가 이 모델을 검증하려고 하는데 `INSTALLED_APPS`에 등록되지 않아서 에러가 발생합니다.

**해결 방법:**
- Django의 모델 검증을 우회하여 모델을 로드합니다.
- 또는 `AnncLhTemp`에 `app_label`을 명시적으로 설정합니다.

## 최종 해결 방안

### 방법 1: 모델 검증 우회 (현재 구현)
- Django의 모델 생성자를 임시로 패치하여 검증을 우회합니다.
- `AnncAll`만 정상적으로 처리하고, 다른 모델은 검증을 건너뜁니다.

### 방법 2: AnncLhTemp에 app_label 추가 (권장)
- `zf_django/chatbot/models.py`의 `AnncLhTemp` 모델에 `app_label`을 추가합니다.
- 이 방법이 더 깔끔하고 안전합니다.

```python
class AnncLhTemp(models.Model):
    # ... 필드 정의 ...
    
    class Meta:
        app_label = 'chatbot'  # 이 줄 추가
        db_table = 'annc_lh_temp'
```

### 방법 3: Django 앱 레지스트리 사용
- Django의 `apps` 레지스트리를 사용하여 모델을 가져옵니다.
- 하지만 이것도 `INSTALLED_APPS`에 등록되어 있어야 합니다.

## 권장 사항

1. **단기 해결책:** 현재 구현한 모델 검증 우회 방법 사용
2. **중기 해결책:** `AnncLhTemp`에 `app_label` 추가 (zf_django 팀과 협의)
3. **장기 해결책:** `figma_django`를 `zf_django`로 merge 후 일반적인 Django 방식 사용

## 결론

- merge 후에는 문제가 자연스럽게 해결됩니다.
- 현재 방법은 임시 해결책이며, merge 후에는 제거해도 됩니다.
- 이전에 문제가 없었던 이유는 `AnncLhTemp` 모델이 없었거나 다른 설정을 사용했기 때문일 수 있습니다.
- 현재 오류는 `AnncLhTemp` 모델의 검증 문제이며, 모델 검증 우회 방법으로 해결할 수 있습니다.

