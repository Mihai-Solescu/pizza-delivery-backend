from decimal import Decimal
from django.db import models
from customers.models import Customer
from django.contrib.auth.models import User

class Pizza(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=30)

    def get_price(self):
        ingredients = PizzaIngredientLink.objects.filter(pizza=self).select_related('ingredient')
        labor_price = Decimal(0.5)  # Adjust as needed
        total_ingredient_cost = sum(i.ingredient.cost for i in ingredients)
        total_price = total_ingredient_cost + labor_price
        return total_price

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

class UserPizzaRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    rating = models.IntegerField(default=3)

    class Meta:
        unique_together = ('user', 'pizza')

class Drink(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255, default="")
    price = models.DecimalField(decimal_places=3, max_digits=8)

class Dessert(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=255, default="")
    name = models.CharField(max_length=30)
    price = models.DecimalField(decimal_places=3, max_digits=8)

class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    cost = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegan = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)

class IngredientFilters(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE)
    is_vegan = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegetarian = models.DecimalField(decimal_places=3, max_digits=8)
    spicy = models.DecimalField(decimal_places=3, max_digits=8)
    is_meat = models.DecimalField(decimal_places=3, max_digits=8)
    is_vegetable = models.DecimalField(decimal_places=3, max_digits=8)
    cheesy = models.DecimalField(decimal_places=3, max_digits=8)
    sweet = models.DecimalField(decimal_places=3, max_digits=8)
    salty = models.DecimalField(decimal_places=3, max_digits=8)

class PizzaIngredientLink(models.Model):
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('pizza', 'ingredient')