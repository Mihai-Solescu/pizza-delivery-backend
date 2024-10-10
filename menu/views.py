from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Pizza, Ingredient, Dessert, Drink, UserPizzaTag, PizzaIngredientLink, UserPizzaRating
from .serializers import PizzaSerializer, IngredientSerializer, DessertSerializer, DrinkSerializer
from decimal import Decimal

class PizzaListViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):

        print(request.user)

        # Get query parameters from the request
        filtered = request.query_params.get('filtered', 'false').lower() == 'true'
        budget_range = request.query_params.get('budget_range', None)
        is_vegetarian = request.query_params.get('is_vegetarian', None)
        is_vegan = request.query_params.get('is_vegan', None)

        # Filter the pizza queryset based on the request parameters
        pizzas = Pizza.objects.all()

        # Filter based on budget_range if provided
        print("vegan: " + str(is_vegan) + " request:" + request.query_params.get('is_vegan', None))
        print("vegetarian: " + str(is_vegetarian) + " request:" + request.query_params.get('is_vegetarian', None))

        if filtered:
            if budget_range:
                budget_max = Decimal(budget_range)  # Only the max price is provided
                print("max budget:" + str(budget_max))
                pizzas = [pizza for pizza in pizzas if self._calculate_price(pizza) <= budget_max]

            # Filter based on vegetarian and vegan requirements
            if is_vegetarian is not None:
                is_vegetarian = is_vegetarian.lower() == 'true'
                if is_vegetarian:
                    pizzas = [pizza for pizza in pizzas if
                              all(ingredient.is_vegetarian for ingredient in self._get_ingredients(pizza)) == is_vegetarian]

            if is_vegan is not None:
                is_vegan = is_vegan.lower() == 'true'
                if is_vegan:
                    pizzas = [pizza for pizza in pizzas if
                              all(ingredient.is_vegan for ingredient in self._get_ingredients(pizza)) == is_vegan]

        # Serialize the filtered pizzas
        serializer = PizzaSerializer(pizzas, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _calculate_price(self, pizza):
        """Helper function to calculate total price of the pizza."""
        labor_price = Decimal(0.5)
        ingredients = PizzaIngredientLink.objects.filter(pizza=pizza).select_related('ingredient')
        total_ingredient_cost = sum(i.ingredient.cost for i in ingredients)
        return total_ingredient_cost + labor_price

    def _get_ingredients(self, pizza):
        """Helper function to get ingredients of a pizza."""
        return Ingredient.objects.filter(pizzaingredientlink__pizza=pizza)

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


class PizzaUserRatingView(APIView):
    def post(self, request, pizza_id):
        # Get the pizza object
        pizza = get_object_or_404(Pizza, pizza_id=pizza_id)
        user = request.user  # Get the currently authenticated user

        # Check if UserPizzaTag exists for this user and pizza
        user_pizza_rating, created = UserPizzaRating.objects.get_or_create(
            user=user,
            pizza=pizza,
            defaults={
                'rating': 2,
            }
        )

        # Get data from the request
        rating = request.data.get('rating', False)

        # Update the tags
        user_pizza_rating.rating = rating
        user_pizza_rating.save()

        # Prepare the response data
        response_data = {
            'pizza_id': pizza.pizza_id,
            'rating': user_pizza_rating.rating,
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