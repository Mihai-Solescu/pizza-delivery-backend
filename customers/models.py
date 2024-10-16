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
    budget_range = models.FloatField(default=7.0)# Ensure unique user-pizza combinations


class CustomerData(models.Model):
    customer_data_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customers.Customer', related_name="data", on_delete=models.CASCADE)

    # Average time it takes for a customer to complete an order (in seconds)
    average_order_time = models.FloatField(null=True, blank=True, help_text="Average order time in seconds")

    # Number of times the user clicked on pizza information
    pizza_info_clicks = models.IntegerField(default=0, help_text="Number of times user clicked on pizza info")

    # Scroll depth (integer - num of last pizza depth)
    scroll_deepness = models.IntegerField(null=True, blank=True, help_text="Scroll depth as an integer")

    # Number of times the user abandoned the customization process
    abandoned_customization_times = models.IntegerField(default=0, help_text="Times the user abandoned customization")

    # A JSONField to track the number of times each ingredient was removed
    times_ingredient_removed = models.JSONField(default=dict, help_text="Dictionary of ingredients and times removed")

    # A JSONField to track how many times each pizza was ordered
    times_pizza_ordered = models.JSONField(default=dict, help_text="Dictionary of pizzas and times they were ordered")

    # A JSONField to store the average rating for each pizza
    avg_pizza_rating = models.JSONField(default=dict, help_text="Dictionary of pizzas and their average ratings")

