from django.urls import path
from . import views
from .views import payment_detail, initiate_payment, mpesa_callback, payment_history, request_refund

app_name='payments'
urlpatterns = [
    #path('', views.index, name='index'),
    path('<int:order_id>/', payment_detail, name='payment_detail'),
    path('payments/', payment_history, name='payment_history'),
    path('payments/', request_refund, name='request_refund'),
    path('payments/initiate/', initiate_payment, name='initiate_payment'),
    path('payments/mpesa/callback/', mpesa_callback, name='mpesa_callback'),
]

