from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('user/<str:phoneNumber>/', views.get_user), 
    path('register/', views.register_user),
    path('user/qr/<uuid:qr_code_id>/', views.get_user_by_qr_code_id),
    path('wallet/<int:user_id>/', views.get_wallet_balance),
    path('user/update/<int:user_id>/', views.update_user_name),
    path('wallet/increase/', views.increase_wallet_balance),
    path('transactions/create/', views.create_transaction),
]