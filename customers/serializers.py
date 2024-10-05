from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Customer, DiscountCode, CustomerPreferences, CustomerData


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


class CustomerPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPreferences
        fields = '__all__'
        read_only_fields = ('customer',)


class CustomerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerData
        fields = '__all__'
        read_only_fields = ('customer',)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)


class CustomerRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'address', 'postal_code', 'city']

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username']
        )
        customer = Customer.objects.create(
            user=user,
            address_line=validated_data['address'],
            postal_code=validated_data['postal_code'],
            city=validated_data['city']
        )
        return customer


