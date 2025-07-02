from django import forms
from django.forms import formset_factory
from .models import MenuItem

class CustomerOrderItemForm(forms.Form):
    menu_item = forms.ModelChoiceField(
        queryset=MenuItem.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select text-center border-primary',
            'aria-label': 'Select Menu Item'
        })
    )
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control text-center border-primary mb-3',
            'placeholder': 'Enter quantity'
        })
    )

# You can increase `extra` to show more rows
CustomerOrderFormSet = formset_factory(CustomerOrderItemForm, extra=5)
