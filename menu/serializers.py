from decimal import Decimal

from rest_framework import serializers
from .models import Pizza, Ingredient, Dessert, Drink, MenuItem, PizzaBase
from django.db.models import Sum


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class PizzaBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = PizzaBase
        fields = '__all__'


class PizzaSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    base_id = PizzaBaseSerializer(many=False)
    price = serializers.SerializerMethodField()
    vegan = serializers.SerializerMethodField()

    class Meta:
        model = Pizza
        fields = '__all__'

    def get_ingredients(self, obj):
        menu_item_id = obj.menu_item_id
        ingredients = Ingredient.objects.filter(menuitemingredient__menu_item=menu_item_id)

        return IngredientSerializer(ingredients, many=True).data

    def get_vegan(self, obj):
        menu_item_id = obj.menu_item_id
        is_base_veg = PizzaBase.objects.get(pizza__menu_item_id=menu_item_id).is_vegetarian
        ingredients = Ingredient.objects.filter(menuitemingredient__menu_item=menu_item_id)
        return all([ingredient.is_vegetarian for ingredient in ingredients] and is_base_veg)

#Now that's an one liner!
    def get_price(self, obj):
        # 2h on this oneliner lmao, Decimals are a pain
        cost_base = PizzaBase.objects.get(pizza__menu_item_id=obj.menu_item_id).cost or Decimal('0')
        cost_labor = Decimal('0.5')
        cost_ingredients = Ingredient.objects.filter(menuitemingredient__menu_item=obj.menu_item_id).aggregate(Sum('cost'))['cost__sum'] or Decimal('0')
        return round(cost_base + cost_ingredients + cost_labor, 3)

class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drink
        fields = '__all__'

class DessertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dessert
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    desserts = DessertSerializer(many=True)
    drinks = DrinkSerializer(many=True)
    pizzas = PizzaSerializer(many=True)

    class Meta:
        model = MenuItem
        fields = '__all__'