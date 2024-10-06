from decimal import Decimal

from rest_framework import serializers
from .models import Pizza, Ingredient, Dessert, Drink, PizzaIngredientLink
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

    class Meta:
        model = Pizza
        fields = '__all__'

    def get_ingredients(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj)
        return [{'name': i.ingredient.name, 'price': i.ingredient.cost, 'is_vegetarian': i.ingredient.is_vegetarian}
                for i in ingredients]

    def get_price(self, obj):
        labor_price = 0.5
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj)
        total_ingredient_cost = sum(ingredient.ingredient.cost for ingredient in ingredients)
        total_price = total_ingredient_cost + labor_price
        return round(total_price, 3)

    def get_is_vegan(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj)
        return all(ingredient.is_vegan for ingredient in ingredients)

    def get_is_vegetarian(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj)
        return all(ingredient.ingredient.is_vegetarian for ingredient in ingredients)

class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'

class DessertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dessert
        fields = '__all__'