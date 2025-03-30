# for running the unit test run the following command:
# python manage.py test daric.tests.test_models

from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import User, Transaction
import uuid

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            firstName="John",
            lastName="Doe",
            phoneNumber="1234567890",
            socialSecureNumber="123-45-6789",
            walletBalance=Decimal('100.00')
        )

    def test_user_creation(self):
        self.assertEqual(self.user.firstName, "John")
        self.assertEqual(self.user.lastName, "Doe")
        self.assertEqual(self.user.phoneNumber, "1234567890")
        self.assertEqual(self.user.socialSecureNumber, "123-45-6789")
        self.assertEqual(self.user.walletBalance, Decimal('100.00'))

    def test_user_clean_method(self):
        self.user.walletBalance = Decimal('-10.00')
        with self.assertRaises(ValidationError):
            self.user.clean()

    def test_user_str_method(self):
        self.assertEqual(str(self.user), "John Doe")

class TransactionModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create(
            firstName="Alice",
            lastName="Smith",
            phoneNumber="0987654321",
            socialSecureNumber="987-65-4321",
            walletBalance=Decimal('200.00')
        )
        self.receiver = User.objects.create(
            firstName="Bob",
            lastName="Johnson",
            phoneNumber="1122334455",
            socialSecureNumber="112-23-4455",
            walletBalance=Decimal('50.00')
        )
        self.transaction = Transaction.objects.create(
            amount=Decimal('50.00'),
            sender=self.sender,
            receiver=self.receiver
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.amount, Decimal('50.00'))
        self.assertEqual(self.transaction.sender, self.sender)
        self.assertEqual(self.transaction.receiver, self.receiver)

    def test_transaction_clean_method(self):
        self.transaction.amount = Decimal('0.00')
        with self.assertRaises(ValidationError):
            self.transaction.clean()

    def test_transaction_save_method(self):
        self.assertEqual(self.sender.walletBalance, Decimal('150.00'))
        self.assertEqual(self.receiver.walletBalance, Decimal('100.00'))

