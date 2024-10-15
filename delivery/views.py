from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import models

from orders.models import Order
from .models import DeliveryPerson, Delivery
from .serializers import DeliveryPersonSerializer, DeliverySerializer
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Q

class DeliveryPersonListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        delivery_persons = DeliveryPerson.objects.all()
        serializer = DeliveryPersonSerializer(delivery_persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DeliveryPersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryPersonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(DeliveryPerson, pk=pk)

    def get(self, request, pk):
        delivery_person = self.get_object(pk)
        serializer = DeliveryPersonSerializer(delivery_person)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        delivery_person = self.get_object(pk)
        serializer = DeliveryPersonSerializer(delivery_person, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        delivery_person = self.get_object(pk)
        serializer = DeliveryPersonSerializer(delivery_person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        delivery_person = self.get_object(pk)
        delivery_person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailableDeliveryPersonsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        postal_code = request.query_params.get('postal_code', None)
        if postal_code:
            available_persons = DeliveryPerson.objects.filter(
                postal_area=postal_code
            ).filter(
                Q(last_dispatched__isnull=True) |
                Q(last_dispatched__lte=timezone.now() - timedelta(minutes=30))
            )
        else:
            available_persons = DeliveryPerson.objects.filter(
                Q(last_dispatched__isnull=True) |
                Q(last_dispatched__lte=timezone.now() - timedelta(minutes=30))
            )
        serializer = DeliveryPersonSerializer(available_persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AssignDelivery(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        print(order_id)

        if not order_id:
            return Response({'error': 'Order ID not provided.'}, status=400)

        order = Order.objects.filter(customer=request.user.customer_profile).order_by('-order_date').first()


        # Access delivery information directly from the order
        postal_code = order.delivery.delivery_postal_code
        address = order.delivery.delivery_address
        pizza_quantity = order.delivery.pizza_quantity

        available_delivery_persons = DeliveryPerson.objects.filter(
            postal_area=postal_code
        ).filter(
            models.Q(last_dispatched__isnull=True) |
            models.Q(last_dispatched__lte=timezone.now() - timedelta(minutes=30))
        )

        if not available_delivery_persons.exists():
            return Response({'error': 'No courier available.'}, status=400)

        now = timezone.now()

        existing_delivery = Delivery.objects.filter(
            delivery_postal_code=postal_code,
            delivery_status='pending',
            created_at__gte=now - timedelta(minutes=3),
            pizza_quantity__lt=3
        ).first()

        if existing_delivery:
            existing_delivery.orders.add(order)
            existing_delivery.pizza_quantity += pizza_quantity
            existing_delivery.save()
            delivery = existing_delivery
        else:
            delivery = Delivery.objects.create(
                delivery_postal_code=postal_code,
                delivery_address=address,
                pizza_quantity=pizza_quantity,
                delivery_status='pending',
            )
            delivery.orders.add(order)

            assigned = delivery.assign_delivery_person()
            if not assigned:
                delivery.delivery_status = 'no_courier'
                delivery.save()

        serializer = DeliverySerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SetDeliveryPersonAvailableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        delivery_person = get_object_or_404(DeliveryPerson, pk=pk)
        delivery_person.last_dispatched = None
        delivery_person.save()
        return Response({'status': 'Delivery person is available!'}, status=status.HTTP_200_OK)

class DeliveryListForDeliveryPerson(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            delivery_person = user.deliveryperson_profile
        except DeliveryPerson.DoesNotExist:
            return Response({'error': 'Not a delivery person.'}, status=403)

        deliveries = Delivery.objects.filter(
            delivery_person=delivery_person,
            delivery_status__in=['pending', 'in_process']
        )

        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data)


# Delivery Views

class DeliveryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deliveries = Delivery.objects.all()
        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Delivery, pk=pk)

    def get(self, request, pk):
        delivery = self.get_object(pk)
        serializer = DeliverySerializer(delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        delivery = self.get_object(pk)
        serializer = DeliverySerializer(delivery, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        delivery = self.get_object(pk)
        serializer = DeliverySerializer(delivery, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        delivery = self.get_object(pk)
        delivery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupedDeliveriesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        three_minutes_ago = now - timedelta(minutes=3)
        grouped_deliveries = Delivery.objects.filter(
            created_at__gte=three_minutes_ago,
            delivery_status='pending',
            pizza_quantity__lte=3
        )
        serializer = DeliverySerializer(grouped_deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompleteDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        delivery = get_object_or_404(Delivery, pk=pk)
        delivery.delivery_status = 'completed'
        delivery.save()
        if delivery.delivery_person:
            delivery.delivery_person.last_dispatched = timezone.now()
            delivery.delivery_person.save()

        return Response({'status': 'Delivery completed!'}, status=status.HTTP_200_OK)


class DeliveryUpdateStatus(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = request.user
        try:
            delivery_person = user.deliveryperson_profile
        except DeliveryPerson.DoesNotExist:
            return Response({'error': 'No courier!'}, status=403)

        try:
            delivery = Delivery.objects.get(delivery_id=id)
        except Delivery.DoesNotExist:
            return Response({'error': '404'}, status=404)

        if delivery.delivery_person != delivery_person:
            return Response({'error': 'Not authorized.'}, status=403)

        new_status = request.data.get('delivery_status')
        if new_status not in ['pending', 'in_process', 'completed', 'no_courier']:
            return Response({'error': 'Not valid!'}, status=400)

        delivery.delivery_status = new_status
        if new_status == 'in_process':
            delivery_person.last_dispatched = timezone.now()
            delivery_person.save()
        delivery.save()

        return Response({'message': 'Status updated!'})