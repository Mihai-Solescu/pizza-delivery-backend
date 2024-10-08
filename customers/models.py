from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User


# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    customer_id = models.AutoField(primary_key=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    address_line = models.CharField(max_length=30, null=True, blank=True)
    postal_code = models.CharField(max_length=20, default=0)
    city = models.CharField(max_length=30, null=True, blank=True)
    total_pizzas_ordered = models.IntegerField(default=0)
    is_birthday_freebie = models.BooleanField(default=False)
    discount_code = models.CharField(max_length=32, unique=True)
    discount_applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerPreferences(models.Model):
    customer_preferences_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('customers.Customer', related_name="preferences", on_delete=models.CASCADE)

    # Pizza Base Preference (Encoded as integers)
    # 0: Thin Crust, 1: Thick Crust, 2: Gluten-Free, 3: Regular
    pizza_base = models.IntegerField(choices=[
        (0, 'Thin Crust'),
        (1, 'Thick Crust'),
        (2, 'Gluten-Free'),
        (3, 'Regular')
    ])

    # Favourite Sauce (Encoded as integers)
    # 0: Tomato, 1: Pesto, 2: White Sauce
    favourite_sauce = models.IntegerField(choices=[
        (0, 'Tomato'),
        (1, 'Pesto'),
        (2, 'White Sauce')
    ])

    # Cheese Preference (Encoded as integers)
    # 0: Mozzarella, 1: Cheddar, 2: No Cheese, 3: Vegan Cheese
    cheese_preference = models.IntegerField(choices=[
        (0, 'Mozzarella'),
        (1, 'Cheddar'),
        (2, 'No Cheese'),
        (3, 'Vegan Cheese')
    ])

    # Preferred Toppings (Binary flags for each topping)
    # 1 if selected, 0 otherwise
    topping_pepperoni = models.BooleanField(default=False)
    topping_mushrooms = models.BooleanField(default=False)
    topping_onions = models.BooleanField(default=False)
    topping_olives = models.BooleanField(default=False)
    topping_bell_peppers = models.BooleanField(default=False)
    topping_chicken = models.BooleanField(default=False)

    # Spiciness Level (Encoded as integers)
    # 0: Mild, 1: Medium, 2: Spicy
    spiciness_level = models.IntegerField(choices=[
        (0, 'Mild'),
        (1, 'Medium'),
        (2, 'Spicy')
    ])

    # Dietary Restrictions (Binary flags)
    # 1 if applicable, 0 otherwise
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)

    # Pizza Size (Encoded as integers)
    # 0: Small, 1: Medium, 2: Large
    pizza_size = models.IntegerField(choices=[
        (0, 'Small'),
        (1, 'Medium'),
        (2, 'Large')
    ])

    # Budget Range (Use numeric ranges or midpoints for similarity calculations)
    budget_range = models.DecimalField(max_digits=5, decimal_places=2)


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

