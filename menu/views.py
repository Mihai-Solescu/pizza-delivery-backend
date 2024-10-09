from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Pizza, Ingredient, Dessert, Drink, UserPizzaTag
from .serializers import PizzaSerializer, IngredientSerializer, DessertSerializer, DrinkSerializer

class PizzaListViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        print(request.user)

        pizzas = Pizza.objects.all()
        serializer = PizzaSerializer(pizzas, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PizzaUserTagsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pizza_id):
        # Get the pizza object
        pizza = get_object_or_404(Pizza, pizza_id=pizza_id)
        user = request.user  # Get the currently authenticated user

        # Check if UserPizzaTag exists for this user and pizza
        user_pizza_tag, created = UserPizzaTag.objects.get_or_create(
            user=user,
            pizza=pizza,
            defaults={
                'rate_tag': False,
                'order_tag': False,
                'try_tag': False,
            }
        )

        # Check the ingredients to determine vegetarian and vegan tags
        is_vegan = all(
            ingredient.is_vegan for ingredient in pizza.pizzaingredientlink_set.values_list('ingredient', flat=True))
        is_vegetarian = all(ingredient.is_vegetarian for ingredient in
                            pizza.pizzaingredientlink_set.values_list('ingredient', flat=True))

        # Update the vegetarian and vegan tags
        user_pizza_tag.vegetarian_tag = is_vegetarian
        user_pizza_tag.vegan_tag = is_vegan
        user_pizza_tag.save()

        # Prepare the response data
        response_data = {
            'pizza_id': pizza.pizza_id,
            'name': pizza.name,
            'description': pizza.description,
            'vegetarian_tag': user_pizza_tag.vegetarian_tag,
            'vegan_tag': user_pizza_tag.vegan_tag,
            'rate_tag': user_pizza_tag.rate_tag,
            'order_tag': user_pizza_tag.order_tag,
            'try_tag': user_pizza_tag.try_tag,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, pizza_id):
        # Get the pizza object
        pizza = get_object_or_404(Pizza, pizza_id=pizza_id)
        user = request.user  # Get the currently authenticated user

        # Check if UserPizzaTag exists for this user and pizza
        user_pizza_tag, created = UserPizzaTag.objects.get_or_create(
            user=user,
            pizza=pizza,
            defaults={
                'rate_tag': False,
                'order_tag': False,
                'try_tag': False,
            }
        )

        # Get data from the request
        rate_tag = request.data.get('rate_tag', False)
        order_tag = request.data.get('order_tag', False)
        try_tag = request.data.get('try_tag', False)

        # Update the tags
        user_pizza_tag.rate_tag = rate_tag
        user_pizza_tag.order_tag = order_tag
        user_pizza_tag.try_tag = try_tag
        user_pizza_tag.save()

        # Prepare the response data
        response_data = {
            'pizza_id': pizza.pizza_id,
            'rate_tag': user_pizza_tag.rate_tag,
            'order_tag': user_pizza_tag.order_tag,
            'try_tag': user_pizza_tag.try_tag,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class IngredientListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request): # fix this
        ingredients = Ingredient.objects.all()
        serializer = IngredientSerializer(ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DrinkListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        drinks = Drink.objects.all()
        serializer = DrinkSerializer(drinks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DessertListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        desserts = Dessert.objects.all()
        serializer = DessertSerializer(desserts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)