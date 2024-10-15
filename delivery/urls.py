from django.urls import path
from .views import (
    DeliveryPersonListView,
    DeliveryPersonDetailView,
    AvailableDeliveryPersonsView,
    SetDeliveryPersonAvailableView,
    DeliveryListView,
    DeliveryDetailView,
    GroupedDeliveriesView,
    CompleteDeliveryView, AssignDelivery, DeliveryListForDeliveryPerson, DeliveryUpdateStatus
)


urlpatterns = [
    # Courier Endpoints
    path('delivery-persons/', DeliveryPersonListView.as_view(), name='deliveryperson-list'),
    path('delivery-persons/<int:pk>/', DeliveryPersonDetailView.as_view(), name='deliveryperson-detail'),
    path('delivery-persons/available/', AvailableDeliveryPersonsView.as_view(), name='deliveryperson-available'),
    path('delivery-persons/<int:pk>/set_available/', SetDeliveryPersonAvailableView.as_view(), name='deliveryperson-set-available'),

    # Delivery Endpoints
    path('deliveries/', DeliveryListView.as_view(), name='delivery-list'),
    path('deliveries/<int:pk>/', DeliveryDetailView.as_view(), name='delivery-detail'),
    path('deliveries/grouped_deliveries/', GroupedDeliveriesView.as_view(), name='delivery-grouped-deliveries'),
    path('deliveries/<int:pk>/complete_delivery/', CompleteDeliveryView.as_view(), name='delivery-complete-delivery'),

    path('assign_delivery/', AssignDelivery.as_view(), name='assign_delivery'),
    path('my_deliveries/', DeliveryListForDeliveryPerson.as_view(), name='my_deliveries'),
    path('update_delivery/<int:delivery_id>/', DeliveryUpdateStatus.as_view(), name='update_delivery'),
]