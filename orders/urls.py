# urls.py

from django.urls import path
from .views import (
    AddItemToOrder,
    FinalizeOrderView,
    EarningAPIView,
)

urlpatterns = [
    path('orders/<int:pk>/finalize/', FinalizeOrderView.as_view()),
    path('add-item-to-order/', AddItemToOrder.as_view()),
    path('earnings/', EarningAPIView.as_view()),
]

