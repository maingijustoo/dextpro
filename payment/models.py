from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from orders.models import Order

class PaymentMethod(models.Model):
    PAYMENT_GATEWAY_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('stripe', 'Stripe'),
        ('manual', 'Manual')
    ]

    name = models.CharField(max_length=50, choices=PAYMENT_GATEWAY_CHOICES)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_name_display()

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    PAYMENT_TYPE_CHOICES = [
        ('order', 'Order Payment'),
        ('refund', 'Refund'),
        ('adjustment', 'Payment Adjustment')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='order')
    
    # Payment gateway specific fields
    mpesa_transaction_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.payment_method.name} Payment for Order #{self.order.id} - {self.status}"

class MpesaPaymentRequest(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    checkout_request_id = models.CharField(max_length=255, unique=True)
    response_description = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mpesa Payment Request for {self.payment}"

class StripeCustomer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return f"Stripe Customer for {self.user.username}"