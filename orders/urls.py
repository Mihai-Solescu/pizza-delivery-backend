from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet, OrderMenuItemView, OrderMenuItemExtraIngredientView

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'ordermenuitems', OrderMenuItemView)
router.register(r'ordermenuitemextras', OrderMenuItemExtraIngredientView)

urlpatterns = [
    path('', include(router.urls)),
]

