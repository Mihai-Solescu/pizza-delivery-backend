from django.db import models
from customers.models import Customer
# Create your models here.

class PizzaBase(models.Model):
    name = models.CharField(max_length=30)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_vegetarian = models.BooleanField(default=False)


class Pizza(models.Model):
    pizza_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    base_id = models.ForeignKey('menu.PizzaBase', on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=3, max_digits=8) # Ingredient + labor cost + Profit margin
    time_to_cook = models.IntegerField()
    user_id = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    menu_item_id = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE, related_name='pizzas')


class Drink(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=3, max_digits=8)
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE, related_name='drinks')

class Dessert(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=3, max_digits=8)
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE, related_name='desserts')


class MenuItem(models.Model):
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=20)


class Ingredient(models.Model):
    name = models.CharField(max_length=30)
    cost = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegetarian = models.BooleanField(default=False)


class MenuItemIngredient(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('menu_item', 'ingredient')