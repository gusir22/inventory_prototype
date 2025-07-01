from django.urls import path

from .views import (
    PlaceOrderView, 
    OrderSuccessView,
    SalesReportView,
)

urlpatterns = [
    path('place-order/', PlaceOrderView.as_view(), name="place_order"),
    path('order-sucess/', OrderSuccessView.as_view(), name="order_success"),
    path('sales-report/', SalesReportView.as_view(), name="sales_report"),
]
