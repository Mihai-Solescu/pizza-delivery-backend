# urls.py

from django.urls import path
from .views import (
    AddItemToOrder,
    FinalizeOrderView,
    EarningAPIView, GetOrderItemsView,
)

urlpatterns = [
    path('order/items/', GetOrderItemsView.as_view(), name='get_order_items'),
    path('orders/<int:pk>/finalize/', FinalizeOrderView.as_view()),
    path('add-item/', AddItemToOrder.as_view()),
    path('earnings/', EarningAPIView.as_view()),
]

