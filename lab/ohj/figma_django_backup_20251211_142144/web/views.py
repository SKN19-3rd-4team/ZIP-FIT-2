# web/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# -------------------
# 랜딩 페이지
# -------------------
def landing_view(request):
    return render(request, "web/landing.html")

# -------------------
# 메인 페이지 (대시보드)
# -------------------
def main_view(request):
    return render(request, "web/main.html")

# -------------------
# 사용자 정보 입력 페이지
# -------------------
def user_info_view(request):
    # 사용자 정보는 프론트엔드에서 관리 (API 호출 시 전달)
    # Django session에 저장하지 않음
    return render(request, "web/user_info.html")

# -------------------
# 채팅 페이지
# -------------------
def chat_view(request):
    # user_key, session_key는 프론트엔드에서 관리
    # API 호출 시 프론트엔드에서 전달
    return render(request, "web/chat.html")

# -------------------
# 공고 목록 페이지
# -------------------
def list_view(request):
    return render(request, "web/list.html")

