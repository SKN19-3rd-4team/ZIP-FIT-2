from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse('Hello World!')


def chat_interface(request):
    """
    채팅 인터페이스 페이지를 렌더링합니다.
    """
    return render(request, 'chat_interface.html')