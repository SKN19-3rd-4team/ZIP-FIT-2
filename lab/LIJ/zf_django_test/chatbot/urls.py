from django.urls import path
from .views import annc_info  # 위에서 만든 함수 import

urlpatterns = [
    # .as_view() 없이 그냥 함수명만 적습니다.
    path('api/annc/', annc, name='annc'),
]