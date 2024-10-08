from datetime import timezone

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Delivery, DeliveryPerson
from .serializers import DeliverySerializer


#to be tested...
class DeliveryStatusView():
    def get(self, request):
        delivery_status = Delivery.objects.get(pk=request.query_params.get('delivery_id')).delivery_status
        return Response({'status': delivery_status}, status=status.HTTP_200_OK)

    def post(self, request):
        delivery = Delivery.objects.get(pk=request.data.get('delivery_id'))
        canceled = request.data.get('canceled')
        if canceled:
            delivery.delivery_status = 'Canceled'
            delivery.save()
            return Response({'status': delivery.delivery_status}, status=status.HTTP_200_OK)
        elif request.data.get('delivered'):
            delivery.delivery_status = 'Delivered'
            delivery.save()
            return Response({'status': delivery.delivery_status}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryPersonView(APIView):
