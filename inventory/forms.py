from django import forms
from django.core.validators import MinValueValidator
#from .models import Product, ProductCategory
from django.core.exceptions import ValidationError
from .models import Item, ItemImage, ItemCategory, ItemTemplate
from django.forms.widgets import ClearableFileInput


        
"""class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=ItemCategory.objects.all(), 
        required=False
    )
    low_stock_threshold = forms.IntegerField(
        initial=10,
        validators=[MinValueValidator(0)],
        help_text="Set the threshold for low stock alerts"
    )

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'stock_quantity', 
            'category', 'condition', 'low_stock_threshold'"""

'''
class StockAdjustmentForm(forms.Form):
    adjustment_quantity = forms.IntegerField(
        help_text="Enter positive or negative value to adjust stock"
    )
    reason = forms.CharField(
        widget=forms.Textarea, 
        required=False, 
        help_text="Optional: Reason for stock adjustment"
    )

class ProductSearchForm(forms.Form):
    name = forms.CharField(required=False, label="Product Name")
    min_price = forms.DecimalField(required=False, label="Minimum Price")
    max_price = forms.DecimalField(required=False, label="Maximum Price")
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(), 
        required=False
    )
    in_stock = forms.BooleanField(required=False, label="Only Show In-Stock Products")'''






class MultipleFileInput(forms.ClearableFileInput):
    """
    Custom multiple file input widget
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['multiple'] = 'multiple'

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name, None)

class ItemForm(forms.ModelForm):
    
    # Multiple file input for images
    images = forms.FileField(
        #widget=forms.MultipleFileInput(attrs={"multiple": True, "accept": "image/*"}),
        widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        #widget=forms.ClearableFileInput(attrs={"multiple": True}),
        #widget=forms.ClearableFileInput(attrs={"multiple": True, "accept": "image/*"}),
        
        required=False,
        help_text="Upload up to 5 images"
    )

    # Optional template selection
    use_template = forms.ModelChoiceField(
        queryset=None,
        required=False,
        help_text="Select a saved template to pre-fill details"
    )

    class Meta:
        model = Item
        fields = [
            'name', 'category', 'description', 
            'price', 'is_price_negotiable', 
            'stock_quantity', 'condition', 
            'delivery_option', 
            #'location'
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'placeholder': 'Add unique features or usage details...',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'step': '1',
                'min': '1'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Dynamically set template queryset for the current user
        if user:
            self.fields['use_template'].queryset = ItemTemplate.objects.filter(user=user)

    def clean_images(self):
        images = self.files.getlist('images')
        
        # Validate number of images
        if len(images) > 5:
            raise ValidationError("You can upload a maximum of 5 images")
        
        # Validate image file types and sizes
        for image in images:
            # Example: limit to 5MB
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(f"{image.name} is too large. Max size is 5MB")
        
        return images

class ItemTemplateForm(forms.ModelForm):
    class Meta:
        model = ItemTemplate
        fields = ['name', 'category', 'description', 'price', 'condition']

class ItemSearchForm(forms.Form):
    query = forms.CharField(required=False, label="Search Items")
    category = forms.ModelChoiceField(
        queryset=ItemCategory.objects.all(), 
        required=False
    )
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    condition = forms.ChoiceField(
        choices=[('', 'Any Condition')] + Item.CONDITION_CHOICES, 
        required=False
    )

class StockAdjustmentForm(forms.Form):
    adjustment_quantity = forms.IntegerField(
        help_text="Enter positive or negative value to adjust stock"
    )
    reason = forms.CharField(
        widget=forms.Textarea, 
        required=False, 
        help_text="Optional: Reason for stock adjustment"
    )