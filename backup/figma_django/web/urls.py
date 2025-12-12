# web/urls.py
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('main/', views.main_view, name='main'),
    path('user-info/', views.user_info_view, name='user_info'),
    path('chat/', views.chat_view, name='chat'),
    path('list/', views.list_view, name='list'),
]

