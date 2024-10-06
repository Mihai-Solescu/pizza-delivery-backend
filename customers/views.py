from rest_framework import permissions
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from customers.serializers import CustomerRegisterSerializer, CustomerPreferencesSerializer, CustomerDataSerializer
from customers.models import CustomerPreferences, CustomerData


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')

        print (request.data)
        print (username)
        print (password)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

class CustomerRegisterView(APIView):
    def post(self, request):
        print (request.data)
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDataView(APIView):
    def post(self, request):
        try:
            # Get the existing data for the authenticated user
            customer_data = CustomerData.objects.get(customer=request.user)
        except CustomerData.DoesNotExist:
            # If no data exists for this user, create a new record
            customer_data = CustomerData(customer=request.user)

        # Handle pizza order updates
        pizzas_ordered = request.data.get('pizzas_ordered', [])
        for pizza in pizzas_ordered:
            if pizza in customer_data.times_pizza_ordered:
                customer_data.times_pizza_ordered[pizza] += 1
            else:
                customer_data.times_pizza_ordered[pizza] = 1

        # Handle pizza rating updates
        pizzas_ratings = request.data.get('pizzas_ratings', {})
        for pizza, new_rating in pizzas_ratings.items():
            # If the pizza already has a rating, update the average rating
            if pizza in customer_data.avg_pizza_rating:
                current_avg_rating = customer_data.avg_pizza_rating[pizza]
                total_ratings = customer_data.times_pizza_ordered.get(pizza,
                                                                      1)  # Ensure there's at least one order for this pizza
                updated_avg_rating = (current_avg_rating * (total_ratings - 1) + new_rating) / total_ratings
                customer_data.avg_pizza_rating[pizza] = updated_avg_rating
            else:
                # First rating for the pizza
                customer_data.avg_pizza_rating[pizza] = new_rating

        # Save the updated data
        customer_data.save()

        # Serialize the data and return the response
        serializer = CustomerDataSerializer(customer_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Update or create customer data for the authenticated user
        try:
            customer_data = CustomerData.objects.get(customer=request.user)
            serializer = CustomerDataSerializer(customer_data, data=request.data)
        except CustomerData.DoesNotExist:
            serializer = CustomerDataSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerPreferencesView(APIView):
    def get(self, request):
        # Get preferences of the authenticated user
        try:
            preferences = CustomerPreferences.objects.get(customer=request.user)
            serializer = CustomerPreferencesSerializer(preferences)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerPreferences.DoesNotExist:
            return Response(
                {"detail": "Preferences not found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        # Create or update preferences for the authenticated user
        try:
            # Check if preferences already exist for this user
            preferences = CustomerPreferences.objects.get(customer=request.user)
            serializer = CustomerPreferencesSerializer(preferences, data=request.data)
        except CustomerPreferences.DoesNotExist:
            # If not, create new preferences
            serializer = CustomerPreferencesSerializer(data=request.data)

        if serializer.is_valid():
            # Save the preferences with the current user as the owner
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
