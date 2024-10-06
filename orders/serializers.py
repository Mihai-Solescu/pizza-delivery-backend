from decimal import Decimal

import customers.models
from menu.models import Pizza, PizzaBase, Ingredient, Drink
from .models import Order, OrderMenuItem, OrderMenuItemExtraIngredient, MenuItem
from delivery.models import Delivery
from rest_framework import serializers
from customers.models import Customer
import calendar


# This gets the ingredients, we use it as a component to build up the final menu item serializer
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'is_vegetarian', 'cost']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class OrderMenuItemExtraIngredientSerializer(serializers.ModelSerializer):
    ingredient_id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')

    class Meta:
        model = OrderMenuItemExtraIngredient
        fields = ['ingredient_id', 'quantity']


class OrderMenuItemSerializer(serializers.ModelSerializer):
    extra_ingredients = OrderMenuItemExtraIngredientSerializer(many=True, required=False)

    class Meta:
        model = OrderMenuItem
        fields = ['id', 'order', 'menu_item', 'quantity', 'extra_ingredients']

    def create(self, validated_data):
        extra_ingredients_data = validated_data.pop('extra_ingredients', [])
        order_menu_item = OrderMenuItem.objects.create(**validated_data)
        for ingredient_data in extra_ingredients_data:
            OrderMenuItemExtraIngredient.objects.create(
                order_menu_item=order_menu_item,
                **ingredient_data
            )
        return order_menu_item


class OrderSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source='customer')
    order_menu_items = OrderMenuItemSerializer(many = True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'order_date', 'status', 'total_price', 'discount_applied', 'delivery_address',
                  'estimated_delivery_time', 'order_menu_items']