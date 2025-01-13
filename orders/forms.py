from django import forms
from django.utils import timezone
from .models import Order, DeliveryPreference
from inventory.models import Product

class OrderForm(forms.ModelForm):
    products = forms.JSONField(required=False)
    delivery_preference = forms.ModelChoiceField(
        queryset=DeliveryPreference.objects.all(),
        required=True
    )

    class Meta:
        model = Order
        fields = ['delivery_preference']

class OrderSearchForm(forms.Form): 
    status = forms.ChoiceField(choices=Order.STATUS_CHOICES, required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))