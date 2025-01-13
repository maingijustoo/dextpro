from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
        ('thrifted', 'thrifted'),
        ('ex-uk', 'ex-uk'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    def __str__(self):
        return self.name

class StockAdjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_adjustments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    adjustment_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} - Stock Adjustment"

# Signal to handle low stock notifications
@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    """
    Send email notification when product stock is low
    """
    if instance.is_low_stock():
        # In a real-world scenario, you'd want to limit the frequency of these emails
        send_mail(
            'Low Stock Alert',
            f'Product {instance.name} is running low on stock. Current quantity: {instance.stock_quantity}',
            'from@dext.com',
            ['admin@dext.com'],  # Replace with actual admin email
            fail_silently=False,
        )




class ItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like_New'),
        ('good', 'Good'),
        ('thrifted', 'thifted')
    ]

    DELIVERY_OPTIONS = [
        ('self_pickup', 'Self Pickup'),
        ('delivery', 'Delivery'),
        ('meet_up', 'Meet Up'),
        ('peddy', 'peddy')
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('rejected', 'Rejected')
    ]

    # Basic Details
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_price_negotiable = models.BooleanField(default=False)
    
    # Inventory Management
    stock_quantity = models.PositiveIntegerField(default=1)
    
    # Additional Details
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTIONS, default='peddy')
    
    # Location and Delivery
    location = models.CharField(max_length=200, blank=True, null=True)
    
    # Status and Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='item_images/',
        validators=[FileExtensionValidator(['png', 'jpg', 'jpeg', 'gif'])]
    )
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.item.name}"

class ItemTemplate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='item_templates')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=Item.CONDITION_CHOICES, default='new')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name