from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction, User
from .serializers import TransactionSerializer, UserSerializer

@api_view(['GET'])
def get_user(request, phoneNumber):
    try:
        # Fetch the user by phone number
        user = User.objects.get(phoneNumber=phoneNumber)
        # Serialize the user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": "User not found, please check the phone number or create an acount"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def register_user(request):
    # Deserialize the input data
    serializer = UserSerializer(data=request.data)
    
    # Validate the data
    if serializer.is_valid():
        # Save the new user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # Return errors if validation fails
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def transaction_history(request, user_id):
    # Fetch transactions where the user is either the sender or the receiver
    transactions = Transaction.objects.filter(Q(sender_id=user_id) | Q(receiver_id=user_id)).order_by('-date')
    # Serialize the transactions
    serializer = TransactionSerializer(transactions, many=True, context={'request': request})
    return Response(serializer.data)