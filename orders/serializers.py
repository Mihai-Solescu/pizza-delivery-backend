from decimal import Decimal

import customers.models
from menu.models import Pizza, PizzaBase, Ingredient
from .models import Order, OrderMenuItem, OrderMenuItemExtraIngredient
from rest_framework import serializers
from django.db.models import Sum
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from menu.views import MenuItemSerializer
from customers.serializers import CustomerSerializer
import calendar

# This gets the ingredients, we use it as a component to build up the final menu item serializer
class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id']


class OrderMenuItemExtraIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=True)

    class Meta:
        model = OrderMenuItemExtraIngredient
        fields = ['order_menu_item', 'ingredient', 'quantity']

    extra_kwargs = {
        'ingredient': {'required': False}
    }


class OrderMenuItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()
    extra_ingredients = OrderMenuItemExtraIngredientSerializer(many=True, required=False)

    class Meta:
        model = OrderMenuItem
        fields = '__all__'

    def create(self, validated_data):
        extra_ingredients_data = validated_data.pop('extra_ingredients')
        order_menu_item = OrderMenuItem.objects.create(**validated_data)
        for extra_ingredient_data in extra_ingredients_data:
            OrderMenuItemExtraIngredient.objects.create(order_menu_item=order_menu_item, **extra_ingredient_data)
        return order_menu_item

class OrderSerializer(serializers.ModelSerializer):
    order_menu_items = OrderMenuItemSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        pizza_count = 0
        pizza_count_bd = 0
        drink_count_bd = 0
        # Order menu items are nested, so we pop them out to create them separately
        # they include the extra ingredients
        order_menu_items_data = validated_data.pop('order_menu_items', [])
        order = Order.objects.create(**validated_data)
        if not order.customer.discount_code.is_redeemed:
            order.total_price = order.total_price * Decimal('0.9')
            order.customer.discount_code.is_redeemed = True
            order.customer.discount_code.save()
            order.save()
        for order_menu_item_data in order_menu_items_data:
            order_menu_item = OrderMenuItem.objects.create(order=order, **order_menu_item_data)
            if order_menu_item.menu_item.type == 'pizza':
                order.customer.total_pizzas_ordered += 1
                order.customer.save()
                pizza_count += 1

            # Birthday free stuff
            if order.customer.birthdate == date.today():
               if order_menu_item.menu_item.type == 'pizza' and pizza_count_bd == 0:
                    order.total_price = order.total_price - order_menu_item.menu_item.price
                    pizza_count_bd = 1
                    order.save()
               if order_menu_item.menu_item.type == 'drink' and drink_count_bd == 0:
                   order.total_price = order.total_price - order_menu_item.menu_item.price
                   drink_count_bd = 1


            extra_ingredients_data = order_menu_item_data.pop('extra_ingredients', [])
            for extra_ingredient_data in extra_ingredients_data:
                OrderMenuItemExtraIngredient.objects.create(order_menu_item=order_menu_item, **extra_ingredient_data)
        if order.customer.total_pizzas_ordered >= 10:
            order.total_price = order.total_price * Decimal('0.9')
            order.customer.total_pizzas_ordered = order.customer.total_pizzas_ordered - 10
            order.customer.save()
            order.save()

        if pizza_count == 0:
            return ValidationError('You must order at least one pizza')
        return order

    def retrieve(self, validated_data):
        order = Order.objects.filter(status="pending")
        return order