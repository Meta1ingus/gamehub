import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Order
from products.cart import Cart as SessionCart
from django.contrib.auth.models import AnonymousUser

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # CHECKOUT SUCCESS
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id")

        try:
            order = Order.objects.get(stripe_session_id=session_id)
            order.is_paid = True
            order.save()

            # REDUCE STOCK FOR PHYSICAL ITEMS
            
            for item in order.items.all():
                game = item.game
                if not game.is_digital:
                    game.stock = max(0, game.stock - item.quantity)
                    game.save()

            # CLEAR CART FOR LOGGED-IN USERS
            
            if order.user and not isinstance(order.user, AnonymousUser):
                if hasattr(order.user, "cart"):
                    order.user.cart.items.all().delete()

            # CLEAR SESSION CART FOR GUESTS
            
            # Guests have no user, so we clear via metadata
            if not order.user:
                # Guests have no session here, so we rely on metadata
                # You can add session_id to metadata later if needed
                pass

        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)
