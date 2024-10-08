from datetime import timezone
from rest_framework import serializers
from orders.models import Order
from .models import Delivery, DeliveryPerson


class DeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = ('delivery_id', 'order_id', 'delivery_person_id', 'delivery_status')

    def create(self, validated_data):
        delivery_person = validated_data.get('delivery_person')
        order_id = validated_data.get('order_id')
        delivery_person.last_dispatched = timezone.now()
        delivery_person.save()
        delivery = Delivery.objects.create(**validated_data)
        Order.objects.filter(order_id=order_id).update(delivery=delivery.delivery_id)
        return delivery

    def update(self, instance, validated_data):
        instance.order_id = validated_data.get('order_id', instance.order_id)
        instance.delivery_person_id = validated_data.get('delivery_person_id', instance.delivery_person_id)
        instance.delivery_status = validated_data.get('delivery_status', instance.delivery_status)
        instance.save()
        return instance

    def retrieve (self, instance):
        return Delivery.objects.get(pk=instance.delivery_id)

    def delete(self, instance):
        instance.delete()
        return instance

class DeliveryPersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryPerson
        fields = ('delivery_person_id', 'name', 'is_available', 'postal_area')

    def create(self, validated_data):
        return DeliveryPerson.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.is_available = validated_data.get('is_available', instance.is_available)
        instance.postal_area = validated_data.get('postal_area', instance.postal_area)
        instance.save()
        return instance

    def retrieve (self, instance):
        return DeliveryPerson.objects.get(pk=instance.delivery_person_id)

    def delete(self, instance):
        instance.delete()
        return instance