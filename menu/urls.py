from .views import PizzaView, IngredientView, MenuItemView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'pizza', PizzaView, basename="PapaLuigiPizza")
router.register(r'ingredient', IngredientView, basename="Ingredients!")
router.register(r'menuItem', MenuItemView, basename="MenuItem")

urlpatterns = [
    path('', include(router.urls)),
]