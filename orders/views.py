from django.contrib.contenttypes.models import ContentType
from django.views.generic import ListView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import date, timedelta
import calendar

from menu.models import Pizza, Drink, Dessert
from menu.serializers import PizzaSerializer, DrinkSerializer, DessertSerializer
from .models import Order, OrderItem


class GetOrderItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            order, created = Order.objects.get_or_create(customer=user.customer_profile, status='open')
        except Order.MultipleObjectsReturned:
            return Response({'error': 'Multiple open orders found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        order_items = order.items.all()

        pizzas = []
        drinks = []
        desserts = []

        for item in order_items:
            if item.content_type.model == 'pizza':
                pizza = get_object_or_404(Pizza, id=item.object_id)
                pizzas.append({
                    'pizza': PizzaSerializer(pizza, many=False, context={'request': request}).data,
                    'quantity': item.quantity
                })
            elif item.content_type.model == 'drink':
                drink = get_object_or_404(Drink, id=item.object_id)
                drinks.append({
                    'drink': DrinkSerializer(drink, many=False, context={'request': request}).data,
                    'quantity': item.quantity
                })
            elif item.content_type.model == 'dessert':
                dessert = get_object_or_404(Dessert, id=item.object_id)
                desserts.append({
                    'dessert': DessertSerializer(dessert, many=False, context={'request': request}).data,
                    'quantity': item.quantity
                })

        return Response({
            'pizza': pizzas,
            'drink': drinks,
            'dessert': desserts,
        }, status=status.HTTP_200_OK)


class GetOrderItemCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        order, created = Order.objects.get_or_create(customer=user.customer_profile, status='open')

        if not order:
            return Response({'error': 'No open order'}, status=status.HTTP_404_NOT_FOUND)

        item_count = OrderItem.objects.filter(order=order).aggregate(Sum('quantity'))['quantity__sum']
        return Response({'item_count': item_count}, status=status.HTTP_200_OK)


class AddItemToOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order, created = Order.objects.get_or_create(
            customer=user.customer_profile,
            status='open'
        )

        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if item_type == 'pizza':
            item = get_object_or_404(Pizza, id=item_id)
        elif item_type == 'drink':
            item = get_object_or_404(Drink, id=item_id)
        elif item_type == 'dessert':
            item = get_object_or_404(Dessert, id=item_id)
        else:
            return Response({'error': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)

        order.add_menu_item(item, quantity)
        return Response({'message': f'{item_type.capitalize()} added.'}, status=status.HTTP_200_OK)


class RemoveItemFromOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order = Order.objects.filter(customer=user.customer_profile, status='open').first()

        if not order:
            return Response({'error': 'No open order exists'}, status=status.HTTP_404_NOT_FOUND)

        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        if item_type == 'pizza':
            item = get_object_or_404(Pizza, id=item_id)
        elif item_type == 'drink':
            item = get_object_or_404(Drink, id=item_id)
        elif item_type == 'dessert':
            item = get_object_or_404(Dessert, id=item_id)
        else:
            return Response({'error': 'Invalid item'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order.remove_menu_item(item, quantity)
            return Response({'message': f'{item_type.capitalize()} removed'}, status=status.HTTP_200_OK)
        except OrderItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_400_BAD_REQUEST)


class FinalizeOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order = Order.objects.filter(customer=user.customer_profile, status='open').first()

        if not order:
            return Response({'error': 'No open order'}, status=status.HTTP_404_NOT_FOUND)

        order.process_order()
        return Response({
            'message': 'Order finalized.',
            'total_price': order.calculate_total_price(),
            'estimated_delivery_time': order.estimated_delivery_time
        }, status=status.HTTP_200_OK)


class OrderTotalPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        order, created = Order.objects.get_or_create(customer=user.customer_profile, status='open')

        if not order:
            return Response({'error': 'No open order'}, status=status.HTTP_404_NOT_FOUND)

        total_price = order.calculate_total_price()
        return Response({'total_price': total_price}, status=status.HTTP_200_OK)


class RedeemDiscountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        discount_code = request.data.get('discount_code')
        user = request.user
        order = Order.objects.filter(customer=user.customer_profile, status='open').first()

        if not order:
            return Response({'error': 'No open order'}, status=status.HTTP_404_NOT_FOUND)

        order.apply_discount_code(discount_code)
        if order.redeemable_discount_applied:
            return Response({'total_price': order.calculate_total_price()}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Not valid discount code.'}, status=status.HTTP_400_BAD_REQUEST)


class EarningAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        orders = Order.objects.filter(order_date__range=[first_day, last_day], status='confirmed')

        # Apply filters
        gender = request.query_params.get('gender', None)
        age_min = request.query_params.get('age_min', None)
        age_max = request.query_params.get('age_max', None)
        postal_code = request.query_params.get('postal_code', None)

        if gender:
            orders = orders.filter(customer__gender=gender)

        if age_min:
            date_threshold = today - timedelta(days=int(age_min)*365)
            orders = orders.filter(customer__birthdate__lte=date_threshold)

        if age_max:
            date_threshold = today - timedelta(days=int(age_max)*365)
            orders = orders.filter(customer__birthdate__gte=date_threshold)

        if postal_code:
            orders = orders.filter(customer__postal_code=postal_code)

        total_earnings = sum([order.calculate_total_price() for order in orders])

        return Response({'Earnings': total_earnings}, status=status.HTTP_200_OK)


class LatestOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            latest_order = Order.objects.filter(customer=request.user.customer_profile).order_by('-order_date').first()

            if latest_order:
                delivery = latest_order.delivery
                delivery_data = None
                if delivery:
                    delivery_data = {
                        'delivery_status': delivery.delivery_status,
                        'pizza_quantity': delivery.pizza_quantity,
                        'delivery_address': delivery.delivery_address,
                        'delivery_postal_code': delivery.delivery_postal_code,
                        'delivery_person': delivery.delivery_person.name if delivery.delivery_person else None,
                    }

                return Response({
                    'id': latest_order.pk,
                    'status': latest_order.status,
                    'estimated_delivery_time': latest_order.estimated_delivery_time,  # As integer minutes
                    'delivery': delivery_data,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'No orders you!'}, status=status.HTTP_404_NOT_FOUND)

        except Order.DoesNotExist:
            return Response({'error': 'Order has not been existing'}, status=status.HTTP_404_NOT_FOUND)


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id, customer=request.user.customer_profile, status__in=['open', 'confirmed'])
            if order.cancel_order_within_time():
                return Response({'status': 'Order canceled'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Cannot modify anymore'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order cant be canceled'}, status=status.HTTP_404_NOT_FOUND)


class ConfirmedOrderPizzasAPIView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        pizza_content_type = ContentType.objects.get_for_model(Pizza)
        order_items = OrderItem.objects.filter(
            order__status='confirmed',
            content_type=pizza_content_type
        )
        pizza_ids = order_items.values_list('object_id', flat=True).distinct()
        pizzas = Pizza.objects.filter(id__in=pizza_ids)
        serializer = PizzaSerializer(pizzas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

