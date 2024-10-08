# urls.py

from django.urls import path
from .views import (
    AddItemToOrder,
    FinalizeOrderView,
    EarningAPIView, GetOrderItemsView, OrderStatusView, OrderCancelView,
)

urlpatterns = [
    path('items/', GetOrderItemsView.as_view()),
    path('finalize/', FinalizeOrderView.as_view()),
    path('add-item/', AddItemToOrder.as_view()),
    path('remove-item/', AddItemToOrder.as_view()),
    path('earnings/', EarningAPIView.as_view()),
    path('<int:order_id>/status/', OrderStatusView.as_view()),
    path('<int:order_id>/cancel/', OrderCancelView.as_view())
]

