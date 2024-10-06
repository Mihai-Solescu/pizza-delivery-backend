# views.py

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from datetime import date, timedelta
import calendar

from .models import Order, OrderMenuItem, OrderMenuItemExtraIngredient
from .serializers import OrderSerializer, OrderMenuItemSerializer, OrderMenuItemExtraIngredientSerializer
from django.core.exceptions import PermissionDenied

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=self.request.user.customer)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)

    @action(detail=True, methods=['post'])
    def apply_discounts(self, request, pk=None):
        try:
            order = self.get_object()
            if order.customer != request.user.customer:
                raise PermissionDenied("Perm denied.")
        except Order.DoesNotExist:
            return Response({'error': 'No order.'}, status=status.HTTP_404_NOT_FOUND)
        discount_code = request.data.get('discount_code')
        if discount_code:
            pass;
        order.apply_loyalty_discount()
        order.apply_discount_code()
        order.save()
        return Response({'message': 'Discounts applied.', 'total_price': str(order.total_price)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        try:
            order = self.get_object()
            if order.customer != request.user.customer:
                raise PermissionDenied("No perm.")
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not order.order_items.filter(menu_item__type='pizza').exists():
            return Response({'error': 'You must order at least one pizza.'}, status=status.HTTP_400_BAD_REQUEST)

        order.process_order()
        order.status = 'confirmed'
        order.save()

        return Response({
            'message': 'Order finalized.',
            'estimated_delivery_time': order.estimated_delivery_time,
            'total_price': str(order.total_price)
        }, status=status.HTTP_200_OK)

class EarningView(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['age', 'gender', 'postal_code']

    def list(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        orders = Order.objects.filter(order_date__range = [first_day, last_day])
        age = request.query_params.get('age')
        gender = request.query_params.get('gender')
        postal_code = request.query_params.get('postal_code')
        if age:
            birthdate_threshold = date.today() - timedelta(days=int(age) * 365)
            orders = orders.filter(customer__birthdate__lte=birthdate_threshold)
        if gender:
            orders = orders.filter(customer__gender = gender)
        if postal_code:
            orders = orders.filter(customer__address__postal_code=postal_code)

        total_earnings = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        return Response({
            'Earnings': total_earnings,
            'Filters': {
                'age': age,
                'gender': gender,
                'postal_code': postal_code
            }
        })
class OrderMenuItemView(viewsets.ModelViewSet):
    queryset = OrderMenuItem.objects.all()
    serializer_class = OrderMenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderMenuItem.objects.filter(order__customer=self.request.user.customer)

class OrderMenuItemExtraIngredientView(viewsets.ModelViewSet):
    queryset = OrderMenuItemExtraIngredient.objects.all()
    serializer_class = OrderMenuItemExtraIngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderMenuItemExtraIngredient.objects.filter(order_menu_item__order__customer = self.request.user.customer)