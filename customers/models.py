from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class Customer(AbstractBaseUser):
    customer_id = models.AutoField(primary_key=True)  #In Django we don't need to define primary key, but it makes clear
    name = models.CharField(max_length=30, unique=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    birthdate = models.DateField()  # If it's children, then we must know whether they can use the service.
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=64)
    total_pizzas_ordered = models.IntegerField(default=0)
    discount_code = models.ForeignKey('customers.DiscountCode', on_delete=models.SET_NULL, blank=True, null=True) #Ref, how to do this in django?
    is_birthday_freebie = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerAddress(models.Model):
    customer_address_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customers.Customer', related_name="address", on_delete=models.CASCADE) # This automatically references back to Customer tables primary key aka customer_id
    address_line = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=20)
    is_primary = models.BooleanField()

class DiscountCode(models.Model):
    discount_code_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=11)
    amount = models.DecimalField(decimal_places=3, max_digits=8)
    description = models.CharField(max_length=100)
    is_redeemed = models.BooleanField(default=False)
    expiration_date = models.DateField()

class CustomerPreferences(models.Model):
    customer_preferences_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customers.Customer', related_name="preferences", on_delete=models.CASCADE)
    is_vegetarian = models.BooleanField()
    is_vegan = models.BooleanField()
    is_spicy = models.BooleanField()