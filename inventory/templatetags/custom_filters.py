# inventory/templatetags/form_filters.py
from django import template
from django.forms.boundfield import BoundField

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Adds a CSS class to a form field
    """
    if isinstance(value, BoundField):
        # If it's a form field, modify the widget attrs
        existing_class = value.field.widget.attrs.get('class', '')
        new_classes = f"{existing_class} {arg}".strip()
        value.field.widget.attrs['class'] = new_classes
        return value
    return value