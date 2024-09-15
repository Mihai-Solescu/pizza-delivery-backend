from django.contrib import admin
from .models import PizzaBase, Pizza, Drink, Dessert, MenuItem, Ingredient, MenuItemIngredient

admin.site.register(PizzaBase)
admin.site.register(Pizza)
admin.site.register(Drink)
admin.site.register(Dessert)
admin.site.register(MenuItem)
admin.site.register(Ingredient)
admin.site.register(MenuItemIngredient)