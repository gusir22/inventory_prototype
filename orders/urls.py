from django.urls import path

from .views import (
    HomePageView, 
    OrderSuccessView,
    TodaySalesReportView,
    SalesReportView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('order-sucess/', OrderSuccessView.as_view(), name="order_success"),
    path('sales-report/', SalesReportView.as_view(), name="sales_report"),
]
