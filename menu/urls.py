from django.urls import path, include
from menu.views import PizzaListViewSet, IngredientListView, DrinkListView, DesertListView

urlpatterns = [
    path('pizzalist/', PizzaListViewSet.as_view({'get': 'list'})),
    path('ingredientlist/', IngredientListView.as_view({'get': 'list'})),
    path('drinklist/', DrinkListView.as_view()),
    path('dessertlist/', DesertListView.as_view())
]