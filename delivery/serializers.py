from rest_framework import serializers

from delivery.models import Delivery, DeliveryPerson
from orders.models import Order


class DeliveryPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPerson
        fields = ['delivery_person_id', 'name', 'postal_area', 'last_dispatched']

class DeliverySerializer(serializers.ModelSerializer):
    delivery_person = DeliveryPersonSerializer(read_only=True)

    class Meta:
        model = Delivery
        fields = [
            'delivery_id', 'delivery_status', 'pizza_quantity',
            'delivery_address', 'postal_code', 'delivery_person'
        ]

class OrderSerializer(serializers.ModelSerializer):
    delivery = DeliverySerializer(read_only=True)
    estimated_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id', 'order_date', 'status', 'customer',
            'delivery', 'estimated_delivery_time'
        ]

    def get_estimated_delivery_time(self, obj):
        return obj.estimated_delivery_time