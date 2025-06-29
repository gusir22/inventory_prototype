from django.urls import path

from .views import (
    HomePageView, 
    OrderSuccessView,
    TodaySalesReportView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('order-sucess/', OrderSuccessView.as_view(), name="order_success"),
    path('todays-report/', TodaySalesReportView.as_view(), name="todays_report"),
]
