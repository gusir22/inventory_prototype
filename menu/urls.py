from django.contrib import admin
from django.urls import path

from .views import IngredientListView, MenuItemListView


urlpatterns = [
    path('inventory/', IngredientListView.as_view(), name="inventory"),
    path('menu/', MenuItemListView.as_view(), name="menu"),
]
