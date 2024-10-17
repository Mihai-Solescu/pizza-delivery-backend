from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    gender = models.CharField(max_length=1, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    address_line = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=20, default=0)
    city = models.CharField(max_length=30, null=True, blank=True)

    total_pizzas_ordered = models.IntegerField(default=0)
    is_birthday_freebie = models.BooleanField(default=False)
    discount_code = models.CharField(max_length=32, null=True, blank=True)
    discount_applied = models.BooleanField(default=False)

class CustomerPreferences(models.Model):
    customer_preferences_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile1')

    # Preferred Toppings (Decimal flags for each topping)
    # Values: 1 for liked, 0 for neutral, -1 for dislike
    tomato_sauce = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    cheese = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    pepperoni = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    BBQ_sauce = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    chicken = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    pineapple = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    ham = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    mushrooms = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    olives = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    onions = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    bacon = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    jalapenos = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    spinach = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    feta_cheese = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    red_peppers = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    garlic = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    parmesan = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    sausage = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    anchovies = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    basil = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    broccoli = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    mozzarella = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    ground_beef = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    zucchini = models.DecimalField(default=0, max_digits=3, decimal_places=3)
    sun_dried_tomatoes = models.DecimalField(default=0, max_digits=3, decimal_places=3)

    # filters
    spicy = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_meat = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegetable = models.DecimalField(decimal_places=3, max_digits=8)
    cheesy = models.DecimalField(decimal_places=3, max_digits=8)
    sweet = models.DecimalField(decimal_places=3, max_digits=8)
    salty = models.DecimalField(decimal_places=3, max_digits=8)

    # Budget Range (Use numeric ranges or midpoints for similarity calculations)
    max_budget = models.DecimalField(default=10, decimal_places=3, max_digits=8)

