from decimal import Decimal

import customers.models
from menu.models import Pizza, PizzaBase, Ingredient, Drink
from .models import Order, OrderMenuItem, OrderMenuItemExtraIngredient, MenuItem
from delivery.models import Delivery
from rest_framework import serializers
from django.db.models import Sum
from datetime import date, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from menu.views import MenuItemSerializer
from customers.serializers import CustomerSerializer
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
    menu_item_id = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all(), source='menu_item')
    extra_ingredients = OrderMenuItemExtraIngredientSerializer(many=True, required=False)

    class Meta:
        model = OrderMenuItem
        fields = ['menu_item_id', 'quantity', 'extra_ingredients']

    def create(self, validated_data):
        extra_ingredients_data = validated_data.pop('extra_ingredients', [])
        order_menu_item = OrderMenuItem.objects.create(**validated_data)
        for extra_ingredient_data in extra_ingredients_data:
            OrderMenuItemExtraIngredient.objects.create(order_menu_item=order_menu_item, **extra_ingredient_data)
        return order_menu_item


class OrderSerializer(serializers.ModelSerializer):
    order_menu_items = OrderMenuItemSerializer(many=True)
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source='customer')

    class Meta:
        model = Order
        fields = ['customer_id', 'order_date', 'status', 'total_price', 'discount_applied', 'delivery_address',
                  'order_menu_items', 'estimated_delivery_time']

    def create(self, validated_data):
        pizza_amount = 0
        order_menu_items_data = validated_data.pop('order_menu_items')
        order = Order.objects.create(**validated_data)
        if order.customer.total_pizzas_ordered >= 10:
            order.total_price = order.total_price * Decimal('0.9')
            order.customer.total_pizzas_ordered = order.customer.total_pizzas_ordered - 10
            order.customer.save()
            order.save()
        for order_menu_item_data in order_menu_items_data:
            extra_ingredients_data = order_menu_item_data.pop('extra_ingredients')
            order_menu_item = OrderMenuItem.objects.create(order=order, **order_menu_item_data)
            if order_menu_item.menu_item.type == 'pizza':
                order.customer.total_pizzas_ordered += order_menu_item.quantity
                pizza_amount += order_menu_item.quantity
                order.customer.save()
            for extra_ingredient_data in extra_ingredients_data:
                OrderMenuItemExtraIngredient.objects.create(order_menu_item=order_menu_item, **extra_ingredient_data)

        if order.order_menu_items.filter(menu_item__type='pizza').count() == 0:
            raise ValidationError('You must order at least one pizza')

        if order.customer.discount_code is not None:
            if not order.customer.discount_code.is_redeemed:
                order.total_price = order.total_price * Decimal('0.9')
                order.customer.discount_code.is_redeemed = True
                order.customer.discount_code.save()
                order.save()

        drinkFree = False
        pizzaFree = False
        if (order.customer.birthdate.month == date.today().month and
                order.customer.birthdate.day == date.today().day and
                not order.customer.is_birthday_freebie):
            for order_menu_item in order.order_menu_items.all():
                if order_menu_item.menu_item.type == 'pizza':
                    order.total_price = order.total_price - Pizza.objects.get(menu_item_id=order_menu_item.menu_item).price
                    pizzaFree = True
                    if pizzaFree and drinkFree:
                        order.customer.is_birthday_freebie = True
                        order.customer.save()
                    order.save()
                    break
            for order_menu_item in order.order_menu_items.all():
                if order_menu_item.menu_item.type == 'drink':
                    order.total_price = order.total_price - Drink.objects.get(menu_item_id=order_menu_item.menu_item).price
                    drinkFree = True
                    if pizzaFree and drinkFree:
                        order.customer.is_birthday_freebie = True
                        order.customer.save()
                        break
                    order.save()
                    break
        order.estimated_delivery_time = 2*pizza_amount+10
        order.save()
        return order

    def retrieve(self, validated_data):
        order = Order.objects.filter(status="pending")
        return order
