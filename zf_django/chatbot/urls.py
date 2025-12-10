from django.urls import path
from .views import chat_histories, chat_history_detail, annc_list, annc_summary, TestApiView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from chatbot.views_chat import chat_message # 추후 합칠때 없애야 함


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/test/', TestApiView.as_view(), name='test_api'),

    # 채팅
    path('api/chat', chat_message, name='chat-message'),
    path('api/chathistories', chat_histories, name='chat-histories'),
    path('api/chathistories/<str:session_key>', chat_history_detail, name='chat-history-detail'),

    # 공고
    path('api/anncs', annc_list, name='annc-list'),
    path('api/annc_summary', annc_summary, name='annc-summary'),
]