# DB 필드 분석 및 해결 방안

## 1. DB 필드 확인 결과 분석

### 공고 1: [정정공고]양주회천 A25BL 영구임대주택 입주자 모집공고
| 필드 | DB 값 | 실제 값 | 분석 |
|------|-------|---------|------|
| annc_pblsh_dt | 2025.12.02 | 공고일: 2025.11.27 | 정정공고일로 보임 (원본 공고일 아님) |
| annc_deadline_dt | 2025.12.19 | 접수 종료일: 2025.12.19 | ✅ 일치 |
| annc_status | 공고중 | 공고중 | ✅ 일치 |
| annc_type | 임대 | 임대 | ✅ 일치 |
| annc_dtl_type | 영구임대 | 영구임대 | ✅ 일치 |

### 공고 2: 양주시, 동두천시 행복주택 상시모집
| 필드 | DB 값 | 실제 값 | 분석 |
|------|-------|---------|------|
| annc_pblsh_dt | 2025.05.28 | 공고일: 2025.05.28<br>접수 시작일: 2025.06.19 | ⚠️ 접수 시작일과 다름 |
| annc_deadline_dt | 2025.12.31 | 접수 종료일: 2025.12.31 | ✅ 일치 |
| annc_status | 공고중 | 접수중 (현재 접수기간 내) | ⚠️ 상태 불일치 |
| annc_type | 임대 | 임대 | ✅ 일치 |
| annc_dtl_type | 행복주택 | 행복주택 | ✅ 일치 |

## 2. 핵심 문제 분석

### 문제 1: annc_pblsh_dt의 의미 불명확
- **현재 상황**: `annc_pblsh_dt`가 "게시일" 또는 "정정공고일"로 저장됨
- **문제점**: 접수 시작일과 다를 수 있음
  - 공고2: 게시일 2025.05.28, 접수 시작일 2025.06.19 (약 3주 차이)
- **영향**: 모집 기간 표시가 잘못될 수 있음

### 문제 2: 접수 시작일 정보 부재
- **현재 상황**: 접수 시작일을 저장하는 필드가 없음
- **문제점**: 접수기간 내에 있는지 판단 불가
- **영향**: 상태가 "공고중"인지 "접수중"인지 정확히 판단 불가

### 문제 3: annc_status가 정적
- **현재 상황**: DB에 "공고중"으로 저장됨
- **문제점**: 접수기간 내에 있어도 "공고중"으로 표시됨
- **영향**: 동적 상태 표시 불가

## 3. 크롤러 코드 분석 필요 사항

### 확인해야 할 부분
1. **크롤러에서 접수 시작일을 추출하는지 확인**
   - `zf_crawler/src/crawler/lh.py` 확인
   - LH 웹사이트에서 접수 시작일 정보 추출 가능한지 확인

2. **접수 시작일을 저장하는 필드가 있는지 확인**
   - `zf_django/chatbot/models.py`의 `AnncAll` 모델 확인
   - 접수 시작일 필드 추가 필요 여부 확인

3. **크롤러가 접수 시작일을 어디서 가져오는지 확인**
   - 공고 상세 페이지에서 추출하는지
   - 목록 페이지에서 추출하는지

## 4. 해결 방안

### 방안 1: 접수 시작일 필드 추가 (권장)

**장점**:
- 정확한 접수기간 표시 가능
- 동적 상태 판단 가능 (공고중 vs 접수중)

**단점**:
- 모델 수정 필요
- 마이그레이션 필요
- 크롤러 수정 필요

**구현 단계**:
1. `AnncAll` 모델에 `annc_recruitment_start_dt` 필드 추가
2. 크롤러에서 접수 시작일 추출 로직 추가
3. 프론트엔드에서 접수 시작일 사용하도록 수정

### 방안 2: annc_pblsh_dt를 접수 시작일로 사용 (임시)

**전제 조건**:
- `annc_pblsh_dt`가 실제로 접수 시작일인 경우에만 가능
- 현재는 게시일로 보이므로 부적합

**장점**:
- 모델 수정 불필요
- 빠른 구현 가능

**단점**:
- 정확도 낮음 (게시일과 접수 시작일이 다를 수 있음)

### 방안 3: 날짜 기반 동적 상태 계산 (현재 + 개선)

**현재 로직**:
- `annc_pblsh_dt`와 `annc_deadline_dt`를 사용하여 상태 계산
- 하지만 `annc_pblsh_dt`가 접수 시작일이 아니므로 부정확

**개선 방안**:
- 접수 시작일 정보가 없으면 `annc_pblsh_dt`를 접수 시작일로 가정
- 또는 `annc_status`를 그대로 사용하되, 날짜 기반으로 재확인

**구현**:
```javascript
// 접수 시작일이 없으면 annc_pblsh_dt를 접수 시작일로 가정
const recruitmentStartDate = annc.annc_recruitment_start_dt 
    ? parseDate(annc.annc_recruitment_start_dt)
    : parseDate(annc.annc_pblsh_dt);

// 현재 날짜가 접수기간 내에 있으면 "접수중"
if (today >= recruitmentStartDate && today <= deadlineDate) {
    return '접수중';
}
```

## 5. 즉시 적용 가능한 해결책

### 단기 해결책: 프론트엔드에서 동적 상태 계산

**로직**:
1. `annc_pblsh_dt`를 접수 시작일로 가정 (임시)
2. 현재 날짜가 `annc_pblsh_dt`와 `annc_deadline_dt` 사이에 있으면 "접수중"
3. `annc_deadline_dt`가 지났으면 "마감"
4. `annc_pblsh_dt`가 미래면 "공고예정"

**주의사항**:
- `annc_pblsh_dt`가 실제 접수 시작일이 아닐 수 있음
- 공고2의 경우: 게시일 2025.05.28, 접수 시작일 2025.06.19
- 이 경우 약 3주간 "공고중"으로 표시되어야 함

**수정 코드**:
```javascript
function getCurrentStatus(annc) {
    if (annc.annc_pblsh_dt && annc.annc_deadline_dt) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const publishDate = parseDate(annc.annc_pblsh_dt);
        const deadlineDate = parseDate(annc.annc_deadline_dt);
        
        if (publishDate && deadlineDate) {
            publishDate.setHours(0, 0, 0, 0);
            deadlineDate.setHours(0, 0, 0, 0);
            
            // 마감일이 지났으면 마감
            if (deadlineDate < today) {
                return '마감';
            }
            
            // 공고일이 미래면 공고예정
            if (publishDate > today) {
                return '공고예정';
            }
            
            // 현재 날짜가 접수기간 내에 있으면 접수중
            // 단, annc_pblsh_dt가 접수 시작일이 아닐 수 있으므로
            // annc_status가 "공고중"이고 날짜가 접수기간 내에 있으면 "접수중"으로 표시
            // 하지만 정확한 접수 시작일이 없으므로 임시로 annc_pblsh_dt 사용
            if (today >= publishDate && today <= deadlineDate) {
                // annc_status가 "공고중"이면 "접수중"으로 변경
                if (annc.annc_status === '공고중') {
                    return '접수중';
                }
                return annc.annc_status;
            }
        }
    }
    
    // 날짜 정보가 없으면 annc_status 그대로 사용
    return annc.annc_status === '접수마감' ? '마감' : annc.annc_status;
}
```

## 6. 장기 해결책: 접수 시작일 필드 추가

### 1단계: 모델 수정
```python
# zf_django/chatbot/models.py
class AnncAll(models.Model):
    # ... 기존 필드 ...
    annc_pblsh_dt = models.CharField(max_length=50, verbose_name="게시일")
    annc_recruitment_start_dt = models.CharField(max_length=50, verbose_name="접수 시작일", null=True, blank=True)  # 추가
    annc_deadline_dt = models.CharField(max_length=50, verbose_name="마감일")
```

### 2단계: 마이그레이션 생성 및 실행
```bash
cd zf_django
python manage.py makemigrations
python manage.py migrate
```

### 3단계: 크롤러 수정
- LH 웹사이트에서 접수 시작일 추출 로직 추가
- `annc_recruitment_start_dt` 필드에 저장

### 4단계: 프론트엔드 수정
- `annc_recruitment_start_dt` 필드를 우선 사용
- 없으면 `annc_pblsh_dt` 사용 (하위 호환성)

## 7. 권장 사항

### 즉시 적용 (단기)
1. 프론트엔드에서 `annc_pblsh_dt`를 접수 시작일로 가정하여 동적 상태 계산
2. 접수기간 내에 있으면 "접수중"으로 표시
3. 단, 정확도는 낮을 수 있음

### 향후 개선 (장기)
1. 크롤러 코드 확인하여 접수 시작일 추출 가능 여부 확인
2. 가능하면 접수 시작일 필드 추가
3. 크롤러에서 접수 시작일 추출 및 저장
4. 프론트엔드에서 접수 시작일 사용

## 8. 다음 단계

1. **크롤러 코드 확인**: 접수 시작일 추출 가능 여부 확인
2. **임시 해결책 적용**: 프론트엔드에서 동적 상태 계산 로직 수정
3. **장기 해결책 계획**: 접수 시작일 필드 추가 여부 결정

