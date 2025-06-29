from django.views.generic import ListView

from .models import Ingredient


class IngredientListView(ListView):
    model = Ingredient
    template_name = "menu/inventory_list.html"
    context_object_name = "ingredients"
