from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    total_pizzas_ordered = models.IntegerField(default=0)
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