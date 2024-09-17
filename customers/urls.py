from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LoginView

router = DefaultRouter()
router.register(r'login', LoginView, basename="LoginViews")

urlpatterns = [
    path('login/', LoginView.as_view()),
]