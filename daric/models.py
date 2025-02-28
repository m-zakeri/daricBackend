from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.urls import reverse
import uuid

class User(models.Model):
    JOB_HEALTH_CARE = "HC"
    JOB_TAXI_DRIVER = "TD"
    JOB_COMMON_USER = "CU"

    JOBS_CHOICES = [
        (JOB_HEALTH_CARE, "Health Care"),
        (JOB_TAXI_DRIVER, "Taxi Driver"),
        (JOB_COMMON_USER, "Common User"),
    ]

    firstName = models.CharField(max_length=255, verbose_name="First Name", help_text="Enter the user's first name.")
    lastName = models.CharField(max_length=255, verbose_name="Last Name", help_text="Enter the user's last name.")
    phoneNumber = models.CharField(max_length=11, unique=True, verbose_name="Phone Number", help_text="Enter the user's phone number.")
    walletBalance = models.DecimalField(max_digits=11, decimal_places=2, default=0, verbose_name="Wallet Balance", help_text="The current balance in the user's wallet.")
    socialSecureNumber = models.CharField(max_length=20, unique=True, verbose_name="Social Secure Number", help_text="Enter the user's social security number.")
    job = models.CharField(max_length=2, choices=JOBS_CHOICES, default=JOB_COMMON_USER, verbose_name="Job", help_text="Select the user's job type.")
    qr_code_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="QR Code ID", help_text="Unique ID for generating QR codes.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At", help_text="The date and time when the user was created.")

    def __str__(self):
        return f"{self.firstName} {self.lastName}"

    def clean(self):
        if self.walletBalance < 0:
            raise ValidationError("Wallet balance cannot be negative.")

    class Meta:
        ordering = ['lastName', 'firstName']
        verbose_name_plural = "Users"

    def get_absolute_url(self):
        return reverse('user-detail', args=[str(self.id)])
        
class Transaction(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Transaction Date", help_text="The date of the transaction.")
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Amount",
        help_text="The amount of the transaction.",
        validators=[MinValueValidator(0.01)]  # Ensures amount is greater than 0
    )
    sender = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sent_transactions', verbose_name="Sender", help_text="The user who sent the transaction.")
    receiver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='received_transactions', verbose_name="Receiver", help_text="The user who received the transaction.")

    def __str__(self):
        return f"Transaction {self.id} - {self.amount}"

    def clean(self):
        # Ensure amount is not None
        if self.amount is None:
            raise ValidationError({"amount": "The amount cannot be null."})

        # Ensure amount is greater than 0
        if self.amount <= 0:
            raise ValidationError({"amount": "The amount must be greater than 0."})

        # Ensure sender is not None and exists in the User table
        if self.sender is None:
            raise ValidationError({"sender": "The sender cannot be null."})
        if not User.objects.filter(id=self.sender.id).exists():
            raise ValidationError({"sender": "The sender does not exist in the User table."})

        # Ensure receiver is not None and exists in the User table
        if self.receiver is None:
            raise ValidationError({"receiver": "The receiver cannot be null."})
        if not User.objects.filter(id=self.receiver.id).exists():
            raise ValidationError({"receiver": "The receiver does not exist in the User table."})

        # Ensure the sender has enough balance to send the amount
        if self.sender.walletBalance < self.amount:
            raise ValidationError({"amount": "The sender does not have enough balance to complete this transaction."})

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Transactions"

    def get_absolute_url(self):
        return reverse('transaction-detail', args=[str(self.id)])