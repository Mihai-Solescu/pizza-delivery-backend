from django.db import models
from customers.models import Customer
# Create your models here.

class Pizza(models.Model):
    pizza_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)

class Drink(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=3, max_digits=8)

class Dessert(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=3, max_digits=8)

class Ingredient(models.Model):
    name = models.CharField(max_length=30)
    cost = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegetarian = models.BooleanField(default=False)

class PizzaIngredient(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    is_vegan = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('menu_item', 'ingredient')