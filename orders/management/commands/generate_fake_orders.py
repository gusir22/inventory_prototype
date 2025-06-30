import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from orders.models import Order, OrderItem
from menu.models import MenuItem


class Command(BaseCommand):
    help = "Generate fake orders from Jan 1 to Dec 31 with rush hour trends"

    def handle(self, *args, **kwargs):
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        menu_items = list(MenuItem.objects.all())

        if not menu_items:
            self.stdout.write(self.style.ERROR("No menu items found. Populate MenuItem first."))
            return

        # Popularity weights (simulate bestsellers & flops)
        # Repeat popular items, skip unpopular
        weighted_items = menu_items + random.choices(menu_items, k=10)  # Amplify some popularity

        total_orders = 0

        for day_offset in range((end_date - start_date).days + 1):
            current_day = start_date + timedelta(days=day_offset)

            # Simulate number of orders for this day (weekends are busier)
            base_orders = 10 if current_day.weekday() < 5 else 20
            num_orders = random.randint(base_orders, base_orders + 10)

            for _ in range(num_orders):
                # Choose rush period
                if random.random() < 0.5:
                    hour = random.randint(11, 14)  # Lunch
                else:
                    hour = random.randint(18, 21)  # Dinner

                # Random minute and second
                order_time = make_aware(datetime.combine(current_day, time(hour, random.randint(0, 59), random.randint(0, 59))))

                # Create Order
                order = Order.objects.create(created_at=order_time)

                # Choose number of items in this order (1–4)
                items_in_order = random.randint(1, 4)
                items = random.choices(weighted_items, k=items_in_order)

                # Add order items
                for item in items:
                    quantity = random.randint(1, 3)
                    OrderItem.objects.create(order=order, menu_item=item, quantity=quantity)

                total_orders += 1

        self.stdout.write(self.style.SUCCESS(f"✔ Created {total_orders} fake orders from {start_date.date()} to {end_date.date()}"))
