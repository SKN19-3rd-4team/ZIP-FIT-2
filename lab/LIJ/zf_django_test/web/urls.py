from django.urls import path
from web import views


app_name = 'web'

urlpatterns = [
    # path('', views.index, name='index'), # views 함수의 별칭
    path('', views.chat_interface, name='chat_interface'),
]