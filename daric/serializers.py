from rest_framework import serializers
from .models import Transaction, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'phoneNumber', 'socialSecureNumber', 'walletBalance', 'qr_code_id']

class TransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'transaction_type']

    def get_transaction_type(self, obj):
        user_id = self.context['request'].parser_context['kwargs'].get('user_id')
        if obj.sender_id == user_id:
            return "Sent"
        elif obj.receiver_id == user_id:
            return "Received"
        return "Unknown"