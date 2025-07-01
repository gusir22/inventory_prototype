from collections import Counter
from datetime import datetime
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.utils.timezone import make_aware, localdate, localtime
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

        order = Order.objects.create()  # create order

        for form in formset:

            # get form field values from the request
            menu_item_name = form.cleaned_data.get('menu_item')
            quantity_ordered = form.cleaned_data.get('quantity')

            # if no menu item was chosen, the field is discarted and we move on to next
            # iteration of the form-forset loop
            if not menu_item_name:
                continue
            
            # Get MenuItem instance chosen by menu_item_name value
            menu_item = get_object_or_404(MenuItem, name=menu_item_name)

            # Cycle through all ingredients in the MenuItem instance to deduct ingredient from inventory
            for recipe_item in menu_item.recipe_items.all():
                ingredient = get_object_or_404(Ingredient, name=recipe_item.ingredient)  # access the Ingredient instance
                ingredient.quantity_in_stock -= recipe_item.quantity_needed * quantity_ordered  # update inventory amount
                ingredient.save()  # save new inventory amount

            OrderItem.objects.create(
                order=order, 
                menu_item=menu_item, 
                quantity=quantity_ordered
            )  # create order item

        return super().form_valid(formset)


class OrderSuccessView(TemplateView):
    template_name = "orders/order_success.html"


class SalesReportView(ListView):
    model = Order
    template_name = "orders/sales_report.html"
    context_object_name = "orders"

    def post(self, request, *args, **kwargs):
        # Store submitted dates in session or instance for reuse in get_context_data
        self.from_date = request.POST.get("from_date")
        self.to_date = request.POST.get("to_date")
        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        """Filters orders by today only"""
        if hasattr(self, "from_date") and self.from_date:
            # convert date times into aware to local time
            from_date = make_aware(datetime.fromisoformat(self.from_date))
            to_date = make_aware(datetime.fromisoformat(self.to_date))

            return Order.objects.filter(created_at__range=(from_date, to_date))
        else:
            today = localdate()
            return Order.objects.filter(created_at__date=today)
    
    def get_context_data(self, **kwargs):
        """Calculates data context for report using filtered queryset"""
        context = super().get_context_data(**kwargs)

        # Add todays date
        if self.request.method == "POST":
            from_date = make_aware(datetime.fromisoformat(self.from_date))
            to_date = make_aware(datetime.fromisoformat(self.to_date))
            context["from_date"] = from_date
            if from_date.date() != to_date.date():
                context["to_date"] = to_date
        else:
            context["from_date"] = localdate()

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
        if total_orders > 0:
            context['average_order_price'] = round_money(total_revenue / total_orders)
        else:
            context['average_order_price'] = Decimal("0.00")

        # create menu items sales data list
        menu_item_sales_count = {item.name: 0 for item in MenuItem.objects.all()}  # Initialize all menu items to 0 quantity sold menu item
        for order in orders:
            for order_item in order.orderitems.all():
                menu_item_sales_count[order_item.menu_item.name] += order_item.quantity  # add quantity sold to

        # sort for top-selling items
        top_items = sorted(menu_item_sales_count.items(), key=lambda x: x[1], reverse=True)[:5]  # top 5
        context['top_selling_labels'] = [item[0] for item in top_items]
        context['top_selling_data'] = [item[1] for item in top_items]

        # Sort for lowest-selling menu items
        lowest_items = sorted(menu_item_sales_count.items(), key=lambda x: x[1])[:5]  # bottom 5
        context['lowest_selling_labels'] = [item[0] for item in lowest_items]
        context['lowest_selling_data'] = [item[1] for item in lowest_items]

        # Count orders per hour
        order_hours = [
            localtime(order.created_at).hour
            for order in orders
            if 11 <= localtime(order.created_at).hour <= 21  # ensure it's within 11am–9pm
        ]
        order_hour_counts = Counter(order_hours)

        # Restaurant open-close range (e.g., 11 AM to 9 PM)
        hour_range = range(11, 22)  # 11 to 21 inclusive

        hour_labels = [f"{h}:00" for h in hour_range]
        hour_data = [order_hour_counts.get(h, 0) for h in hour_range]

        context["order_hour_labels"] = hour_labels
        context["order_hour_data"] = hour_data

        return context