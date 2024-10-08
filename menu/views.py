from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from .models import Pizza, Ingredient, Dessert, Drink
from .serializers import PizzaSerializer, IngredientSerializer, DessertSerializer, DrinkSerializer

class PizzaListViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        print(request.user)

        pizzas = Pizza.objects.all()
        serializer = PizzaSerializer(pizzas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class IngredientListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request): # fix this
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DesertListView(APIView):
    permission_classes = [permissions.AllowAny]
    queryset = Dessert.objects.all()
    serializer_class = DessertSerializer

class DrinkListView(APIView):
    permission_classes = [permissions.AllowAny]
    queryset = Drink.objects.all()
    serializer_class = DrinkSerializer