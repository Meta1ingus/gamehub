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
