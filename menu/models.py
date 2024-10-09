from django.db import models
from customers.models import Customer
from django.contrib.auth.models import User
# Create your models here.

class Pizza(models.Model):
    pizza_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=30)

class UserPizzaTag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    rate_tag = models.BooleanField(default=False)
    order_tag = models.BooleanField(default=False)
    try_tag = models.BooleanField(default=False)
    vegetarian_tag = models.BooleanField(default=False)
    vegan_tag = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'pizza')

class Drink(models.Model):
    drink_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, default="")
    price = models.DecimalField(decimal_places=3, max_digits=8)

class Dessert(models.Model):
    dessert_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=3, max_digits=8)

class Ingredient(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    cost = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegan = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)

class PizzaIngredientLink(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('pizza', 'ingredient')