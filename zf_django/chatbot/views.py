import uuid
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .graph import chat
from .services import ChatHistoryService


class TestApiView(APIView):
    """
    테스트용 REST API View. GET 요청 시 Hello World 메시지를 반환합니다.
    """
    def get(self, request):
        data = {
            "message": "Hello, world! (from chatbot REST API)",
            "status": "success"
        }
        return Response(data, status=status.HTTP_200_OK)


class ChatApiView(APIView):
    """
    챗봇 API View.
    POST: 메시지 전송 및 응답 받기
    GET: 세션 기록 조회
    """

    def post(self, request):
        """
        채팅 메시지 전송

        Request Body:
        {
            "message": "사용자 메시지",
            "session_id": "세션 ID (optional, 없으면 새로 생성)"
        }

        Response:
        {
            "answer": "챗봇 응답",
            "session_id": "세션 ID",
            "session_state": {...}
        }
        """
        message = request.data.get("message", "").strip()
        session_id = request.data.get("session_id")
        # message 없으면 에러 반환
        if not message:
            return Response(
                {"error": "message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 세션 ID 생성/검증
        if not session_id:
            session_id = str(uuid.uuid4())

        # 세션 상태 가져오기 (request에서 전달받거나 기본값 사용)
        session_state = request.data.get("session_state", {
            "chat_history": [],
            "candidate_anncs": [],
            "current_annc_ids": [],
            "search_filters": {}
        })

        try:
            # 챗봇 실행
            result = chat(message, session_state)

            # DB에 대화 기록 저장
            ChatHistoryService.add_message(
                session_key=session_id,
                message=message,
                message_type='user'
            )
            ChatHistoryService.add_message(
                session_key=session_id,
                message=result["answer"],
                message_type='bot'
            )

            return Response({
                "answer": result["answer"],
                "session_id": session_id,
                "session_state": result["session_state"]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        """
        세션별 채팅 기록 조회

        Query Params:
        - session_id: 세션 ID (required)
        - limit: 조회할 메시지 수 (optional, default: 20)
        """
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "session_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        limit = int(request.query_params.get("limit", 20))

        try:
            history = ChatHistoryService.get_history_by_session(session_id, limit)
            return Response({
                "session_id": session_id,
                "messages": history
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )