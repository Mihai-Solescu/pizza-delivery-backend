import numpy as np
from .models import Pizza, Ingredient


def get_user_preference_vector(customer):
    # Get user preference vector
    user_preferences = [
        customer.favourite_sauce,
        customer.cheese_preference,
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
        customer.spiciness_level,
        customer.is_vegetarian,
        customer.is_vegan,
        customer.pizza_size
    ]
    return np.array(user_preferences)


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
    # Get user preference vector
    user_preferences = get_user_preference_vector(user)

    # Calculate similarity between user preferences and each pizza
    pizza_similarities = []
    for pizza in Pizza.objects.all():
        pizza_vector = get_pizza_vector(pizza)
        similarity = cosine_similarity(user_preferences, pizza_vector)
        pizza_similarities.append((pizza, similarity))

    # Sort pizzas by similarity score
    sorted_pizzas = sorted(pizza_similarities, key=lambda x: x[1], reverse=True)

    # Return the top N recommended pizzas
    return [pizza for pizza, similarity in sorted_pizzas[:top_n]]
