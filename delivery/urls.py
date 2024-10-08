from django.urls import path, include

from delivery.serializers import DeliverySerializer

urlpatterns = [
    path('delivery/', DeliverySerializer)

]