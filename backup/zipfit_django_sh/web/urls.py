# web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('web/', views.chat_view, name='chat'),
    path('profile/', views.profile_view, name='profile'),
    path('announcements/', views.announcements_view, name='announcements'),
]
