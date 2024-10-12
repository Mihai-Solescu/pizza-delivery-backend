from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, DeliveryPerson
from .serializers import OrderSerializer
from django.utils import timezone
from datetime import timedelta

class OrderStatusView(APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            serializer = OrderSerializer(order)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

class CancelOrderView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
            if order.cancel_order_within_time():
                return Response({'message': 'Order cancelled successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Cancellation window has passed'}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

class PlaceOrderView(APIView):
    def post(self, request):
        # Assuming order data is sent in the request body
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            # Assign delivery and handle grouping
            order.create_or_update_delivery()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)