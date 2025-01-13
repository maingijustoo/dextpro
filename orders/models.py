from django.db import models
from django.conf import settings
from django.utils import timezone
from inventory.models import Product

class DeliveryPreference(models.Model):
    DELIVERY_CHOICES = [
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
        ('pickup', 'Store Pickup')
    ]

    name = models.CharField(max_length=50, choices=DELIVERY_CHOICES)
    additional_instructions = models.TextField(blank=True, null=True)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_preference = models.ForeignKey(DeliveryPreference, on_delete=models.SET_NULL, null=True)
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set estimated delivery date based on delivery preference
        if not self.estimated_delivery_date:
            if self.delivery_preference:
                if self.delivery_preference.name == 'express':
                    self.estimated_delivery_date = timezone.now() + timezone.timedelta(days=1)
                elif self.delivery_preference.name == 'standard':
                    self.estimated_delivery_date = timezone.now() + timezone.timedelta(days=3)
                else:
                    self.estimated_delivery_date = timezone.now() + timezone.timedelta(days=5)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class OrderStatusUpdate(models.Model):
    order = models.ForeignKey(Order, related_name='status_updates', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    update_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Status change for Order #{self.order.id}"