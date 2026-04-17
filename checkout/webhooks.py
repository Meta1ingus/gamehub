from importlib.metadata import metadata

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # StripeObject → convert to dict safely
        metadata = session.metadata.to_dict() if session.metadata else {}
        order_id = metadata.get("order_id")

        if order_id:
            from orders.models import Order
            try:
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()
            except Exception as e:
                print("WEBHOOK ERROR:", e)

    return HttpResponse(status=200)
