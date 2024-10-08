# urls.py

from django.urls import path
from .views import (
    AddItemToOrder,
    FinalizeOrderView,
    EarningAPIView, GetOrderItemsView,
)

urlpatterns = [
    path('items/', GetOrderItemsView.as_view(), name='get_order_items'),
    path('finalize/', FinalizeOrderView.as_view()),
    path('add-item/', AddItemToOrder.as_view()),
    path('remove-item/', AddItemToOrder.as_view()),
    path('earnings/', EarningAPIView.as_view()),
]

