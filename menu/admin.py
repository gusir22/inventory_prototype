from django.contrib import admin

from . models import (
    Ingredient,
    MenuItem,
    RecipeItem,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "quantity_in_stock",
        "unit",
        "cost",
    ]

    search_fields = [
        "name",
    ]


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 3
    autocomplete_fields = [
        "ingredient"
    ]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "price",
    ]

    inlines = [RecipeItemInline]

    search_fields = [
        "name",
    ]
