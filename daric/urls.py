from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('user/<str:phoneNumber>/', views.get_user), 
    path('register/', views.register_user),
    path('transactions/history/<int:user_id>/', views.transaction_history),
]