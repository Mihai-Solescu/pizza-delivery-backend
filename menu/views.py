from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Min
from django.contrib.contenttypes.models import ContentType

from orders.models import OrderItem
from .models import Pizza, Ingredient, Dessert, Drink, UserPizzaTag, PizzaIngredientLink, UserPizzaRating
from .serializers import PizzaSerializer, IngredientSerializer, DessertSerializer, DrinkSerializer
from decimal import Decimal


class PizzaListViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get query parameters from the request
        smart = request.query_params.get('smart', 'false').lower() == 'true'
        order_type = request.query_params.get('order_type', None)
        budget_range = request.query_params.get('budget_range', None)
        is_vegetarian = request.query_params.get('is_vegetarian', None)
        is_vegan = request.query_params.get('is_vegan', None)

        # Filter the pizza queryset based on the request parameters
        pizzas = Pizza.objects.all()

        if order_type == 'normal':
            if smart:
                pizzas = self._pref_filter(budget_range, is_vegetarian, is_vegan, pizzas)

            # Serialize the smart filtered pizzas
            serializer = PizzaSerializer(pizzas, many=True, context={'request': request})
        else:
            pizzas = self._pref_filter(budget_range, is_vegetarian, is_vegan, pizzas)

            if smart:
                print("needs implementation")
            else:
                # Enhance quick order: return only one pizza sorted by popularity
                pizzas = self._get_most_popular_pizza(pizzas)

            # Serialize the pizzas
            serializer = PizzaSerializer(pizzas, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_most_popular_pizza(self, pizzas):
        """Return the most popular pizza based on total quantity ordered."""
        # Ensure pizzas is a queryset
        if pizzas is None:
            return Pizza.objects.none()  # Return an empty queryset

        # Get the content type for Pizza
        pizza_content_type = ContentType.objects.get_for_model(Pizza)

        # Query OrderItems related to pizzas and sum their quantities
        order_items = OrderItem.objects.filter(content_type=pizza_content_type) \
            .values('object_id') \
            .annotate(total_quantity=Sum('quantity')) \
            .order_by('-total_quantity')

        # Extract the most popular pizza object_id
        most_popular_pizza_id = order_items[0]['object_id'] if order_items else None

        if most_popular_pizza_id:
            # Return the most popular pizza based on the object_id as a list
            most_popular_pizza = pizzas.filter(id=most_popular_pizza_id).first()
            if most_popular_pizza:
                return [most_popular_pizza]

        # If no popular pizza is found, return the first available pizza as a list
        first_pizza = pizzas.first() if pizzas.exists() else None
        return [first_pizza] if first_pizza else []

    def _calculate_price(self, pizza):
        """Helper function to calculate total price of the pizza."""
        labor_price = Decimal(0.5)
        ingredients = PizzaIngredientLink.objects.filter(pizza=pizza).select_related('ingredient')
        total_ingredient_cost = sum(i.ingredient.cost for i in ingredients)
        return total_ingredient_cost + labor_price

    def _get_ingredients(self, pizza):
        """Helper function to get ingredients of a pizza."""
        return Ingredient.objects.filter(pizzaingredientlink__pizza=pizza)

    def _pref_filter(self, budget_range, is_vegetarian, is_vegan, pizzas):
        # Budget filter
        if budget_range:
            budget_max = Decimal(budget_range)
            pizzas = pizzas.filter(id__in=[
                pizza.id for pizza in pizzas if self._calculate_price(pizza) <= budget_max
            ])

        # Vegetarian filter
        if is_vegetarian is not None:
            is_vegetarian = is_vegetarian.lower() == 'true'
            if is_vegetarian:
                pizzas = pizzas.annotate(
                    all_veg=Min('pizzaingredientlink__ingredient__is_vegetarian')
                ).filter(all_veg=True).distinct()

        # Vegan filter
        if is_vegan is not None:
            is_vegan = is_vegan.lower() == 'true'
            if is_vegan:
                pizzas = pizzas.annotate(
                    all_vegan=Min('pizzaingredientlink__ingredient__is_vegan')
                ).filter(all_vegan=True).distinct()

        return pizzas


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
            'pizza_id': pizza.id,
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
            'pizza_id': pizza.id,
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
            'pizza_id': pizza.id,
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