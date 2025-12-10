from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
import math

from .models import AnncAll
from .serializers import (
    AnnouncementListResponseSerializer, AnncSummaryResponseSerializer,
    ChatRequestSerializer, ChatResponseSerializer,
    ChatHistoriesResponseSerializer, ChatHistoryDetailResponseSerializer
)

# ---------------------------------------------------
# 1. 채팅 메시지 등록 및 AI 응답 (POST /api/chat)
# ---------------------------------------------------
@extend_schema(
    summary="사용자 - 신규 채팅 메시지 등록 및 AI 응답 받기",
    operation_id="postChatMessage",
    tags=["채팅"],
    request=ChatRequestSerializer,
    responses={200: ChatResponseSerializer}
)
@api_view(['POST'])
def chat_message(request):
    # 실제로는 여기서 AI 모델 호출 로직이 들어감
    user_msg = request.data.get('user_message', '')
    
    # 더미 응답 생성
    response_data = {
        "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
        "status": "success",
        "data": {
            "ai_response": {
                "id": 101,
                "sequence": 2,
                "message_type": "bot",
                "message": f"AI가 답변합니다: '{user_msg}'에 대한 정보입니다."
            }
        }
    }
    return Response(response_data)

# ---------------------------------------------------
# 2. 채팅 히스토리 목록 조회 (GET /api/chathistories)
# ---------------------------------------------------
@extend_schema(
    summary="사용자 - 채팅 히스토리 목록 조회",
    operation_id="getChatHistories",
    tags=["채팅 히스토리"],
    parameters=[
        OpenApiParameter(name="user_key", description="사용자 키", required=True, type=str),
    ],
    responses={200: ChatHistoriesResponseSerializer}
)
@api_view(['GET'])
def chat_histories(request):
    # 더미 데이터
    response_data = {
        "message": "성공적으로 채팅 히스토리 목록을 조회했습니다.",
        "status": "success",
        "data": [
            {"title": "수원 신혼부부 추천", "session_key": "session-001"},
            {"title": "강남 임대 아파트", "session_key": "session-002"},
        ]
    }
    return Response(response_data)

# ---------------------------------------------------
# 3. 특정 채팅 히스토리 상세 조회 (GET /api/chathistories/{session_key})
# ---------------------------------------------------
@extend_schema(
    summary="사용자 - 특정 히스토리 조회",
    operation_id="getChatHistoryDetail",
    tags=["채팅 히스토리"],
    parameters=[
        OpenApiParameter(name="user_key", description="사용자 키", required=True, type=str),
    ],
    responses={200: ChatHistoryDetailResponseSerializer}
)
@api_view(['GET'])
def chat_history_detail(request, session_key):
    # 더미 데이터
    response_data = {
        "message": "성공적으로 특정 채팅 히스토리를 조회했습니다.",
        "status": "success",
        "data": {
            "title": "수원 신혼부부 추천 분양",
            "session_key": session_key,
            "user_key": request.GET.get('user_key', 'unknown'),
            "chat_list": [
                {"id": 1, "sequence": 1, "message_type": "user", "message": "추천해줘"},
                {"id": 2, "sequence": 2, "message_type": "bot", "message": "여기 추천 목록입니다."}
            ]
        }
    }
    return Response(response_data)

# ---------------------------------------------------
# 4. 공고 목록 조회 (GET /api/anncs) - BaseResponse 적용
# ---------------------------------------------------
@extend_schema(
    summary="공고 목록 조회",
    operation_id="getAnnouncementList",
    tags=["공고"],
    parameters=[
        OpenApiParameter(name="annc_title", required=False, type=str),
        OpenApiParameter(name="annc_status", required=False, type=str, enum=["진행중", "마감", "예정"]),
        OpenApiParameter(name="annc_type", required=False, type=str),
        OpenApiParameter(name="items_per_page", required=True, type=int, default=10),
        OpenApiParameter(name="current_page", required=True, type=int, default=1),
    ],
    responses={200: AnnouncementListResponseSerializer}
)
@api_view(['GET'])
def annc_list(request):
    # 1. 파라미터 처리
    annc_title = request.GET.get('annc_title')
    annc_status = request.GET.get('annc_status')
    items_per_page = int(request.GET.get('items_per_page', 10))
    current_page = int(request.GET.get('current_page', 1))

    # 2. 필터링
    queryset = AnncAll.objects.all().order_by('-created_dttm')
    if annc_title:
        queryset = queryset.filter(annc_title__icontains=annc_title)
    if annc_status:
        queryset = queryset.filter(annc_status=annc_status)

    # 3. 페이징 계산
    total_count = queryset.count()
    total_pages = math.ceil(total_count / items_per_page)
    start = (current_page - 1) * items_per_page
    end = start + items_per_page
    page_data = queryset[start:end]

    # 4. 응답 생성 (BaseResponse 구조 맞춤)
    # 모델 데이터를 직렬화 (AnnouncementItemSerializer 이용)
    # 여기서는 수동으로 구조를 맞춰서 보냅니다.
    from .serializers import AnnouncementItemSerializer
    items_data = AnnouncementItemSerializer(page_data, many=True).data

    response_data = {
        "message": "성공적으로 공고 목록을 조회했습니다.",
        "status": "success",
        "data": {
            "page_info": {
                "total_count": total_count,
                "current_page": current_page,
                "items_per_page": items_per_page,
                "total_pages": total_pages
            },
            "items": items_data
        }
    }
    return Response(response_data)

# ---------------------------------------------------
# 5. 공고 요약 정보 조회 (GET /api/annc_summary)
# ---------------------------------------------------
@extend_schema(
    summary="홈 - 공고 요약 데이터 요약",
    operation_id="getAnnouncementSummary",
    tags=["공고 요약"],
    responses={200: AnncSummaryResponseSerializer}
)
@api_view(['GET'])
def annc_summary(request):
    # 실제 DB 집계 로직
    total = AnncAll.objects.count()
    lease = AnncAll.objects.filter(annc_type="임대").count() # 예시
    sale = AnncAll.objects.filter(annc_type="분양").count()   # 예시
    etc = total - (lease + sale)

    response_data = {
        "message": "성공적으로 공고 요약 정보를 조회했습니다.",
        "status": "success",
        "data": {
            "cnt_total": total,
            "cnt_lease": lease,
            "cnt_sale": sale,
            "cnt_etc": etc
        }
    }
    return Response(response_data)



class TestApiView(APIView):
    """
    테스트용 REST API View. GET 요청 시 Hello World 메시지를 반환합니다.
    """
    def get(self, request):
        # API 응답으로 보낼 데이터 (JSON 형태로 자동 변환됨)
        data = {
            "message": "Hello, world! (from chatbot REST API)",
            "status": "success"
        }
        return Response(data, status=status.HTTP_200_OK)