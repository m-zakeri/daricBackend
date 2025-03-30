from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('user/<str:phoneNumber>/', views.get_user, name='get-user'),  # done
    path('register/', views.register_user, name='register-user'),  # done
    path('user/qr/<uuid:qr_code_id>/', views.get_user_by_qr_code_id, name='get-user-by-qr-code'),  # done
    path('wallet/<int:user_id>/', views.get_wallet_balance, name='get-wallet-balance'),  # --------
    path('user/update/<int:user_id>/', views.update_user_name, name='update-user-name'),  # done
    path('wallet/increase/', views.increase_wallet_balance, name='increase-wallet-balance'),  # done
    path('transactions/create/', views.create_transaction, name='create-transaction'),  # done
    path('update_default_payment_value/', views.update_default_payment_amount, name='update-default-payment-amount'),  # -------
    path('generate_new_qr_code_id/', views.generate_new_qr_code_id, name='generate-new-qr-code-id'),  # --------
    path('transaction-history/<int:user_id>/', views.get_transaction_history, name='get-transaction-history'),  # done
]

