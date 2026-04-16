import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(game):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": game.title,
                    },
                    "unit_amount": int(game.price * 100),  # Decimal → pence
                },
                "quantity": 1,
            }
        ],
        success_url="http://localhost:8000/checkout/success/",
        cancel_url="http://localhost:8000/checkout/cancel/",
    )

def create_checkout_session_cart(line_items):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url="http://localhost:8000/checkout/success/",
        cancel_url="http://localhost:8000/checkout/cancel/",
    )

def build_line_items_from_cart(cart_items):
    line_items = []

    for item in cart_items:
        line_items.append({
            "price_data": {
                "currency": "gbp",
                "product_data": {
                    "name": item.game.title,
                },
                "unit_amount": int(item.price * 100),
            },
            "quantity": item.quantity,
        })

    return line_items