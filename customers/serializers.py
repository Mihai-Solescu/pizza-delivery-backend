from django.contrib.auth.models import User
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

# This should create User  + Customer account
    def create(self, data):
        user = User.objects.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        customer = Customer.objects.create(
            user=user,
            phone_number=data['phone_number']
        )
        return customer


