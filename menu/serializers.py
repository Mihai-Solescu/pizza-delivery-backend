from decimal import Decimal

from rest_framework import serializers
from .models import Pizza, Ingredient, Dessert, Drink, PizzaIngredientLink, UserPizzaTag, UserPizzaRating
from django.db.models import Sum
from django.contrib.auth.models import User
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

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

    def get_user_pizza_matrix(self):
        # Fetch all user-pizza ratings
        ratings = UserPizzaRating.objects.all()

        # Create dictionaries to map users and pizzas to row/column indices
        users = {user.id: idx for idx, user in enumerate(User.objects.all())}
        pizzas = {pizza.id: idx for idx, pizza in enumerate(Pizza.objects.all())}

        print(f"Users: {users}")
        print(f"Pizzas: {pizzas}")

        # Initialize the matrix with zeros (unrated pizzas will remain 0)
        user_pizza_matrix = np.zeros((len(users), len(pizzas)))

        # Fill the matrix with user ratings where available
        for rating in ratings:
            user_idx = users[rating.user_id]
            pizza_idx = pizzas[rating.pizza_id]
            user_pizza_matrix[user_idx, pizza_idx] = rating.rating

        print(f"User-Pizza Matrix (before normalization):\n{user_pizza_matrix}")

        # Normalize the matrix by subtracting the mean rating for each user
        mean_user_ratings = np.mean(user_pizza_matrix, axis=1).reshape(-1, 1)  # Compute mean ratings for each user
        user_pizza_matrix_normalized = user_pizza_matrix - mean_user_ratings  # Subtract mean ratings

        print(f"Mean User Ratings:\n{mean_user_ratings}")
        print(f"User-Pizza Matrix (after normalization):\n{user_pizza_matrix_normalized}")

        return user_pizza_matrix_normalized, users, pizzas, mean_user_ratings

    def calculate_user_similarity(self, user_pizza_matrix_normalized):
        # Compute cosine similarity between users (rows in the matrix)
        user_similarity = cosine_similarity(user_pizza_matrix_normalized)
        print(f"User Similarity:\n{user_similarity}")
        return user_similarity

    def predict_user_ratings(self, user, user_pizza_matrix_normalized, user_similarity, users, pizzas,
                             mean_user_ratings):
        # Get the index of the current user
        user_idx = users.get(user.id, None)  # Use user.id instead of user.user_id to match Django's user model

        if user_idx is None:
            return np.zeros(len(pizzas))  # Return empty predictions if the user is not found

        user_ratings = user_pizza_matrix_normalized[user_idx, :]  # Get the user's normalized ratings row

        predicted_ratings = np.zeros(user_ratings.shape)  # Initialize predicted ratings

        print(f"User {user} normalized ratings: {user_ratings}")

        # Loop through each pizza to calculate the predicted rating
        for pizza_idx in range(len(pizzas)):
            similar_users = user_similarity[user_idx]  # Get similarity scores for this user with all other users

            # Filter out users who have rated the current pizza
            users_who_rated = user_pizza_matrix_normalized[:, pizza_idx] != 0
            similar_users = similar_users[users_who_rated]
            ratings_for_pizza = user_pizza_matrix_normalized[users_who_rated, pizza_idx]

            print(f"Pizza {pizza_idx}: Similar users {similar_users}")
            print(f"Pizza {pizza_idx}: Ratings for pizza {ratings_for_pizza}")

             # If no users have rated this pizza, we can't predict it
            if len(similar_users) == 0:
                continue  # Skip this pizza, as no similar users have rated it

            # Compute the weighted sum of similar users' ratings for this pizza
            weighted_sum = np.dot(similar_users, ratings_for_pizza)
            similarity_sum = np.sum(np.abs(similar_users))  # Sum of similarities of users who rated this pizza

            # Ensure no division by zero
            if similarity_sum > 0:
                predicted_ratings[pizza_idx] = weighted_sum / similarity_sum
            else:
                predicted_ratings[pizza_idx] = 0  # Default to 0 if no similarity sum is available

            print(f"Predicted rating for pizza {pizza_idx}: {predicted_ratings[pizza_idx]}")

        # Add back the user's mean rating to each predicted rating to de-normalize
        predicted_ratings += mean_user_ratings[user_idx].flatten()

        print(f"Predicted ratings for user {user} (after adding back mean):\n{predicted_ratings}")

        return predicted_ratings

    def get_tags(self, obj):
        user = self.context['request'].user  # Get the authenticated user

        # Get or create the UserPizzaTag for this user and pizza
        user_pizza_tag, created = UserPizzaTag.objects.get_or_create(
            user=user,
            pizza=obj,
            defaults={
                'rate_tag': False,
                'order_tag': False,
                'try_tag': False,
                'vegetarian_tag': self.get_is_vegetarian(obj),  # Set based on pizza data
                'vegan_tag': self.get_is_vegan(obj)  # Set based on pizza data
            }
        )

        smart = self.context['request'].query_params.get('smart', 'false').lower() == 'true'

        if smart:
            # Automatically set rate_tag to True if the user's rating is 4 or higher
            user_rating = UserPizzaRating.objects.filter(user=user, pizza=obj).first()
            if user_rating and user_rating.rating >= 4:
                user_pizza_tag.rate_tag = True
            user_pizza_matrix_normalized, users, pizzas, mean_user_ratings = self.get_user_pizza_matrix()

            user_similarity = self.calculate_user_similarity(user_pizza_matrix_normalized)

            # Predict ratings for this user
            predicted_ratings = self.predict_user_ratings(user, user_pizza_matrix_normalized, user_similarity, users, pizzas, mean_user_ratings)

            # Get recommended pizzas
            recommended_pizzas = self.get_recommended_pizzas(user, predicted_ratings, pizzas)

            # If the current pizza is in the recommended list, mark it as "try"
            if obj in recommended_pizzas:
                user_pizza_tag.try_tag = True

        # Save the updated user_pizza_tag
        user_pizza_tag.save()

        return {
            'rate_tag': user_pizza_tag.rate_tag,
            'order_tag': user_pizza_tag.order_tag,
            'try_tag': user_pizza_tag.try_tag,
            'vegetarian_tag': user_pizza_tag.vegetarian_tag,
            'vegan_tag': user_pizza_tag.vegan_tag,
        }

    def get_recommended_pizzas(self, user, predicted_ratings, pizzas):
        # Get pizzas with predicted ratings >= 4
        recommended_pizza_indices = np.where(predicted_ratings >= 4)[0]

        print(f"Recommended pizza indices: {recommended_pizza_indices}")

        # Convert matrix indices back to pizza IDs using the pizza dictionary
        pizza_ids = list(pizzas.keys())
        recommended_pizzas = []
        for idx in recommended_pizza_indices:
            if idx < len(pizza_ids):
                pizza_id = pizza_ids[idx]  # Get the pizza ID based on the index
                try:
                    pizza = Pizza.objects.get(pk=pizza_id)  # Query the database using the pizza ID
                    recommended_pizzas.append(pizza)
                    print(f"Recommended pizza {pizza.name} (ID: {pizza_id})")
                except Pizza.DoesNotExist:
                    continue  # Skip if the pizza doesn't exist

        print(f"Final recommended pizzas: {[pizza.name for pizza in recommended_pizzas]}")
        return recommended_pizzas

    def get_rating(self, obj):
        user = self.context['request'].user
        user_pizza_rating, created = UserPizzaRating.objects.get_or_create(
            user=user,
            pizza=obj,
            defaults={
                'rating': 3
            }
        )

        return user_pizza_rating.rating

    def _get_ingredients(self, obj):
        """Helper method to retrieve ingredients."""
        return PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'

class DessertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dessert
        fields = '__all__'