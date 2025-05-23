from django.db import transaction
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Min
from django.contrib.contenttypes.models import ContentType

import numpy as np

from customers.models import CustomerPreferences
from orders.models import OrderItem
from orders.recommender import update_preferences_review_decay, toppings_keys, recommend_pizzas
from .models import Pizza, Ingredient, Dessert, Drink, UserPizzaTag, PizzaIngredientLink, UserPizzaRating, \
    IngredientFilters
from .serializers import PizzaSerializer, IngredientSerializer, DessertSerializer, DrinkSerializer
from decimal import Decimal, InvalidOperation


class PizzaListViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get query parameters from the request
        smart = request.query_params.get('smart', 'false').lower() == 'true'
        order_type = request.query_params.get('order_type', None)
        budget_range = request.query_params.get('budget_range', None)
        is_vegetarian = request.query_params.get('is_vegetarian', None)
        is_vegan = request.query_params.get('is_vegan', None)

        # Dynamically handle toppings preferences as a vector
        toppings_list = [
            'tomato_sauce', 'cheese', 'pepperoni', 'BBQ_sauce', 'chicken',
            'pineapple', 'ham', 'mushrooms', 'olives', 'onions',
            'bacon', 'jalapenos', 'spinach', 'feta_cheese', 'red_peppers',
            'garlic', 'parmesan', 'sausage', 'anchovies', 'basil',
            'broccoli', 'mozzarella', 'ground_beef', 'zucchini',
            'sun_dried_tomatoes'
        ]

        # Initialize preferences vector with 0 (neutral)
        preferences_vector = np.zeros(len(toppings_list))

        # Populate the preferences vector based on query params (-1: dislike, 0: neutral, 1: like)
        for index, topping in enumerate(toppings_list):
            if topping in request.query_params:
                # Convert the value from query params to a Decimal before storing it in the preferences_vector
                try:
                    value = Decimal(request.query_params.get(topping))
                    preferences_vector[index] = value
                except (TypeError, ValueError, InvalidOperation):
                    # If the conversion fails, set the value to a neutral (0) as a fallback
                    preferences_vector[index] = Decimal(0)

        print(preferences_vector)

        # Filter the pizza queryset based on the request parameters
        pizzas = Pizza.objects.all()

        if order_type == 'normal':
            if smart:
                pizzas = self._pref_filter(budget_range, is_vegetarian, is_vegan, pizzas)
                pizzas = self._sort_by_similarity(pizzas, preferences_vector, request.user)

            # Serialize the smart filtered pizzas
            serializer = PizzaSerializer(pizzas, many=True, context={'request': request})
        else:
            pizzas = self._pref_filter(budget_range, is_vegetarian, is_vegan, pizzas)

            if smart:
                pizzas = self._pref_filter(budget_range, is_vegetarian, is_vegan, pizzas)
                pizzas = self._sort_by_similarity(pizzas, preferences_vector, request.user)
                best_pizza = pizzas[0]
                pizzas = [best_pizza]  # Keep only the best pizza
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

    def _sort_by_similarity(self, pizzas, preferences_vector, user, alpha=0.7, beta=0.3):
        """Sort pizzas based on similarity to user preferences using vectors and include user-specific pizza rating weight."""
        pizza_similarities = []

        for pizza in pizzas:
            # Get the pizza's ingredient vector (1 for in pizza, 0 for not in pizza)
            ingredients = PizzaIngredientLink.objects.filter(pizza=pizza).select_related('ingredient')
            pizza_vector = np.zeros(len(preferences_vector))

            for index, ingredient in enumerate(ingredients):
                ingredient_name = ingredient.ingredient.name
                if ingredient_name in preferences_vector:
                    pizza_vector[index] = 1  # Mark as present

            # Only calculate similarity if preferences vector has elements
            if preferences_vector.size > 0:
                # Compute cosine similarity manually using NumPy
                similarity = np.dot(pizza_vector, preferences_vector) / (np.linalg.norm(pizza_vector) * np.linalg.norm(
                    preferences_vector) + 1e-10)  # Add small epsilon to avoid division by zero
            else:
                similarity = 0  # Default similarity score if preferences are empty

            # Get the user-specific pizza rating from UserPizzaRating model
            user_rating = UserPizzaRating.objects.filter(user=user, pizza=pizza).first()
            if user_rating:
                pizza_rating = user_rating.rating
            else:
                pizza_rating = 3  # Default to 3 if no user rating exists

            # Normalize the pizza rating (assuming a 1-5 scale)
            normalized_rating = pizza_rating / 5

            # Calculate final score using the weighted sum of similarity and rating
            final_score = alpha * similarity + beta * normalized_rating

            pizza_similarities.append((pizza, final_score))

        # Sort pizzas by the final score
        sorted_pizzas = sorted(pizza_similarities, key=lambda x: x[1], reverse=True)

        # Return sorted pizzas
        return [pizza for pizza, score in sorted_pizzas]

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
                'vegetarian_tag': False,
                'vegan_tag': False,
            }
        )

        # Check the ingredients to determine vegetarian and vegan tags
        is_vegan = all(
            ingredient.is_vegan for ingredient in pizza.pizzaingredientlink_set.values_list('ingredient', flat=True)
        )
        is_vegetarian = all(
            ingredient.is_vegetarian for ingredient in
            pizza.pizzaingredientlink_set.values_list('ingredient', flat=True)
        )

        # Get the current user's rating for this pizza
        user_rating = UserPizzaRating.objects.filter(user=user, pizza=pizza).first()

        # Automatically set rate_tag to True if the user's rating is 4 or higher (but only if the user hasn't manually set the tag)
        if user_rating and user_rating.rating >= 4 and not user_pizza_tag.rate_tag_manual:
            user_pizza_tag.rate_tag = True

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
            'user_rating': user_rating.rating if user_rating else None  # Include user's rating in response
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, pizza_id):
        # Get the pizza object
        pizza = get_object_or_404(Pizza, id=pizza_id)
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

class RuleBasedQuickTopPizzaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        is_vegetarian = request.query_params.get('is_vegetarian', 'false').lower() == 'true'
        is_vegan = request.query_params.get('is_vegan', 'false').lower() == 'true'
        is_spicy = request.query_params.get('is_spicy', 'false').lower() == 'true'
        is_cheesy = request.query_params.get('is_cheesy', 'false').lower() == 'true'
        is_sweet = request.query_params.get('is_sweet', 'false').lower() == 'true'
        is_salty = request.query_params.get('is_salty', 'false').lower() == 'true'
        max_budget = Decimal(request.query_params.get('max_budget', 10))

        # Get all pizzas
        pizzas = Pizza.objects.all()

        filtered_pizzas = []

        # Filter pizzas based on ingredient properties
        for pizza in pizzas:
            ingredients = PizzaIngredientLink.objects.filter(pizza=pizza).select_related('ingredient')
            pizza_price = pizza.get_price()

            # Vegetarian and Vegan filters
            if is_vegetarian:
                if not all(i.ingredient.is_vegetarian for i in ingredients):
                    continue  # Skip pizzas that are not fully vegetarian

            if is_vegan:
                if not all(i.ingredient.is_vegan for i in ingredients):
                    continue  # Skip pizzas that are not fully vegan

            # Apply the spiciness, cheesiness, sweetness, and saltiness filters
            # if the filter is >= 0.5
            matches_spicy = (is_spicy and any(IngredientFilters.objects.get(ingredient=i.ingredient).spicy >= 0.5 for i in ingredients)) \
                #or (not is_spicy and all(IngredientFilters.objects.get(ingredient=i.ingredient).spicy < 0.5 for i in ingredients))
            matches_cheesy = (is_cheesy and any(IngredientFilters.objects.get(ingredient=i.ingredient).cheesy >= 0.5 for i in ingredients)) \
                #or (not is_cheesy and all(IngredientFilters.objects.get(ingredient=i.ingredient).cheesy < 0.5 for i in ingredients))
            matches_sweet = (is_sweet and any(IngredientFilters.objects.get(ingredient=i.ingredient).sweet >= 0.5 for i in ingredients)) \
                #or (not is_sweet and all(IngredientFilters.objects.get(ingredient=i.ingredient).sweet < 0.5 for i in ingredients))
            matches_salty = (is_salty and any(IngredientFilters.objects.get(ingredient=i.ingredient).salty >= 0.5 for i in ingredients)) \
                #or (not is_salty and all(IngredientFilters.objects.get(ingredient=i.ingredient).salty < 0.5 for i in ingredients))

            # If the filter is true, the pizza must have at least one ingredient matching that property
            if is_spicy and not matches_spicy:
                continue
            if is_cheesy and not matches_cheesy:
                continue
            if is_sweet and not matches_sweet:
                continue
            if is_salty and not matches_salty:
                continue

            # Check if pizza fits within the max budget
            if pizza_price > max_budget:
                continue

            # If the pizza matches all filters, add it to the result
            filtered_pizzas.append(pizza)

        # order top_pizzas based on popularity
        # where popularity is the number of times the pizza has been ordered
        # and is computed by summing the quantity of all order items that contain the pizza
        orders = OrderItem.objects.all()
        # for each pizza in filtered_pizzas, get the total quantity ordered
        # and sort the pizzas based on the total quantity ordered
        top_popularity_pizzas = sorted(filtered_pizzas, key=lambda x: sum(
            order.quantity for order in orders if order.content_type == ContentType.objects.get_for_model(Pizza) and order.object_id == x.id
        ), reverse=True)
        top_pizzas = top_popularity_pizzas[:3]

        # Serialize the top pizzas
        serializer = PizzaSerializer(top_pizzas, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class RecommenderQuickTopPizzaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # yse the recommender to get the top 3 pizzas
        top_pizzas = recommend_pizzas(request.user, top_n=3)

        # Serialize the top pizzas
        serializer = PizzaSerializer(top_pizzas, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PizzaUserRatingView(APIView):
    def post(self, request, pizza_id):
        # Get the pizza object
        pizza = get_object_or_404(Pizza, id=pizza_id)
        user = request.user  # Get the currently authenticated user

        # Check if UserPizzaTag exists for this user and pizza
        user_pizza_rating, created = UserPizzaRating.objects.get_or_create(
            user=user,
            pizza=pizza,
            defaults={
                'rating': 3,
            }
        )

        # Get data from the request
        rating = request.data.get('rating', False)

        # Update user preferences
        update_preferences_review_decay(user, pizza, rating)

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