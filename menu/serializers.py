from decimal import Decimal
from rest_framework import serializers
from .models import Pizza, Drink, Dessert, Ingredient, PizzaIngredientLink, UserPizzaTag, UserPizzaRating
from django.contrib.auth.models import User
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class PizzaSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    is_vegan = serializers.SerializerMethodField()
    is_vegetarian = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Pizza
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')
        return [
            {
                'name': i.ingredient.name,
                'price': i.ingredient.cost
            }
            for i in ingredients
        ]

    def get_price(self, obj):
        return round(obj.get_price(), 3)

    def get_is_vegan(self, obj):
        return all(i.ingredient.is_vegan for i in self._get_ingredients(obj))

    def get_is_vegetarian(self, obj):
        return all(i.ingredient.is_vegetarian for i in self._get_ingredients(obj))

    def get_rating(self, obj):
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return None

        user = request.user

        user_pizza_rating, created = UserPizzaRating.objects.get_or_create(
            user=user,
            pizza=obj,
            defaults={
                'rating': 3
            }
        )
        return user_pizza_rating.rating

    def get_tags(self, obj):
        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}

        user = request.user

        try:
            user_pizza_tag = UserPizzaTag.objects.get(user=user, pizza=obj)
        except UserPizzaTag.DoesNotExist:
            user_pizza_tag = UserPizzaTag.objects.create(
                user=user,
                pizza=obj,
                vegetarian_tag=self.get_is_vegetarian(obj),
                vegan_tag=self.get_is_vegan(obj)
            )

        smart = request.query_params.get('smart', 'false').lower() == 'true'
        if smart:
            user_pizza_rating = UserPizzaRating.objects.filter(user=user, pizza=obj).first()
            if user_pizza_rating and user_pizza_rating.rating >= 4:
                user_pizza_tag.rate_tag = True

            user_pizza_matrix_normalized, users, pizzas, mean_user_ratings = self.get_user_pizza_matrix()

            user_similarity = self.calculate_user_similarity(user_pizza_matrix_normalized)

            predicted_ratings = self.predict_user_ratings(user, user_pizza_matrix_normalized, user_similarity, users, pizzas, mean_user_ratings)

            recommended_pizzas = self.get_recommended_pizzas(user, predicted_ratings, pizzas)

            if obj in recommended_pizzas:
                user_pizza_tag.try_tag = True

        user_pizza_tag.save()

        return {
            'rate_tag': user_pizza_tag.rate_tag,
            'order_tag': user_pizza_tag.order_tag,
            'try_tag': user_pizza_tag.try_tag,
            'vegetarian_tag': user_pizza_tag.vegetarian_tag,
            'vegan_tag': user_pizza_tag.vegan_tag,
        }

    def _get_ingredients(self, obj):
        return PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')

    def get_user_pizza_matrix(self):
        ratings = UserPizzaRating.objects.all()

        users = {user.id: idx for idx, user in enumerate(User.objects.all())}
        pizzas = {pizza.id: idx for idx, pizza in enumerate(Pizza.objects.all())}

        user_pizza_matrix = np.zeros((len(users), len(pizzas)))

        for rating in ratings:
            user_idx = users[rating.user_id]
            pizza_idx = pizzas[rating.pizza_id]
            user_pizza_matrix[user_idx, pizza_idx] = rating.rating

        mean_user_ratings = np.mean(user_pizza_matrix, axis=1).reshape(-1, 1)
        user_pizza_matrix_normalized = user_pizza_matrix - mean_user_ratings

        return user_pizza_matrix_normalized, users, pizzas, mean_user_ratings

    def calculate_user_similarity(self, user_pizza_matrix_normalized):
        user_similarity = cosine_similarity(user_pizza_matrix_normalized)
        return user_similarity

    def predict_user_ratings(self, user, user_pizza_matrix_normalized, user_similarity, users, pizzas, mean_user_ratings):
        user_idx = users.get(user.id, None)
        if user_idx is None:
            return np.zeros(len(pizzas))

        user_ratings = user_pizza_matrix_normalized[user_idx, :]

        predicted_ratings = np.zeros(user_ratings.shape)

        similar_users = user_similarity[user_idx]

        for pizza_idx in range(len(pizzas)):
            mask = user_pizza_matrix_normalized[:, pizza_idx] != 0
            similar_users_pizza = similar_users[mask]
            ratings_for_pizza = user_pizza_matrix_normalized[mask, pizza_idx]

            if len(similar_users_pizza) == 0:
                continue

            weighted_sum = np.dot(similar_users_pizza, ratings_for_pizza)
            similarity_sum = np.sum(np.abs(similar_users_pizza))

            if similarity_sum > 0:
                predicted_ratings[pizza_idx] = weighted_sum / similarity_sum
            else:
                predicted_ratings[pizza_idx] = 0

        predicted_ratings += mean_user_ratings[user_idx].flatten()

        return predicted_ratings

    def get_recommended_pizzas(self, user, predicted_ratings, pizzas):
        recommended_pizza_indices = np.where(predicted_ratings >= 4)[0]

        pizza_ids = list(pizzas.keys())
        recommended_pizzas = []
        for idx in recommended_pizza_indices:
            if idx < len(pizza_ids):
                pizza_id = pizza_ids[idx]
                try:
                    pizza = Pizza.objects.get(pk=pizza_id)
                    recommended_pizzas.append(pizza)
                except Pizza.DoesNotExist:
                    continue

        return recommended_pizzas


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'


class DessertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dessert
        fields = '__all__'