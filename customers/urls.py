from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView, CustomerRegisterView, CustomerPreferencesView, CustomerDataView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('register/', CustomerRegisterView.as_view()),
    path('preferences/', CustomerPreferencesView.as_view()),
    path('metrics/', CustomerDataView.as_view())
]