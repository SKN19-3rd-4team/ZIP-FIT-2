from django.urls import path
from .views import chat_message, chat_histories, chat_history_detail, annc_list, annc_summary

urlpatterns = [
    # 채팅
    path('api/chat', chat_message, name='chat-message'),
    path('api/chathistories', chat_histories, name='chat-histories'),
    path('api/chathistories/<str:session_key>', chat_history_detail, name='chat-history-detail'),

    # 공고
    path('api/anncs', annc_list, name='annc-list'),
    path('api/annc_summary', annc_summary, name='annc-summary'),
]