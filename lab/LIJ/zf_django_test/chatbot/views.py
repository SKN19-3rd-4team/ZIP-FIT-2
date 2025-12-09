from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AnncAll

@api_view(['GET'])
def annc_info(request):
    """
    공고 목록 조회 및 DB 연결 테스트용 함수
    """
    # [디버깅 1] API 호출 여부 확인
    print("\n" + "="*50)
    print(">>> 1. API 요청 수신! (views.py가 실행되었습니다)")

    # 1. ORM으로 데이터 조회
    data = AnncAll.objects.values(
        'annc_title',       # 공고 제목
        'annc_url',         # 공고 URL
        'annc_type',        # 공고 유형
        'annc_dtl_type',    # 공고 유형 상세
        'annc_region',      # 지역
        'annc_pblsh_dt',    # 게시일
        'annc_deadline_dt', # 마감일
        'annc_status',      # 공고 상태
        'annc_id'           # 공고 식별 ID
    ).order_by('-created_dttm')[:100]  # 최신순 100개 제한

    # [디버깅 2] DB 데이터 개수 확인
    count = len(data)
    print(f">>> 2. DB 조회 완료! 가져온 데이터 개수: {count} 개")

    # [디버깅 3] 데이터 내용 샘플 확인
    if count > 0:
        print(f">>> 3. 첫 번째 데이터 제목: {data[0]['annc_title']}")
    else:
        print(">>> 3. 연결은 성공했으나, 테이블이 비어있습니다.")
    
    print("="*50 + "\n")

    # 2. 리스트로 변환하여 JSON 응답 반환
    return Response({
        "count": count,
        "data": list(data)
    })