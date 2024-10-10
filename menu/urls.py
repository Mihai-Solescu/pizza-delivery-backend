from django.urls import path, include
from menu.views import PizzaListViewSet, IngredientListView, DrinkListView, DessertListView, PizzaUserTagsView, \
    PizzaUserRatingView

urlpatterns = [
    path('pizzalist/', PizzaListViewSet.as_view()),
    path('ingredientlist/', IngredientListView.as_view()),
    path('drinklist/', DrinkListView.as_view()),
    path('dessertlist/', DessertListView.as_view()),
    path('pizza/<int:pizza_id>/tags/', PizzaUserTagsView.as_view()),
    path('pizza/<int:pizza_id>/rating', PizzaUserRatingView.as_view())
]