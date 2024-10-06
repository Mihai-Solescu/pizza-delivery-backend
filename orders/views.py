from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from datetime import date, timedelta
import calendar

from menu.models import Pizza, Drink, Dessert
from .models import Order

class AddItemToOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order, created = Order.objects.get_or_create(
            customer=user.customer_profile,
            status='open',
            defaults={'order_date': date.today(), 'total_price': 0}
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


class FinalizeOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, status='finalized')
            if order.customer != request.user.customer:
                raise PermissionDenied("No entry! ")
        except Order.DoesNotExist:
            return Response({'error': 'Order not found!'}, status=status.HTTP_404_NOT_FOUND)

        if not order.order_menu_items.filter(menu_item__type='pizza').exists():
            return Response({'error': 'Need one pizza please.'}, status=status.HTTP_400_BAD_REQUEST)

        order.process_order()
        return Response({
            'message': 'Order accepted.',
            'estimated_delivery_time': order.estimated_delivery_time,
            'total_price': str(order.total_price)
        }, status=status.HTTP_200_OK)


class EarningAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        orders = Order.objects.filter(order_date__range=[first_day, last_day])

        total_earnings = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        return Response({'Earnings': total_earnings})