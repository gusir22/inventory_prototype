from django.contrib import admin

from . models import (
    Ingredient,
    MenuItem,
    RecipeItem,
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "quantity_in_stock",
        "unit",
        "cost",
    ]


admin.site.register(Ingredient, IngredientAdmin)

class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price",
    ]


admin.site.register(MenuItem, MenuItemAdmin)

class RecipeItemAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
    ]


admin.site.register(RecipeItem, RecipeItemAdmin)
