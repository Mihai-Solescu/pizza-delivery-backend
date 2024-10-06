# urls.py

from django.urls import path
from .views import (
    AddItemToOrder,
    ModifyOrderItem,
    ApplyDiscount,
    RemoveOrderItem,
    OrderListCreateView,
    OrderDetailView,
    ApplyDiscountToOrderView,
    FinalizeOrderView,
    EarningAPIView,
    OrderMenuItemListCreateView,
    OrderMenuItemDetailView,
    OrderMenuItemExtraIngredientListCreateView,
    OrderMenuItemExtraIngredientDetailView,
)

urlpatterns = [
    # order endpoints
    path('orders/', OrderListCreateView.as_view()),
    path('orders/<int:pk>/', OrderDetailView.as_view()),
    path('orders/<int:pk>/apply_discount/', ApplyDiscountToOrderView.as_view()),
    path('orders/<int:pk>/finalize/', FinalizeOrderView.as_view()),

    # Order menu items
    path('order-items/', OrderMenuItemListCreateView.as_view()),
    path('order-items/<int:pk>/', OrderMenuItemDetailView.as_view()),

    # Order menu items with extras
    path('order-item-extras/', OrderMenuItemExtraIngredientListCreateView.as_view()),
    path('order-item-extras/<int:pk>/', OrderMenuItemExtraIngredientDetailView.as_view()),

    #  custom endpoints
    path('add-item-to-order/', AddItemToOrder.as_view()),
    path('modify-order-item/<int:item_id>/', ModifyOrderItem.as_view()),
    path('apply-discount/', ApplyDiscount.as_view()),
    path('remove-order-item/<int:item_id>/', RemoveOrderItem.as_view()),
    path('earnings/', EarningAPIView.as_view()),
]

