from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "firstName", "lastName", "phoneNumber", "walletBalance", "job", "qr_code_id", "created_at"]
    list_per_page = 10
    list_editable = ["job"]
    search_fields = ["firstName", "lastName", "phoneNumber", "created_at"]
    readonly_fields = ["created_at"]  # Make created_at read-only in the admin panel


@admin.register(models.Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "amount", "sender", "receiver"]
    list_per_page = 10
    list_filter = ["date"]
    search_fields = ["sender__firstName", "receiver__firstName", "amount"]

