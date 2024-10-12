import os
import json
from django.core.management.base import BaseCommand
from menu.models import Pizza, Drink, Dessert, Ingredient, PizzaIngredientLink, IngredientFilters


class Command(BaseCommand):
    help = 'Load menu data from JSON files into the database'

    def handle(self, *args, **kwargs):
        # Define the file paths for your JSON files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pizzas_file = os.path.join(base_dir, 'pizzas.json')
        ingredients_file = os.path.join(base_dir, 'ingredients.json')
        pizza_ingredients_file = os.path.join(base_dir, 'pizza_ingredient_links.json')
        drinks_file = os.path.join(base_dir, 'drinks.json')
        desserts_file = os.path.join(base_dir, 'desserts.json')
        ingredient_filters_file = os.path.join(base_dir, 'ingredient_filters.json')

        # Load the data from the JSON files
        self.load_pizzas(pizzas_file)
        self.load_ingredients(ingredients_file)
        self.load_pizza_ingredients(pizza_ingredients_file)
        self.load_drinks(drinks_file)
        self.load_desserts(desserts_file)
        self.load_ingredient_filters(ingredient_filters_file)

    def load_pizzas(self, file_path):
        with open(file_path, 'r') as f:
            pizzas = json.load(f)
            for pizza_data in pizzas:
                pizza, created = Pizza.objects.get_or_create(name=pizza_data['name'])
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Pizza '{pizza.name}' created"))

    def load_ingredients(self, file_path):
        with open(file_path, 'r') as f:
            ingredients = json.load(f)
            for ingredient_data in ingredients:
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_data['name'],
                    cost=ingredient_data['cost'],
                    is_vegan=ingredient_data['is_vegan'],
                    is_vegetarian=ingredient_data['is_vegetarian']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Ingredient '{ingredient.name}' created"))

    def load_pizza_ingredients(self, file_path):
        with open(file_path, 'r') as f:
            pizza_ingredients = json.load(f)
            for link_data in pizza_ingredients:
                pizza = Pizza.objects.get(name=link_data['pizza_name'])
                ingredient = Ingredient.objects.get(name=link_data['ingredient_name'])
                link, created = PizzaIngredientLink.objects.get_or_create(
                    pizza=pizza,
                    ingredient=ingredient
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Link for Pizza '{pizza.name}' and Ingredient '{ingredient.name}' created"))

    def load_drinks(self, file_path):
        with open(file_path, 'r') as f:
            drinks = json.load(f)
            for drink_data in drinks:
                drink, created = Drink.objects.get_or_create(
                    name=drink_data['name'],
                    price=drink_data['price']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Drink '{drink.name}' created"))

    def load_desserts(self, file_path):
        with open(file_path, 'r') as f:
            desserts = json.load(f)
            for dessert_data in desserts:
                dessert, created = Dessert.objects.get_or_create(
                    name=dessert_data['name'],
                    price=dessert_data['price']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Dessert '{dessert.name}' created"))

    def load_ingredient_filters(self, file_path):
        with open(file_path, 'r') as f:
            ingredient_filters = json.load(f)
            for filter_data in ingredient_filters:
                ingredient = Ingredient.objects.get(name=filter_data['ingredient_name'])
                filters, created = IngredientFilters.objects.get_or_create(
                    ingredient=ingredient,
                    is_vegan=filter_data['is_vegan'],
                    is_vegetarian=filter_data['is_vegetarian'],
                    spicy=filter_data['spicy'],
                    is_meat=filter_data['is_meat'],
                    is_vegetable=filter_data['is_vegetable'],
                    cheesy=filter_data['cheesy'],
                    sweet=filter_data['sweet'],
                    salty=filter_data['salty']
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Filters for Ingredient '{ingredient.name}' created"))