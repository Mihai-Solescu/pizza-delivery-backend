import numpy as np
from django.contrib.auth.models import User

from customers.models import CustomerPreferences
from .models import Pizza, Ingredient

weight = 0.25 # Decay factor for exponential decay

def get_user_preference_vector(user):
    customer = user.customer_profile
    ingredient_preferences = [
        customer.pepperoni,
        customer.mushrooms,
        customer.onions,
        customer.olives,
        customer.sun_dried_tomatoes,
        customer.bell_peppers,
        customer.chicken,
        customer.bacon,
        customer.ham,
        customer.sausage,
        customer.ground_beef,
        customer.anchovies,
        customer.pineapple,
        customer.basil,
        customer.broccoli,
        customer.zucchini,
        customer.garlic,
        customer.jalapenos,
        customer.BBQ_sauce,
        customer.red_peppers,
        customer.spinach,
        customer.feta_cheese,
    ]
    other_preferences = [
        customer.cheese_preference,
        customer.spiciness_level,
        customer.is_vegetarian,
        customer.is_vegan,
        customer.pizza_size,
    ]
    return np.array(ingredient_preferences), other_preferences

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