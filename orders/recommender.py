import numpy as np
from django.contrib.auth.models import User

from customers.models import CustomerPreferences
from .models import Pizza, Ingredient

weight = 0.25 # Decay factor for exponential decay

def get_user_preference_vector(user):
    preferences = CustomerPreferences.objects.get(user)
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
    return ingredients, filters

def get_pizza_vector(pizza):
    ingredient_ids = pizza.ingredients.values_list('id', flat=True)
    ingredient_vector = [1 if i in ingredient_ids else 0 for i in range(Ingredient.objects.count())]
    return np.array(ingredient_vector)

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

def recommend_pizzas(user, top_n=5):
    user_preferences = get_user_preference_vector(user)

    pizza_similarities = []
    for pizza in Pizza.objects.all():
        pizza_vector = get_pizza_vector(pizza)
        similarity = cosine_similarity(user_preferences, pizza_vector)
        pizza_similarities.append((pizza, similarity))

    sorted_pizzas = sorted(pizza_similarities, key=lambda x: x[1], reverse=True)
    return [pizza for pizza, similarity in sorted_pizzas[:top_n]]


def update_preferences_review_decay(user, pizza, review_score):
    preferences = CustomerPreferences.objects.get(user=user)
    old_preferences = np.array(preferences.preferences)
    pizza_vector = get_pizza_vector(pizza)
    a = (review_score - 3) / 2 # normalize [1, 5] to [-1, 1]
    new_preferences = old_preferences + a * pizza_vector
    preferences.preferences = weight * new_preferences + (1 - weight) * old_preferences # exponential decay
    preferences.save()

def update_preferences_unrated_decay (user, pizza, review_score):
    preferences = CustomerPreferences.objects.get(user=user)
    old_preferences = np.array(preferences.preferences)
    pizza_vector = get_pizza_vector(pizza)
    new_preferences = old_preferences + pizza_vector
    preferences.preferences = weight * new_preferences + (1 - weight) * old_preferences # exponential decay
    preferences.save()