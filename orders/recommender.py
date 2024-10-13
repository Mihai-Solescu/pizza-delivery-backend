import numpy as np
from django.contrib.auth.models import User

from customers.models import CustomerPreferences
from menu.models import PizzaIngredientLink
from .models import Pizza, Ingredient

weight = 0.25 # Decay factor for exponential decay
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
            ingredient_vector[index] = 1

    return ingredient_vector

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def recommend_pizzas(user, top_n=5):
    ingredients, filters, max_budget = get_user_preferences(user)

    pizza_similarities = []
    for pizza in Pizza.objects.all():
        pizza_vector = get_pizza_vector(pizza)
        similarity = cosine_similarity(ingredients, pizza_vector)
        pizza_similarities.append((pizza, similarity))

    sorted_pizzas = sorted(pizza_similarities, key=lambda x: x[1], reverse=True)
    return [pizza for pizza, similarity in sorted_pizzas[:top_n]]


def update_preferences_review_decay(user, pizza, rating):
    ingredients, filters, max_budget = get_user_preferences(user)
    old_preferences = np.array(list(ingredients.values()))
    pizza_vector = get_pizza_vector(pizza)
    a = (rating - 3) / 2 # normalize [1, 5] to [-1, 1]
    new_preferences = old_preferences + a * pizza_vector
    ingredient_preferences = weight * new_preferences + (1 - weight) * old_preferences # exponential decay

    # print (ingredients)
    # print (pizza_vector)
    # print (new_preferences)
    # print (ingredient_preferences)

    for i, topping in enumerate(toppings_keys):
        ingredients[topping] = ingredient_preferences[i]

    save_preferences(user, ingredients, filters, max_budget)

def update_preferences_unrated_decay (user, pizza, review_score):
    preferences = CustomerPreferences.objects.get(user=user)
    old_preferences = np.array(preferences.preferences)
    pizza_vector = get_pizza_vector(pizza)
    new_preferences = old_preferences + pizza_vector
    preferences.preferences = weight * new_preferences + (1 - weight) * old_preferences # exponential decay
    preferences.save()

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
    max_budget = preferences.budget_range
    return ingredients, filters, max_budget

from django.db import transaction

@transaction.atomic
def save_preferences(user, ingredients, filters, max_budget):
    try:
        CustomerPreferences.objects.update_or_create(
            user=user,
            defaults={
                **{f"{topping}": ingredients[topping] for topping in toppings_keys},
                **{f"{filter_key}": filters[filter_key] for filter_key in filters},
                'budget_range': max_budget
            }
        )
    except Exception as e:
        print(f"Error saving preferences: {str(e)}")

