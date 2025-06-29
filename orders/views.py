from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import CustomerOrderFormSet
from .models import Order, OrderItem

from menu.models import MenuItem, Ingredient


class HomePageView(FormView):
    template_name = "home.html"
    success_url = reverse_lazy('order_success')
    form_class = CustomerOrderFormSet  # We'll override get_form

    def form_valid(self, formset):
        # cycle through all menu items and check their IgredientItems to update the Ingredient's quantity_in_stock variable

        for form in formset:
            menu_item_name = form.cleaned_data.get('menu_item')
            quantity_ordered = form.cleaned_data.get('quantity')

            if not menu_item_name:
                continue

            menu_item = get_object_or_404(MenuItem, name=menu_item_name)

            for recipe_item in menu_item.recipe_items.all():
                ingredient = get_object_or_404(Ingredient, name=recipe_item.ingredient)
                ingredient.quantity_in_stock -= recipe_item.quantity_needed * quantity_ordered
                ingredient.save()  

        return super().form_valid(formset)


class OrderSuccessView(TemplateView):
    template_name = "orders/order_success.html"
