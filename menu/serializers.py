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
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')
        return [{'name': i.ingredient.name,
                 'price': i.ingredient.cost,
                 'is_vegetarian': i.ingredient.is_vegetarian,
                 'is_vegan': i.ingredient.is_vegan}  # Include is_vegan
                for i in ingredients]

    def get_price(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')
        labor_price = Decimal(0.5) # 2h wasted on this line
        total_ingredient_cost = sum(ingredient.ingredient.cost for ingredient in ingredients)
        total_price = total_ingredient_cost + labor_price
        return round(total_price, 3)

    def get_is_vegan(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')
        return all(i.ingredient.is_vegan for i in ingredients)

    def get_is_vegetarian(self, obj):
        ingredients = PizzaIngredientLink.objects.filter(pizza=obj).select_related('ingredient')
        return all(i.ingredient.is_vegetarian for i in ingredients)

class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'

class DessertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dessert
        fields = '__all__'