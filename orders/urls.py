from django.urls import path

from orders.views import order_detail, order_list
from .webhooks import stripe_webhook

urlpatterns = [
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),

    path("orders/", order_list, name="orders"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
]
