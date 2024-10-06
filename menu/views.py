from rest_framework import viewsets
from rest_framework.views import APIView

from .models import Pizza, Ingredient
from .serializers import PizzaSerializer, IngredientSerializer

class PizzaView(viewsets.ReadOnlyModelViewSet):
    queryset = Pizza.objects.select_related('')
    serializer_class = PizzaSerializer

class IngredientView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer