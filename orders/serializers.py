from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer', 'order_date', 'status', 'total_price', 'discount_applied',
                  'delivery_address', 'estimated_delivery_time']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model =
        fields = ['menu_item', 'quantity']