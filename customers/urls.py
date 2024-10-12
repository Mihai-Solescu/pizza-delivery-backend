from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView, CustomerRegisterView, UserPreferencesView, CustomerInfoView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', CustomerRegisterView.as_view()),
    path('preferences/', UserPreferencesView.as_view()),
    path('customer_info/', CustomerInfoView.as_view())
]