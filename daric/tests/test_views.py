# for running the unit test run the following command:
# python manage.py test daric.tests.test_views

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from ..models import User, Transaction
import uuid

class GetUserByPhoneNumberTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            firstName="John",
            lastName="Doe",
            phoneNumber="1234567890",
            socialSecureNumber="123-45-6789",
            walletBalance=Decimal('100.00')
        )
        self.url = reverse('get-user', args=[self.user.phoneNumber])

    def test_get_user_by_phone_number(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phoneNumber'], self.user.phoneNumber)

    def test_get_user_by_phone_number_not_found(self):
        response = self.client.get(reverse('get-user', args=['0000000000']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RegisterUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register-user')
        self.valid_payload = {
            'firstName': 'Jane',
            'lastName': 'Doe',
            'phoneNumber': '1234567890',
            'socialSecureNumber': '123-45-6789',
            'walletBalance': '100.00'
        }

    def test_register_user(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_register_user_invalid_data(self):
        invalid_payload = {
            'firstName': '',
            'lastName': '',
            'phoneNumber': '',
            'socialSecureNumber': '',
            'walletBalance': ''
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateTransactionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.url = reverse('create-transaction')
        self.valid_payload = {
            'sender_id': self.sender.id,
            'receiver_id': self.receiver.id,
            'amount': '50.00'
        }

    def test_create_transaction(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_create_transaction_invalid_data(self):
        invalid_payload = {
            'sender_id': '',
            'receiver_id': '',
            'amount': ''
        }
        response = self.client.post(self.url, invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

