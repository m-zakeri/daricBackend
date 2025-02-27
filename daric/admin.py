from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Transaction

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "firstName", "lastName", "phoneNumber", "walletBalance", "job", "qr_code_id", "created_at"]
    list_per_page = 10
    list_editable = ["job"]
    search_fields = ["firstName", "lastName", "phoneNumber", "created_at"]
    readonly_fields = ["created_at"]  # Make created_at read-only in the admin panel

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "amount", "sender_link", "receiver_link"]
    list_per_page = 10
    list_filter = ["date"]
    search_fields = ["sender__firstName", "receiver__firstName", "amount"]

    def sender_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:daric_user_change', args=[obj.sender.id]), obj.sender)

    def receiver_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:daric_user_change', args=[obj.receiver.id]), obj.receiver)

    sender_link.short_description = 'Sender'
    receiver_link.short_description = 'Receiver'