from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView, CustomerRegisterView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', CustomerRegisterView.as_view()),
]