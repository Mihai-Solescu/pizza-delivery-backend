# views.py

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from datetime import date, timedelta
import calendar

from rest_framework.views import APIView

from .models import (
    Order,
    OrderMenuItem,
    OrderMenuItemExtraIngredient,
)
from .serializers import (
    OrderSerializer,
    OrderMenuItemSerializer,
    OrderMenuItemExtraIngredientSerializer,
)


class ApplyDiscount(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            order = Order.objects.get(customer=user.customer, status='open')
        except Order.DoesNotExist:
            return Response({'error': 'Active order not found.'}, status=status.HTTP_404_NOT_FOUND)

        discount_code = request.data.get('discount_code')
        success = order.apply_discount(discount_code)

        if success:
            return Response({'message': 'Discount applied'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid discount code'}, status=status.HTTP_400_BAD_REQUEST)

class RemoveOrderItem(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        user = request.user
        try:
            order = Order.objects.get(customer=user.customer, status='open')
            order_item = order.items.get(id=item_id)
            order_item.delete()
            return Response({'message': 'Item removed from order'}, status=status.HTTP_200_OK)
        except (Order.DoesNotExist, OrderMenuItem.DoesNotExist):
            return Response({'error': 'Order item not found.'}, status=status.HTTP_404_NOT_FOUND)

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user.customer)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user.customer)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user.customer)

    def perform_update(self, serializer):
        order = self.get_object()
        if order.customer != self.request.user.customer:
            raise PermissionDenied("You do not have permission to modify this order.")
        serializer.save()

class ApplyDiscountToOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            if order.customer != request.user.customer:
                raise PermissionDenied("Permission denied.")
        except Order.DoesNotExist:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        discount_code = request.data.get('discount_code')
        if discount_code:
            success = order.apply_discount(discount_code)
            if success:
                order.save()
                return Response({'message': 'Discount applied.', 'total_price': str(order.total_price)}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid discount code.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Discount code not provided.'}, status=status.HTTP_400_BAD_REQUEST)

class FinalizeOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            if order.customer != request.user.customer:
                raise PermissionDenied("Permission denied.")
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

class EarningAPIView(APIView):
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['age', 'gender', 'postal_code']

    def get(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        orders = Order.objects.filter(order_date__range=[first_day, last_day])

        age = request.query_params.get('age')
        gender = request.query_params.get('gender')
        postal_code = request.query_params.get('postal_code')

        if age:
            birthdate_threshold = date.today() - timedelta(days=int(age) * 365)
            orders = orders.filter(customer__birthdate__lte=birthdate_threshold)
        if gender:
            orders = orders.filter(customer__gender=gender)
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

class OrderMenuItemListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderMenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderMenuItem.objects.filter(order__customer=self.request.user.customer)

class OrderMenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderMenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderMenuItem.objects.filter(order__customer=self.request.user.customer)

class OrderMenuItemExtraIngredientListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderMenuItemExtraIngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderMenuItemExtraIngredient.objects.filter(
            order_menu_item__order__customer=self.request.user.customer
        )

class OrderMenuItemExtraIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderMenuItemExtraIngredientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderMenuItemExtraIngredient.objects.filter(
            order_menu_item__order__customer=self.request.user.customer
        )