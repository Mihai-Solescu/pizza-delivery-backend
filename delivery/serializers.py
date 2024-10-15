# delivery/serializers.py

from rest_framework import serializers

from orders.models import Order
from .models import DeliveryPerson, Delivery


class DeliveryPersonSerializer(serializers.ModelSerializer):
    delivery_person_is_available = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DeliveryPerson
        fields = ['delivery_person_id', 'name', 'last_dispatched', 'postal_area', 'delivery_person_is_available']

    def get_delivery_person_is_available(self, obj):
        return obj.delivery_person_is_available()


class DeliverySerializer(serializers.ModelSerializer):
    delivery_person = DeliveryPersonSerializer(read_only=True)
    delivery_person_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryPerson.objects.all(),
        write_only=True,
        source='delivery_person',
        allow_null=True
    )
    orders = serializers.SerializerMethodField(read_only=True)
    order_ids = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        many=True,
        write_only=True,
        source='orders'
    )

    class Meta:
        model = Delivery
        fields = [
            'delivery_id',
            'delivery_person',
            'delivery_person_id',
            'delivery_status',
            'pizza_quantity',
            'delivery_postal_code',
            'delivery_address',
            'created_at',
            'orders',
            'order_ids',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from orders.models import Order
        self.fields['order_ids'].queryset = Order.objects.filter(status='confirmed')

    def get_orders(self, obj):
        from orders.serializers import OrderSerializer
        orders = obj.orders.all()
        serializer = OrderSerializer(orders, many=True, context=self.context)
        return serializer.data

    def create(self, validated_data):
        orders = validated_data.pop('orders', [])
        delivery = Delivery.objects.create(**validated_data)
        delivery.orders.set(orders)
        delivery.assign_delivery_person()
        delivery.save()
        return delivery