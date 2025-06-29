from django.db import models

from menu.models import MenuItem


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    menu_items = models.ManyToManyField(MenuItem, through='OrderItem')

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item} for {self.order}"