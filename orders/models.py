from django.conf import settings
from django.db import models
from products.models import Game


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {'Paid' if self.is_paid else 'Unpaid'}"
    
    def mark_as_paid(self):
        self.is_paid = True
        self.save()



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of purchase",
    )

    def __str__(self):
        return f"{self.quantity} × {self.game.title} (Order #{self.order_id})"

    @property
    def total_price(self):
        return self.quantity * self.price
