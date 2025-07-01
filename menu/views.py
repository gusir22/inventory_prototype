from django.views.generic import ListView

from .models import Ingredient, MenuItem


class IngredientListView(ListView):
    model = Ingredient
    template_name = "menu/inventory_list.html"
    context_object_name = "ingredients"


class MenuItemListView(ListView):
    model = MenuItem
    template_name = "menu/menu_list.html"
    context_object_name = "menu_items"
    