import numpy as np
from .models import Pizza, Ingredient


def get_user_preference_vector(customer):
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


def update_user_profile_with_review(user, pizza, review_score):
    profile = UserProfile.objects.get(user=user)
    pizza_vector = get_pizza_vector(pizza)

    # Normalize review score to [-1, 1]
    a = (review_score - 2.5) / 2.5

    # Update preferences using a weighting scheme
    updated_preferences = profile.preferences + a * pizza_vector
    profile.preferences = updated_preferences
    profile.save()


def update_preferences_with_decay(user, pizza, w=0.5):
    profile = UserProfile.objects.get(user=user)
    old_preferences = np.array(profile.preferences)
    pizza_vector = get_pizza_vector(pizza)

    # Apply exponential decay
    new_preferences = w * pizza_vector + (1 - w) * old_preferences
    profile.preferences = new_preferences
    profile.save()
