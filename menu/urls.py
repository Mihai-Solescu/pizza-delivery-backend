from .views import PizzaView, IngredientView, MenuItemView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

urlpatterns = [
    path('pizzas/', PizzaView.as_view()),
    path('ingredients/', IngredientView.as_view()),
    path('menu/', MenuItemView.as_view()),
]