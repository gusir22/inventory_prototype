from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


# Create your models here.
class Ingredient(models.Model):
    """Represents an ingredient from a menu item, like a tomato. This model is used to keep track
    of current ingredient inventory."""
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default="g")  # grams, liters, etc.
    cost = models.DecimalField(max_digits=8, decimal_places=3)  # cost of ingredient single unit
    quantity_in_stock = models.FloatField(
        validators=[
            MinValueValidator(0),  # no stock item below zero
        ]
    )

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """Represent a full menu food item, like a burger. This model is used to help build a customer order and track 
    food analytics"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeItem')

    def __str__(self):
        return self.name
    
    def get_menu_item_cost(self):
        total_cost = 0

        for recipe_item in self.recipe_items.all():
            total_cost += recipe_item.get_recipe_item_cost()

        return total_cost
    
    def get_menu_item_profit(self):
        return self.price - self.get_menu_item_cost()

class RecipeItem(models.Model):
    """This proxy model helps add ingredients in varying quantitites to Menu Items.
    For exammple a Burger needing 3 tomatoes per serving."""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="recipe_items")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_needed = models.FloatField()  # quantity of ingredient needed per menu item

    def __str__(self):
        return f"{self.ingredient.name} for {self.menu_item.name}"
    
    def get_recipe_item_cost(self):
        return self.ingredient.cost * Decimal(self.quantity_needed)
