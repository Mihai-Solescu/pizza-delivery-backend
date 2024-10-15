from rest_framework import serializers
from customers.models import Customer
from delivery.models import Delivery
from .models import Order, OrderItem
from django.contrib.contenttypes.models import ContentType
from menu.serializers import PizzaSerializer, DrinkSerializer, DessertSerializer
from customers.serializers import CustomerSerializer
from delivery.serializers import DeliverySerializer  # Import DeliverySerializer


class OrderItemSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        slug_field='model',
        queryset=ContentType.objects.all()
    )
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'content_type', 'object_id', 'content_object', 'quantity']

    def get_content_object(self, obj):
        if obj.content_type.model == 'pizza':
            return PizzaSerializer(obj.content_object).data
        elif obj.content_type.model == 'drink':
            return DrinkSerializer(obj.content_object).data
        elif obj.content_type.model == 'dessert':
            return DessertSerializer(obj.content_object).data
        else:
            return None


from rest_framework import serializers
from customers.models import Customer
from .models import Order, OrderItem
from customers.serializers import CustomerSerializer

class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True,
    )
    delivery_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    items = OrderItemSerializer(many=True, read_only=True)
    item_ids = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_id', 'order_date', 'status', 'delivery_id',
            'redeemable_discount_applied', 'loyalty_discount_applied',
            'freebie_applied', 'estimated_delivery_time', 'items', 'item_ids'
        ]

    def create(self, validated_data):
        item_data = validated_data.pop('item_ids', [])
        customer = validated_data.pop('customer')
        delivery_id = validated_data.pop('delivery_id', None)
        delivery = None

        if delivery_id:
            delivery = Delivery.objects.get(delivery_id=delivery_id)

        order = Order.objects.create(customer=customer, delivery=delivery, **validated_data)

        for item in item_data:
            content_type = ContentType.objects.get(model=item['content_type'])
            OrderItem.objects.create(
                order=order,
                content_type=content_type,
                object_id=item['object_id'],
                quantity=item.get('quantity', 1)
            )
        order.process_order()
        return order