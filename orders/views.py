from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.utils.timezone import now
from django.urls import reverse_lazy
from .forms import CustomerOrderFormSet
from .models import Order, OrderItem
from .helpers import round_money

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


class TodaySalesReportView(ListView):
    model = Order
    template_name = "orders/today_sale_report.html"
    context_object_name = "orders"

    def get_queryset(self):
        """Filters orders by today only"""
        today = now().date()  # get todays date
        return Order.objects.filter(created_at__date=today)  # filters by date
    
    def get_context_data(self, **kwargs):
        """Calculates data context for report using filtered queryset"""
        context = super().get_context_data(**kwargs)

        # Access the filtered queryset
        orders = self.get_queryset()

        # calculate orders made
        total_orders = len(orders)
        context['total_orders'] = total_orders

        # calculate revenue and cost
        total_revenue = 0  # init empty rev total
        total_cost = 0  # init empty cost total

        for order in orders:
            total_revenue += order.get_order_revenue()
            total_cost += order.get_order_cost()

        context['total_revenue'] = total_revenue
        context['total_cost'] = round_money(total_cost)
        context['total_profit'] = round_money(total_revenue - total_cost)  # calculate total profit
        context['average_order_price'] = total_revenue / total_orders

        return context