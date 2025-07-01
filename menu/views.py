from collections import defaultdict

from django.views.generic import ListView

from .models import Ingredient, MenuItem


class IngredientListView(ListView):
    model = Ingredient
    template_name = "menu/inventory_list.html"
    context_object_name = "ingredients"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        grams = Ingredient.objects.filter(unit="g")
        ml = Ingredient.objects.filter(unit="ml")
        pieces = Ingredient.objects.filter(unit="Piece")

        context["g_labels"] = [i.name for i in grams]
        context["g_data"] = [i.quantity_in_stock for i in grams]

        context["ml_labels"] = [i.name for i in ml]
        context["ml_data"] = [i.quantity_in_stock for i in ml]

        context["pieces_labels"] = [i.name for i in pieces]
        context["pieces_data"] = [i.quantity_in_stock for i in pieces]

        return context


class MenuItemListView(ListView):
    model = MenuItem
    template_name = "menu/menu_list.html"
    context_object_name = "menu_items"
    