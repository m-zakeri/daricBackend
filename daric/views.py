from django.db.models import Q
from django.db import transaction as db_transaction
from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction, User
from .serializers import TransactionSerializer, UserSerializer, ReceiverUserSerializer
from datetime import datetime
import uuid

@api_view(['GET'])
def get_user(request, phoneNumber):
    try:
        # Fetch the user by phone number
        user = User.objects.get(phoneNumber=phoneNumber)
        # Serialize the user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        # return Response({"error": "User not found, please check the phone number or create an acount"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "کاربر پیدا نشد. لطفا از درستی شماره تلفن مطمئن شوید یا اگر اکانت ندارید اکانت بسازید"}, status=status.HTTP_404_NOT_FOUND)

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

@api_view(['GET'])  # Ensure the view is decorated with @api_view
def get_user_by_qr_code_id(request, qr_code_id):
    try:
        # Fetch the user by qr_code_id
        user = User.objects.get(qr_code_id=qr_code_id)
        # Serialize the user with only firstName and lastName
        serializer = ReceiverUserSerializer(user)
        return Response(serializer.data)  # Return a properly formatted Response
    except User.DoesNotExist:
        # return Response({"error": "User not found, please check the QR code ID."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "کاربر پیدا نشد. لطفا از درستی رمزینه اسکن شده مطمئن شوید."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_wallet_balance(request, user_id):
    try:
        # Fetch the user by ID
        user = User.objects.get(id=user_id)
        # Return the wallet balance
        return Response({"walletBalance": user.walletBalance}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # return Response({"error": "User not found, please check the user ID."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "کاربر پیدا نشد."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_user_name(request, user_id):
    try:
        # Fetch the user by ID
        user = User.objects.get(id=user_id)
        
        # Get the new first name and last name from the request data
        new_first_name = request.data.get('firstName')
        new_last_name = request.data.get('lastName')
        
        # Validate the data
        if not new_first_name or not new_last_name:
            return Response({"error": "نام و نام‌خانوادگی لازم است."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the user's first name and last name
        user.firstName = new_first_name
        user.lastName = new_last_name
        user.save()
        
        # Return the updated user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({"error": "User not found, please check the user ID."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def increase_wallet_balance(request):
    # Extract data from the request
    user_id = request.data.get('user_id')
    amount = request.data.get('amount')

    # Validate required fields
    if not user_id or not amount:
        return Response(
            {"error": "user_id and amount are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Convert amount to Decimal
        amount = Decimal(str(amount))  # Convert to string first to avoid floating-point precision issues

        # Fetch the user
        user = User.objects.get(id=user_id)

        # Validate the amount
        if amount <= Decimal('0.00'):
            # raise ValidationError({"amount": "The amount must be greater than 0."})
            raise ValidationError({"amount": "مقدار درخواستی برای انتقال باید بیشتر از ۰ باشد."})

        # Increase the wallet balance
        user.walletBalance += amount
        user.save()

        # Return the updated wallet balance
        return Response(
            {"walletBalance": str(user.walletBalance)},  # Convert Decimal to string for JSON serialization
            status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def create_transaction(request):
    # Extract data from the request
    sender_id = request.data.get('sender_id')
    receiver_id = request.data.get('receiver_id')
    amount = request.data.get('amount')

    # Validate required fields
    if not sender_id or not receiver_id or not amount:
        return Response(
            {"error": "sender_id, receiver_id, and amount are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Convert amount to Decimal
        amount = Decimal(str(amount))  # Convert to string first to avoid floating-point precision issues

        # Use a database transaction to ensure atomicity
        with db_transaction.atomic():
            # Fetch sender and receiver
            sender = User.objects.select_for_update().get(id=sender_id)  # Lock the sender's row
            receiver = User.objects.select_for_update().get(id=receiver_id)  # Lock the receiver's row

            # Create and save the transaction record
            transaction_record = Transaction(
                sender=sender,
                receiver=receiver,
                amount=amount
            )
            transaction_record.save()  # This will update wallet balances via the Transaction model's save method

        # Serialize the transaction for the response
        serializer = TransactionSerializer(transaction_record, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        # return Response(
        #     {"error": "Sender or receiver not found."},
        #     status=status.HTTP_404_NOT_FOUND
        # ) 
        return Response(
            {"error": "فرستنده یا گیرنده پیدا نشد."},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
def update_default_payment_amount(request):
    # Extract user_id and default_payment_amount from the request
    user_id = request.data.get('user_id')
    default_payment_amount = request.data.get('default_payment_amount')

    # Validate required fields
    if user_id is None or default_payment_amount is None:
        return Response(
            {"error": "user_id and default_payment_amount are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Convert default_payment_amount to Decimal
        default_payment_amount = Decimal(str(default_payment_amount))  # Convert to string first to avoid floating-point precision issues

        # Fetch the user
        user = User.objects.get(id=user_id)

        # Validate the default_payment_amount
        if default_payment_amount < 0:
            # raise ValidationError({"default_payment_amount": "The default payment amount cannot be negative."})
            raise ValidationError({"default_payment_amount": "مقدار درخواستی برای انتقال نباید منفی باشد."})

        # Update the default_payment_amount
        user.default_payment_amount = default_payment_amount
        user.save()

        # Serialize the updated user for the response
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
def generate_new_qr_code_id(request):
    # Extract user_id from the request
    user_id = request.data.get('user_id')

    # Validate required fields
    if user_id is None:
        return Response(
            {"error": "user_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Fetch the user
        user = User.objects.get(id=user_id)

        # Generate a new unique qr_code_id
        user.qr_code_id = uuid.uuid4()
        user.save()

        # Serialize the updated user for the response
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_transaction_history(request, user_id):
    # Extract start_date and end_date from query parameters
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')

    # Validate the presence of start_date and end_date
    if not start_date_str or not end_date_str:
        return Response(
            {"error": "Both start_date and end_date are required as query parameters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Convert the date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {"error": "Invalid date format. Please use YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Fetch transactions where the user is either the sender or receiver and the date is within the range
    transactions = Transaction.objects.filter(
        Q(sender_id=user_id) | Q(receiver_id=user_id),
        date__range=[start_date, end_date]
    ).order_by('-date')

    # If no transactions exist, return an empty array
    if not transactions.exists():
        return Response([], status=status.HTTP_200_OK)

    # Serialize the transactions with the request context
    serializer = TransactionSerializer(transactions, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)