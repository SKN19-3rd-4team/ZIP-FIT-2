from django.urls import path
from .views import TestApiView

urlpatterns = [
    # path('test/', TestApiView.as_view(), name='test_api'),
    # API 경로를 명확히 구분하기 위해 'api/' prefix를 사용하는 것을 권장합니다.
    path('api/test/', TestApiView.as_view(), name='test_api'),
]