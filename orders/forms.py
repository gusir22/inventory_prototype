from django import forms
from django.forms import formset_factory
from .models import MenuItem

class CustomerOrderItemForm(forms.Form):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.all())
    quantity = forms.IntegerField(min_value=1, initial=1)

# You can increase `extra` to show more rows
CustomerOrderFormSet = formset_factory(CustomerOrderItemForm, extra=5)
