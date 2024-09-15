from rest_framework import viewsets
from .models import Pizza, Ingredient, MenuItem
from .serializers import PizzaSerializer, IngredientSerializer, MenuItemSerializer
from django_filters.rest_framework import DjangoFilterBackend


class PizzaView(viewsets.ModelViewSet):
    queryset = Pizza.objects.select_related('')
    serializer_class = PizzaSerializer


class IngredientView(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class MenuItemView(viewsets.ModelViewSet):
    queryset = MenuItem.objects.prefetch_related(
        'pizzas',
        'drinks',
        'desserts'
    )
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']


