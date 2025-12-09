from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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