# 각 API 호출 결과
> http://127.0.0.1:8000/api/docs/#/ 

> http://127.0.0.1:8000/api/annc_summary
```json
{
  "message": "성공적으로 공고 요약 정보를 조회했습니다.",
  "status": "success",
  "data": {
    "cnt_total": 31,
    "cnt_lease": 31,
    "cnt_sale": 0,
    "cnt_etc": 0
  }
}
```
> http://127.0.0.1:8000/api/anncs?current_page=1&items_per_page=10
```json
{
  "message": "성공적으로 공고 목록을 조회했습니다.",
  "status": "success",
  "data": {
    "page_info": {
      "total_count": 31,
      "current_page": 1,
      "items_per_page": 10,
      "total_pages": 4
    },
    "items": [
      {
        "annc_id": 61,
        "annc_title": "[정정공고]남원노암 영구임대주택 예비입주자 모집(모집공고일 : 2025.06.25,정정공고)",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018325&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=09",
        "created_at": "2025-12-12T05:49:49.582885+09:00",
        "annc_status": "공고중",
        "annc_type": "임대",
        "annc_dtl_type": "영구임대",
        "annc_region": "전북특별자치도",
        "annc_pblsh_dt": "2025.06.25",
        "annc_deadline_dt": "2025.12.31"
      },
      {
        "annc_id": 59,
        "annc_title": "동해유성·태백청솔 국민임대주택 예비입주자 상시모집(2025.09.16)",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018772&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=07",
        "created_at": "2025-12-12T05:47:38.912892+09:00",
        "annc_status": "공고중",
        "annc_type": "임대",
        "annc_dtl_type": "국민임대",
        "annc_region": "강원특별자치도",
        "annc_pblsh_dt": "2025.09.16",
        "annc_deadline_dt": "2025.12.31"
      },
      {
        "annc_id": 57,
        "annc_title": "경북서부지역(구미시,김천시,대구광역시 군위군,의성군) 국민임대주택 예비자모집 공고",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300019067&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=07",
        "created_at": "2025-12-12T05:45:51.151929+09:00",
        "annc_status": "접수중",
        "annc_type": "임대",
        "annc_dtl_type": "국민임대",
        "annc_region": "대구광역시 외",
        "annc_pblsh_dt": "2025.11.17",
        "annc_deadline_dt": "2025.12.12"
      },
      {
        "annc_id": 55,
        "annc_title": "[정정공고]광주광역시(북구,광산구) 고령자 매입임대주택 예비입주자 모집",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300019112&ccrCnntSysDsCd=03&uppAisTpCd=13&aisTpCd=26",
        "created_at": "2025-12-12T05:43:49.314332+09:00",
        "annc_status": "접수중",
        "annc_type": "임대",
        "annc_dtl_type": "매입임대",
        "annc_region": "전국",
        "annc_pblsh_dt": "2025.11.27",
        "annc_deadline_dt": "2025.12.12"
      },
      {
        "annc_id": 53,
        "annc_title": "군산지역 국민임대주택 입주자 상시 모집(산북부향2차 외 4개단지)",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018496&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=07",
        "created_at": "2025-12-12T05:41:11.214793+09:00",
        "annc_status": "공고중",
        "annc_type": "임대",
        "annc_dtl_type": "국민임대",
        "annc_region": "전북특별자치도",
        "annc_pblsh_dt": "2025.07.24",
        "annc_deadline_dt": "2026.08.04"
      },
      {
        "annc_id": 51,
        "annc_title": "정읍수성1 영구임대주택 예비입주자 모집 공고",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018994&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=09",
        "created_at": "2025-12-12T05:38:35.471238+09:00",
        "annc_status": "공고중",
        "annc_type": "임대",
        "annc_dtl_type": "영구임대",
        "annc_region": "전북특별자치도",
        "annc_pblsh_dt": "2025.11.10",
        "annc_deadline_dt": "2025.12.31"
      },
      {
        "annc_id": 49,
        "annc_title": "양산사송 A-8BL 행복주택 입주자격완화·동호지정·상시모집 입주자 추가모집('25.10.16.공고)",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018907&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=10",
        "created_at": "2025-12-12T05:36:24.782337+09:00",
        "annc_status": "공고중",
        "annc_type": "임대",
        "annc_dtl_type": "행복주택",
        "annc_region": "경상남도",
        "annc_pblsh_dt": "2025.10.16",
        "annc_deadline_dt": "2025.12.31"
      },
      {
        "annc_id": 47,
        "annc_title": "경북청도 행복주택 입주자 최초모집 공고",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300019113&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=10",
        "created_at": "2025-12-12T05:34:03.180519+09:00",
        "annc_status": "접수중",
        "annc_type": "임대",
        "annc_dtl_type": "행복주택",
        "annc_region": "경상북도",
        "annc_pblsh_dt": "2025.11.28",
        "annc_deadline_dt": "2025.12.12"
      },
      {
        "annc_id": 45,
        "annc_title": "군산지역 국민임대주택 입주자 상시 모집(산북부향1차 외 3개단지)",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300018493&ccrCnntSysDsCd=03&uppAisTpCd=06&aisTpCd=07",
        "created_at": "2025-12-12T05:31:27.658946+09:00",
        "annc_status": "공고중",
        "annc_type": "임대",
        "annc_dtl_type": "국민임대",
        "annc_region": "전북특별자치도",
        "annc_pblsh_dt": "2025.07.24",
        "annc_deadline_dt": "2026.08.04"
      },
      {
        "annc_id": 43,
        "annc_title": "2025년 신혼·신생아 전세임대 I 입주자 수시모집 공고",
        "annc_url": "https://apply.lh.or.kr/lhapply/apply/wt/wrtanc/selectWrtancInfo.do?mi=1026&panId=2015122300017958&ccrCnntSysDsCd=03&uppAisTpCd=13&aisTpCd=17",
        "created_at": "2025-12-12T05:30:24.558201+09:00",
        "annc_status": "접수중",
        "annc_type": "임대",
        "annc_dtl_type": "전세임대",
        "annc_region": "서울특별시 외",
        "annc_pblsh_dt": "2025.10.13",
        "annc_deadline_dt": "2025.12.31"
      }
    ]
  }
}
```
> http://127.0.0.1:8000/api/chat
```json
{
  "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
  "status": "success",
  "data": {
    "ai_response": {
      "id": 12,
      "session_id": "4d6791af-311c-430e-8134-62f1fee419fa",
      "sequence": 2,
      "message_type": "bot",
      "message": "안녕하세요! \"집핏(ZIP-FIT)\"입니다. 주택이나 임대, 청약 관련 질문이 있으시면 언제든지 말씀해 주세요! 도움이 필요하신 점이 있다면 말씀해 주세요. 😊"
    }
  }
}
```
> http://127.0.0.1:8000/api/chathistories?user_key=0
```json
{
  "message": "성공적으로 채팅 히스토리 목록을 조회했습니다.",
  "status": "success",
  "data": [
    {
      "title": "수원 신혼부부 추천",
      "session_id": "session-001"
    },
    {
      "title": "강남 임대 아파트",
      "session_id": "session-002"
    }
  ]
}
```
> http://127.0.0.1:8000/api/chathistories/4d6791af-311c-430e-8134-62f1fee419fa?user_key=0
```json
{
  "message": "성공적으로 특정 채팅 히스토리를 조회했습니다.",
  "status": "success",
  "data": {
    "title": "수원 신혼부부 추천 분양",
    "session_id": "4d6791af-311c-430e-8134-62f1fee419fa",
    "user_key": "0",
    "chat_list": [
      {
        "id": 1,
        "sequence": 1,
        "message_type": "user",
        "message": "추천해줘"
      },
      {
        "id": 2,
        "sequence": 2,
        "message_type": "bot",
        "message": "여기 추천 목록입니다."
      }
    ]
  }
}
```

