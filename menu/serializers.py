from decimal import Decimal

from rest_framework import serializers
from .models import Pizza, Ingredient, Dessert, Drink, PizzaIngredientLink, UserPizzaTag, UserPizzaRating
from django.db.models import Sum

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
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')
        labor_price = Decimal(0.5)  # Adjust as needed
        total_ingredient_cost = sum(i.ingredient.cost for i in ingredients)
        total_price = total_ingredient_cost + labor_price
        return round(total_price, 3)

    def get_is_vegan(self, obj):
        return all(i.ingredient.is_vegan for i in self._get_ingredients(obj))

    def get_is_vegetarian(self, obj):
        return all(i.ingredient.is_vegetarian for i in self._get_ingredients(obj))

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

        # Automatically set rate_tag to True if the user's rating is 4 or higher
        user_rating = UserPizzaRating.objects.filter(user=user, pizza=obj).first()
        if user_rating and user_rating.rating >= 4:
            user_pizza_tag.rate_tag = True

        # Save the updated user_pizza_tag
        user_pizza_tag.save()

        return {
            'rate_tag': user_pizza_tag.rate_tag,
            'order_tag': user_pizza_tag.order_tag,
            'try_tag': user_pizza_tag.try_tag,
            'vegetarian_tag': user_pizza_tag.vegetarian_tag,
            'vegan_tag': user_pizza_tag.vegan_tag,
        }

    def get_rating(self, obj):
        user = self.context['request'].user
        user_pizza_rating, created = UserPizzaRating.objects.get_or_create(
            user=user,
            pizza=obj,
            defaults={
                'rating': 2
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