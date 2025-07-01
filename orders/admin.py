from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 6
    autocomplete_fields = [
        "menu_item",
    ]
    


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "created_at",
    ]
    list_filter = [
        "created_at",
    ]
    inlines = [OrderItemInline]

