from decimal import Decimal

import numpy as np
from django.contrib.auth.models import User

from customers.models import CustomerPreferences
from menu.models import PizzaIngredientLink
from .models import Pizza

weight = Decimal(0.25) # Decay factor for exponential decay
toppings_keys = [
    'tomato_sauce', 'cheese', 'pepperoni', 'BBQ_sauce', 'chicken',
    'pineapple', 'ham', 'mushrooms', 'olives', 'onions',
    'bacon', 'jalapenos', 'spinach', 'feta_cheese', 'red_peppers',
    'garlic', 'parmesan', 'sausage', 'anchovies', 'basil',
    'broccoli', 'mozzarella', 'ground_beef', 'zucchini',
    'sun_dried_tomatoes'
]

def get_pizza_vector(pizza):
    ingredients = PizzaIngredientLink.objects.filter(pizza=pizza).select_related('ingredient')
    ingredient_vector = np.zeros(len(toppings_keys))
    for ingredient_link in ingredients:
        ingredient_name = ingredient_link.ingredient.name.lower().replace(' ',
                                                                          '_')  # Convert ingredient name to match toppings_keys format
        if ingredient_name in toppings_keys:
            index = toppings_keys.index(ingredient_name)
            ingredient_vector[index] = Decimal(1)

    return ingredient_vector

def cosine_similarity(vec1, vec2):
    fvec1 = np.array([float(v) for v in vec1])
    fvec2 = np.array([float(v) for v in vec2])
    dot_product = np.dot(fvec1, fvec2)
    norm1 = np.linalg.norm(fvec1)
    norm2 = np.linalg.norm(fvec2)
    return dot_product / (norm1 * norm2)

def recommend_pizzas(user, top_n=3):
    ingredients, filters, max_budget = get_user_preferences(user)
    ingredient_vec = np.array([Decimal(value) for value in ingredients.values()])

    pizza_similarities = []
    for pizza in Pizza.objects.all():
        pizza_vector = get_pizza_vector(pizza)
        similarity = cosine_similarity(ingredient_vec, pizza_vector)
        pizza_similarities.append((pizza, similarity))

    sorted_pizzas = sorted(pizza_similarities, key=lambda x: x[1], reverse=True)
    return [pizza for pizza, similarity in sorted_pizzas[:top_n]]


def update_preferences_review_decay(user, pizza, rating):
    ingredients, filters, max_budget = get_user_preferences(user)
    old_preferences = [Decimal(value) for value in ingredients.values()]
    pizza_vector = get_pizza_vector(pizza)
    pizza_vector = [Decimal(v) for v in pizza_vector]
    a = Decimal((rating - 3) / 2)  # normalize [1, 5] to [-1, 1]
    new_preferences = [(a * pizza_ing) for old_pref, pizza_ing in zip(old_preferences, pizza_vector)]
    ingredient_preferences = [(Decimal(weight) * new_pref + (1 - Decimal(weight)) * old_pref)
                              for new_pref, old_pref in zip(new_preferences, old_preferences)]
    print(old_preferences)
    print (new_preferences)
    print (ingredient_preferences)
    save_preferences(user, ingredient_preferences, filters, max_budget)

def update_preferences_order_decay(user, order):
    preferences = CustomerPreferences.objects.get(user=user)
    ingredients, filters, max_budget = get_user_preferences(user)
    old_preferences = {key: Decimal(value) for key, value in ingredients.items()}
    # For each pizza in the order, update the preferences based on its ingredients
    for item in order.items.filter(content_type__model='pizza'):
        pizza = item.content_object  # Get the actual pizza object
        pizza_ingredients = PizzaIngredientLink.objects.filter(pizza=pizza).select_related('ingredient')

        # Loop through each ingredient in the pizza and update the preferences
        for ingredient_link in pizza_ingredients:
            ingredient_name = ingredient_link.ingredient.name.lower().replace(' ', '_')
            if ingredient_name in old_preferences:
                # Apply the update: exponential decay with a +1 factor for the ordered pizza's ingredients
                old_preferences[ingredient_name] = (weight * Decimal(1)) + (1 - weight) * Decimal(old_preferences[ingredient_name])

    # Save the updated preferences back to the database
    for topping, new_preference in old_preferences.items():
        setattr(preferences, topping, new_preference)

    preferences.save()

    return "User preferences updated successfully."


def get_user_preferences(user):
    preferences = CustomerPreferences.objects.get(user=user)
    ingredients = {
        'tomato_sauce' : preferences.tomato_sauce,
        'cheese' : preferences.cheese,
        'pepperoni' : preferences.pepperoni,
        'BBQ_sauce' : preferences.BBQ_sauce,
        'chicken' : preferences.chicken,
        'pineapple' : preferences.pineapple,
        'ham' : preferences.ham,
        'mushrooms' : preferences.mushrooms,
        'olives' : preferences.olives,
        'onions' : preferences.onions,
        'bacon' : preferences.bacon,
        'jalapenos' : preferences.jalapenos,
        'spinach' : preferences.spinach,
        'feta_cheese' : preferences.feta_cheese,
        'red_peppers' : preferences.red_peppers,
        'garlic' : preferences.garlic,
        'parmesan' : preferences.parmesan,
        'sausage' : preferences.sausage,
        'anchovies' : preferences.anchovies,
        'basil' : preferences.basil,
        'broccoli' : preferences.broccoli,
        'mozzarella' : preferences.mozzarella,
        'ground_beef' : preferences.ground_beef,
        'zucchini' : preferences.zucchini,
        'sun_dried_tomatoes' : preferences.sun_dried_tomatoes
    }
    filters = {
        'spicy': preferences.spicy,
        'is_vegetarian': preferences.is_vegetarian,
        'is_vegan': preferences.is_vegan,
        'is_meat': preferences.is_meat,
        'is_vegetable': preferences.is_vegetable,
        'cheesy': preferences.cheesy,
        'sweet': preferences.sweet,
        'salty': preferences.salty
    }
    max_budget = preferences.max_budget
    return ingredients, filters, max_budget

def save_preferences(user, ingredients, filters, max_budget):
    try:
        # Assuming 'ingredients' is now correctly mapped
        ingredients_dict = {topping: ingredients[i] for i, topping in enumerate(toppings_keys)}

        # Attempt to update or create the customer preferences
        preferences, created = CustomerPreferences.objects.update_or_create(
            user=user,
            defaults={
                **ingredients_dict,  # Use the converted dictionary
                **{f"{filter_key}": filters[filter_key] for filter_key in filters},
                'budget_range': max_budget
            }
        )

        # Log whether the preferences were created or updated
        if created:
            print(f"Preferences created for user {user}")
        else:
            print(f"Preferences updated for user {user}")

    except Exception as e:
        print(f"Error saving preferences: {str(e)}")