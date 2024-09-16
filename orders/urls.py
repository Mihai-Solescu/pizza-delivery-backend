from .views import OrderView, EarningView

from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'order', OrderView, basename="order")

urlpatterns = [
    path('', include(router.urls)),
    path('earnings/', EarningView.as_view({'get': 'list'})),
]

