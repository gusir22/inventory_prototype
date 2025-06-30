from django.db import models

from menu.models import MenuItem


class Order(models.Model):
    created_at = models.DateTimeField()
    menu_items = models.ManyToManyField(MenuItem, through='OrderItem')

    def __str__(self):
        return f"Order #{self.id}"
    
    def get_order_revenue(self):
        total_revenue = 0

        for order_item in self.orderitems.all():
            total_revenue += order_item.get_order_item_revenue()

        return total_revenue

    def get_order_cost(self):
        total_cost = 0

        for order_item in self.orderitems.all():
            total_cost += order_item.get_order_item_cost()

        return total_cost
    
    def get_order_profit(self):
        return self.get_order_revenue() - self.get_order_cost()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderitems")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item} for {self.order}"
    
    def get_order_item_revenue(self):
        return self.menu_item.price * self.quantity
    
    def get_order_item_cost(self):
        return self.menu_item.get_menu_item_cost()