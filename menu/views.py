from rest_framework import viewsets
from .models import Pizza, Ingredient, MenuItem
from .serializers import PizzaSerializer, IngredientSerializer, MenuItemSerializer
from django_filters.rest_framework import DjangoFilterBackend


class PizzaView(viewsets.ReadOnlyModelViewSet):
    queryset = Pizza.objects.select_related('')
    serializer_class = PizzaSerializer


class IngredientView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class MenuItemView(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.prefetch_related(
        'pizzas',
        'drinks',
        'desserts'
    )
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']


#Return custom menu items that are customers own i.e. not shared with other customers!


