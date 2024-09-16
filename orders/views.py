import calendar
from datetime import date
from datetime import timedelta, date
from django.db.models import Sum
from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from rest_framework.response import Response

from customers.models import Customer
from .models import Order, OrderMenuItem, OrderMenuItemExtraIngredient
from .serializers import OrderSerializer, OrderMenuItemSerializer, OrderMenuItemExtraIngredientSerializer
from django_filters.rest_framework import DjangoFilterBackend


class OrderView(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

class EarningView(viewsets.ViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['age', 'gender', 'postal_code']
    def list(self, request):
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        orders = Order.objects.filter(order_date__range=[first_day, last_day])
        age = request.query_params.get('age')
        gender = request.query_params.get('gender')
        postal_code = request.query_params.get('postal_code')

        if age:
            birthdate_threshold = date.today() - timedelta(days=int(age)*365)
            orders = orders.filter(customer__birthdate__lte=birthdate_threshold)
        if gender:
            orders = orders.filter(customer__gender=gender)
        if postal_code:
            orders = orders.filter(customer__address__postal_code=postal_code)

        total_earnings = orders.aggregate(Sum('total_price'))['total_price__sum']
        return Response({'Earnings': total_earnings, 'Filters': { 'age': age, 'gender': gender, 'postal_code': postal_code}})



