from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
import math
import uuid
import logging

from .models import AnncAll, Chat, ChatMessage
from .serializers import (
    AnnouncementListResponseSerializer, AnncSummaryResponseSerializer,
    ChatRequestSerializer, ChatResponseSerializer,
    ChatHistoriesResponseSerializer, ChatHistoryDetailResponseSerializer
)
from .graph import chat as langgraph_chat

logger = logging.getLogger(__name__)

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
    """
    사용자 메시지를 받아 LangGraph 기반 챗봇으로 AI 응답을 생성합니다.
    """
    user_msg = request.data.get('user_message', '')
    session_id = request.data.get('session_id')  # session_id로 통일
    user_key = request.data.get('user_key', 'anonymous')

    if not user_msg:
        return Response({
            "message": "user_message는 필수입니다.",
            "status": "error",
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 세션 처리: 기존 세션 조회 또는 새 세션 생성
        if session_id:
            try:
                session_uuid = uuid.UUID(session_id)
                chat_session = Chat.objects.filter(session_key=session_uuid).first()
            except ValueError:
                chat_session = None
        else:
            chat_session = None

        # 새 세션 생성
        if not chat_session:
            session_uuid = uuid.uuid4()
            chat_session = Chat.objects.create(
                session_key=session_uuid,
                user_key=user_key,
                title=user_msg[:50] if len(user_msg) > 50 else user_msg
            )

        # 이전 대화 히스토리 로드 (session_state 구성)
        previous_messages = ChatMessage.objects.filter(
            chat=chat_session
        ).order_by('sequence')

        chat_history = []
        for msg in previous_messages:
            role = 'user' if msg.message_type == 'user' else 'assistant'
            chat_history.append({'role': role, 'content': msg.message})

        # 세션 상태 구성 (이전 상태 복원)
        session_state = {
            'chat_history': chat_history,
            'search_history': [],
            'prev_anncs': [],
            'selected_annc': None
        }

        # LangGraph 챗봇 호출
        result = langgraph_chat(user_msg, session_state)
        ai_response = result.get('answer', '응답을 생성하지 못했습니다.')

        # 현재 최대 sequence 조회
        last_seq = ChatMessage.objects.filter(chat=chat_session).order_by('-sequence').first()
        next_seq = (last_seq.sequence + 1) if last_seq else 1

        # 사용자 메시지 저장
        ChatMessage.objects.create(
            chat=chat_session,
            sequence=next_seq,
            message=user_msg,
            prompt=user_msg,
            message_type='user'
        )

        # AI 응답 저장
        bot_message = ChatMessage.objects.create(
            chat=chat_session,
            sequence=next_seq + 1,
            message=ai_response,
            prompt='',
            message_type='bot'
        )

        response_data = {
            "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
            "status": "success",
            "data": {
                "ai_response": {
                    "id": bot_message.id,
                    "session_id": str(chat_session.session_key),
                    "sequence": bot_message.sequence,
                    "message_type": "bot",
                    "message": ai_response
                }
            }
        }
        return Response(response_data)

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        return Response({
            "message": f"채팅 처리 중 오류가 발생했습니다: {str(e)}",
            "status": "error",
            "data": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
