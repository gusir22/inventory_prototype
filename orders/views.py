from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import CustomerOrderFormSet
from .models import Order, OrderItem


class HomePageView(FormView):
    template_name = "home.html"
    success_url = reverse_lazy('order_success')
    form_class = CustomerOrderFormSet  # We'll override get_form


class OrderSuccessView(TemplateView):
    template_name = "orders/order_success.html"
