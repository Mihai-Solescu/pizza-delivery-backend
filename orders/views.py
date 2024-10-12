from platform import system

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from datetime import date
import calendar

from menu.models import Pizza, Drink, Dessert
from menu.serializers import PizzaSerializer, DrinkSerializer, DessertSerializer
from .models import Order, OrderItem
from .serializers import OrderSerializer


class GetOrderItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the customer associated with the user
        user = request.user

        try:
            # Fetch the open order for the customer
            order, created = Order.objects.get_or_create(customer=user.customer_profile, status='open')
        except Order.MultipleObjectsReturned:
            return Response({'error': 'Multiple open orders found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        order_items = order.items.all()

        # Initialize lists to store pizzas, drinks, and desserts
        pizzas = []
        drinks = []
        desserts = []

        # Loop through all the order items and categorize them based on content_type
        for item in order_items:
            if item.content_type == 'pizza':
                pizza = get_object_or_404(Pizza, pizza_id=item.object_id)
                pizzas.append({'pizza': PizzaSerializer(pizza).data, 'quantity': item.quantity})
            elif item.content_type == 'drink':
                drink = get_object_or_404(Drink, drink_id=item.object_id)
                drinks.append({'drink': DrinkSerializer(drink).data, 'quantity': item.quantity})
            elif item.content_type == 'dessert':
                dessert = get_object_or_404(Dessert, dessert_id=item.object_id)
                desserts.append({'dessert': DessertSerializer(dessert).data, 'quantity': item.quantity})

        # Return the items categorized as pizzas, drinks, and desserts
        return Response({
            'pizzas': pizzas,
            'drinks': drinks,
            'desserts': desserts,
        }, status=status.HTTP_200_OK)


class AddItemToOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order, created = Order.objects.get_or_create(
            customer=user.customer_profile,
            status='open',
            defaults={'order_date': date.today()}
        )

        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if item_type == 'pizza':
            item = get_object_or_404(Pizza, pizza_id=item_id)
        elif item_type == 'drink':
            item = get_object_or_404(Drink, drink_id=item_id)
        elif item_type == 'dessert':
            item = get_object_or_404(Dessert, dessert_id=item_id)
        else:
            return Response({'error': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)

        order.add_menu_item(item, quantity)
        return Response({'message': f'{item_type.capitalize()} added to order.'}, status=status.HTTP_200_OK)

class RemoveItemFromOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order = Order.objects.filter(customer=user.customer_profile, status='open').first()

        if not order:
            return Response({'error': 'No open order found.'}, status=status.HTTP_404_NOT_FOUND)

        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if item_type == 'pizza':
            item = get_object_or_404(Pizza, pizza_id=item_id)
        elif item_type == 'drink':
            item = get_object_or_404(Drink, drink_id=item_id)
        elif item_type == 'dessert':
            item = get_object_or_404(Dessert, dessert_id=item_id)
        else:
            return Response({'error': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)

        order.remove_menu_item(item, quantity)
        return Response({'message': f'{item_type.capitalize()} removed from order.'}, status=status.HTTP_200_OK)

class FinalizeOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order = Order.objects.filter(customer=user.customer_profile, status='open').first()

        if not order:
            return Response({'error': 'No open order found.'}, status=status.HTTP_404_NOT_FOUND)

        # Process the order (calculate total price, apply discounts, freebies, etc.)
        order.process_order()
        return Response({
            'message': 'Order finalized.',
            'total_price': order.calculate_total_price(),  # Call the method to calculate total price
            'estimated_delivery_time': order.estimated_delivery_time
        }, status=status.HTTP_200_OK)


class EarningAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        orders = Order.objects.filter(order_date__range=[first_day, last_day])

        # Since total_price is no longer a field, calculate total earnings dynamically
        total_earnings = sum([order.calculate_total_price() for order in orders])
        return Response({'Earnings': total_earnings}, status=status.HTTP_200_OK)


class OrderStatusView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            return Response({
                'order_id': order.pk,
                'status': order.status,
                'estimated_delivery_time': order.estimated_delivery_time
            }, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

class OrderCancelView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            if order.cancel_order_within_time():
                return Response({'status': 'Order canceled'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Cant modify order'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)
