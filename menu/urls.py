from django.contrib import admin
from django.urls import path

from .views import IngredientListView


urlpatterns = [
    path('inventory/', IngredientListView.as_view(), name="inventory"),
]
