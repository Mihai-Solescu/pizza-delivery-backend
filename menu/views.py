from rest_framework import viewsets
from rest_framework.views import APIView

from .models import Pizza, Ingredient, Dessert, Drink
from .serializers import PizzaSerializer, IngredientSerializer, DessertSerializer, DrinkSerializer

class PizzaListViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing a list of pizzas and their details.
    """
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer


class IngredientListView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class DesertListView(APIView):
    queryset = Dessert.objects.all()
    serializer_class = DessertSerializer

class DrinkListView(APIView):
    queryset = Drink.objects.all()
    serializer_class = DrinkSerializer