from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from django.conf import settings

from .models import Payment, PaymentMethod, Order
from payment import models

class PaymentForm(forms.ModelForm):

    PAYMENT_METHOD_CHOICES = [
        ('', 'All Methods'),
        ('mpesa', 'M-Pesa'),
        ('stripe', 'Stripe'),
        ('manual', 'Manual')
    ]
    '''    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select,
        required=True
    )'''

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        required=False
    )

    # M-Pesa specific field
    phone_number = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^(\+?254|0)?[7-9]\d{8}$', 
                message="Enter a valid Kenyan phone number"
            )
        ],
        required=False,
        help_text="Enter your M-Pesa registered phone number"
    )

    # Stripe specific fields
    card_number = forms.CharField(
        max_length=19,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Card Number'}),
        validators=[
            RegexValidator(
                regex=r'^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$', 
                message="Enter a valid card number"
            )
        ]
    )

    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY'}),
        validators=[
            RegexValidator(
                regex=r'^(0[1-9]|1[0-2])/\d{2}$', 
                message="Enter expiry date in MM/YY format"
            )
        ]
    )

    cvv = forms.CharField(
        max_length=4,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CVV'}),
        validators=[
            RegexValidator(
                regex=r'^\d{3,4}$', 
                message="Enter a valid CVV"
            )
        ]
    )

    class Meta:
        model = Payment
        fields = ['order', 'amount']
        widgets = {
            'order': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter orders for the current user
        if user:
            self.fields['order'].queryset = Order.objects.filter(user=user, payments__isnull=True)

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        # Validate M-Pesa payment
        if payment_method == 'mpesa':
            phone_number = cleaned_data.get('phone_number')
            if not phone_number:
                raise forms.ValidationError("Phone number is required for M-Pesa payment")
        
        # Validate Stripe payment
        elif payment_method == 'stripe':
            card_number = cleaned_data.get('card_number')
            expiry_date = cleaned_data.get('expiry_date')
            cvv = cleaned_data.get('cvv')
            
            if not all([card_number, expiry_date, cvv]):
                raise forms.ValidationError("All card details are required for Stripe payment")
        
        return cleaned_data

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        order = self.cleaned_data.get('order')
        
        # Validate amount against order total
        if order:
            remaining_amount = order.total_amount - sum(payment.amount for payment in order.payments.all())
            if amount > remaining_amount:
                raise forms.ValidationError(f"Payment amount cannot exceed {remaining_amount}")
        
        return amount

class RefundForm(forms.Form):
    REFUND_REASONS = [
        ('duplicate', 'Duplicate Charge'),
        ('fraudulent', 'Fraudulent Charge'),
        ('requested_by_customer', 'Requested by Customer'),
        ('other', 'Other')
    ]

    payment = forms.ModelChoiceField(
        queryset=Payment.objects.filter(status='completed'),
        required=True,
        help_text="Select the payment to refund"
    )

    reason = forms.ChoiceField(
        choices=REFUND_REASONS,
        required=True,
        widget=forms.Select
    )

    custom_reason = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea,
        help_text="Provide additional details if 'Other' is selected"
    )

    refund_amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Enter the amount to refund"
    )

    def clean(self):
        cleaned_data = super().clean()
        payment = cleaned_data.get('payment')
        refund_amount = cleaned_data.get('refund_amount')
        reason = cleaned_data.get('reason')

        # Validate refund amount
        if payment and refund_amount:
            if refund_amount > payment.amount:
                raise forms.ValidationError("Refund amount cannot exceed the original payment amount")

        # Require custom reason for 'Other'
        if reason == 'other':
            custom_reason = cleaned_data.get('custom_reason')
            if not custom_reason:
                raise forms.ValidationError("Please provide a reason when selecting 'Other'")

        return cleaned_data

class PaymentSearchForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    min_amount = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2
    )
    max_amount = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2
    )
    '''    payment_method = forms.ChoiceField(
        choices=[('', 'All Methods')] + Payment.PAYMENT_METHOD_CHOICES,
        required=False
    )'''

    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Payment.PAYMENT_STATUS_CHOICES,
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')

        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be before end date")

        # Validate amount range
        if min_amount and max_amount and min_amount > max_amount:
            raise forms.ValidationError("Minimum amount must be less than maximum amount")

        return cleaned_data