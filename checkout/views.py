from django.shortcuts import render
from products.cart import Cart as SessionCart
from cart.models import Cart as DBCart

def success(request):
    # Clear session cart (logged-out users)
    session_cart = SessionCart(request)
    session_cart.clear()

    # Clear DB cart (logged-in users)
    if request.user.is_authenticated:
        try:
            db_cart = request.user.cart
            db_cart.items.all().delete()
        except DBCart.DoesNotExist:
            pass

    return render(request, "checkout/success.html")


def cancel(request):
    return render(request, "checkout/cancel.html")
