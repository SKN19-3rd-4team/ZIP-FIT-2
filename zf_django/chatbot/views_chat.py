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
                "session_id": "8a7e0d3c-9b1f-4d2a-8c5e-6f4b3a2d1e0f",
                "sequence": 2,
                "message_type": "bot",
                "message": f"AI가 답변합니다: '{user_msg}'에 대한 정보입니다."
            }
        }
    }
    return Response(response_data)