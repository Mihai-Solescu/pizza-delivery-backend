from rest_framework import serializers
from .models import Customer, DiscountCode, CustomerPreferences


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = '__all__'

    def create(self, validated_data):
        customer = Customer.objects.get(pk=validated_data.pop('customer'))
        discount_code = DiscountCode.objects.create(**validated_data)
        customer.discount_code = discount_code
        customer.save()
        return discount_code


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)


class CustomerRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 'address', 'postal_code', 'city']

    def create(self, validated_data):
        customer = Customer.objects.create_user(**validated_data)
        CustomerPreferences.objects.create(customer=customer)
        return customer


