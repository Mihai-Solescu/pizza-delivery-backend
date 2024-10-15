from django.urls import path
from .views import FinalizeOrderView, EarningAPIView, GetOrderItemsView, OrderCancelView, \
    AddItemToOrder, GetOrderItemCountView, OrderTotalPriceView, RemoveItemFromOrder, RedeemDiscountView, \
    LatestOrderStatusView, ConfirmedOrderPizzasAPIView

urlpatterns = [
    path('items/', GetOrderItemsView.as_view()),
    path('itemcount/', GetOrderItemCountView.as_view()),
    path('finalize/', FinalizeOrderView.as_view()),
    path('add-item/', AddItemToOrder.as_view()),
    path('remove-item/', RemoveItemFromOrder.as_view()),
    path('redeem-discount/', RedeemDiscountView.as_view()),
    path('totalprice/', OrderTotalPriceView.as_view()),
    path('earnings/', EarningAPIView.as_view()),
    path('latest/', LatestOrderStatusView.as_view()),
    path('<int:order_id>/cancel/', OrderCancelView.as_view()),
    path('confirmed_pizzas/', ConfirmedOrderPizzasAPIView.as_view(), name='confirmed_pizzas_api'),
]