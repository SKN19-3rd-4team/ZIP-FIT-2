"""
URL configuration for figma_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 웹 페이지 (랜딩 페이지 포함) - 먼저 매칭되도록 먼저 배치
    path('', include('web.urls')),
    # API 엔드포인트 - web.urls 이후에 매칭 (루트 경로가 아닌 API 경로만)
    path('api/', include('chatbot.urls')),
]

