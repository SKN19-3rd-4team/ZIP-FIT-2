from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.ask_api, name='ask_api'),
]
