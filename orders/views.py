from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView
from django.utils.timezone import make_aware, localdate, localtime
from django.urls import reverse_lazy
from .forms import CustomerOrderFormSet
from .models import Order, OrderItem
from .helpers import round_money

from menu.models import MenuItem, Ingredient


from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import CustomerOrderFormSet
from .models import Order, OrderItem
from menu.models import MenuItem, Ingredient


class PlaceOrderView(TemplateView):
    template_name = "orders/place_order.html"
    
    def get(self, request, *args, **kwargs):
        formset = CustomerOrderFormSet()
        return render(request, self.template_name, {"formset": formset})

    def post(self, request, *args, **kwargs):
        
        formset = CustomerOrderFormSet(request.POST)
    
        order = Order.objects.create()

        for form in formset:
            menu_item_id = form.data.get(f'{form.prefix}-menu_item')
            quantity = form.data.get(f'{form.prefix}-quantity')

            if not menu_item_id or not quantity:
                continue
            
            # Get MenuItem instance chosen by menu_item_name value
            menu_item = get_object_or_404(MenuItem, id=menu_item_id)

            for recipe_item in menu_item.recipe_items.all():
                ingredient = get_object_or_404(Ingredient, name=recipe_item.ingredient)
                ingredient.quantity_in_stock -= recipe_item.quantity_needed * float(quantity)
                ingredient.save()

            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                quantity=quantity
            )

        return redirect(reverse_lazy("order_success"))


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
        if hasattr(self, "from_date") and self.from_date:
            from_date = make_aware(datetime.fromisoformat(self.from_date))
            to_date = make_aware(datetime.fromisoformat(self.to_date))
            return Order.objects.filter(created_at__range=(from_date, to_date))\
                                .prefetch_related("orderitems__menu_item")
        else:
            today = localdate()
            return Order.objects.filter(created_at__date=today)\
                                .prefetch_related("orderitems__menu_item")

    
    def get_context_data(self, **kwargs):
        """Calculates data context for report using filtered queryset"""
        context = super().get_context_data(**kwargs)
        
        # Initialize defaults
        today = localdate()
        from_date = make_aware(datetime.combine(today, datetime.min.time()))
        to_date = make_aware(datetime.combine(today, datetime.max.time()))
        multi_day_range = False  # init multi-day range flag

        # Override with POSTed values if applicable
        if self.request.method == "POST":
            self.from_date = self.request.POST.get("from_date")
            self.to_date = self.request.POST.get("to_date")

            if self.from_date and self.to_date:
                from_date = make_aware(datetime.fromisoformat(self.from_date))
                to_date = make_aware(datetime.fromisoformat(self.to_date))
                context["from_date"] = from_date
                if from_date.date() != to_date.date():
                    context["to_date"] = to_date
                    multi_day_range = True
        else:
            context["from_date"] = from_date.date()

        # Access the filtered queryset
        orders = self.get_queryset()

        # calculate orders made
        total_orders = len(orders)
        context['total_orders'] = total_orders

        # calculate revenue and cost
        total_revenue = 0  # init empty rev total
        total_cost = 0  # init empty cost total
        revenue_by_day = defaultdict(Decimal)  # init empty revenue by day
        menu_item_sales_count = {item.name: 0 for item in MenuItem.objects.all()}  # Initialize all menu items to 0 quantity sold menu item

        for order in orders:
            for order_item in order.orderitems.all():
                quantity = order_item.quantity
                menu_item = order_item.menu_item
                item_revenue = menu_item.price * quantity
                item_cost = menu_item.get_menu_item_cost()  # ideally cached if needed
                total_revenue += item_revenue
                total_cost += item_cost
                revenue_by_day[order.created_at.date()] += item_revenue
                menu_item_sales_count[menu_item.name] += quantity

        context['total_revenue'] = total_revenue
        context['total_cost'] = round_money(total_cost)
        context['total_profit'] = round_money(total_revenue - total_cost)  # calculate total profit
        if total_orders > 0:
            context['average_order_price'] = round_money(total_revenue / total_orders)
        else:
            context['average_order_price'] = Decimal("0.00")

        # create context data for doughnut chart
        context["revenue_doughnut_labels"] = ["Cost", "Profit"]
        context["revenue_doughnut_data"] = [float(total_cost), float(total_revenue - total_cost)]

        # sort for top-selling items
        top_items = sorted(menu_item_sales_count.items(), key=lambda x: x[1], reverse=True)[:3]  # top 3
        context['top_selling_labels'] = [item[0] for item in top_items]
        context['top_selling_data'] = [item[1] for item in top_items]

        # Sort for lowest-selling menu items
        lowest_items = sorted(menu_item_sales_count.items(), key=lambda x: x[1])[:3]  # bottom 3
        # Reverse to make lowest-selling at the bottom of the chart
        lowest_items.reverse()
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
            
        # Fill in all days in range with 0 if no revenue
        current_day = from_date.date()
        while current_day <= to_date.date():
            revenue_by_day.setdefault(current_day, Decimal("0.00"))
            current_day += timedelta(days=1)

        # Prepare data for Chart.js
        sorted_dates = sorted(revenue_by_day.keys())
        context["multi_day_range"] = multi_day_range  # pass multi-day range flag to template
        context["daily_revenue_labels"] = [d.strftime("%m/%d") for d in sorted_dates]
        context["daily_revenue_data"] = [float(revenue_by_day[d]) for d in sorted_dates]

        return context