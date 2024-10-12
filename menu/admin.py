from django.contrib import admin
from .models import Pizza, Drink, Dessert, Ingredient, PizzaIngredientLink, UserPizzaTag, UserPizzaRating

admin.site.register(Pizza)
admin.site.register(Drink)
admin.site.register(Dessert)
admin.site.register(Ingredient)
admin.site.register(PizzaIngredientLink)
admin.site.register(UserPizzaTag)
admin.site.register(UserPizzaRating)
