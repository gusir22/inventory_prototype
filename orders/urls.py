from django.urls import path

from .views import HomePageView, OrderSuccessView

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    path('order-sucess/', OrderSuccessView.as_view(), name="order_success"),
]
