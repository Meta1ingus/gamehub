from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem
from products.models import Game
from products.cart import Cart as SessionCart

@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    # Session cart (anonymous)
    session_cart = SessionCart(request)

    # If session cart is empty, nothing to merge
    if len(session_cart) == 0:
        return

    # Get or create the user's persistent cart
    cart, created = Cart.objects.get_or_create(user=user)

    # Merge each item from session cart into DB cart
    for item in session_cart:
        game = item['game']
        quantity = item['quantity']
        price = item['price']

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            game=game,
            defaults={'quantity': quantity, 'price': price}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

    # Clear the session cart after merging
    session_cart.clear()