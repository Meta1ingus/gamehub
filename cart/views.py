from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Game
from products.cart import Cart as SessionCart
from .models import Cart, CartItem

# IMPORTS FOR STRIPE CHECKOUT
from core.stripe_service import (
    build_line_items_from_cart,
    create_checkout_session_cart,
)


def cart_detail(request):
    if request.user.is_authenticated:
        try:
            cart = request.user.cart  # DB cart
            items = cart.items.all()
            total_price = cart.total_price()
            total_quantity = cart.total_quantity()
        except Cart.DoesNotExist:
            items = []
            total_price = 0
            total_quantity = 0
    else:
        cart = SessionCart(request)
        items = list(cart)
        total_price = cart.get_total_price()
        total_quantity = cart.get_total_quantity()

    context = {
        'items': items,
        'total_price': total_price,
        'total_quantity': total_quantity,
    }
    return render(request, 'products/cart_detail.html', context)


@require_POST
def cart_add(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            game=game,
            defaults={'quantity': 1, 'price': game.price}
        )
        if not created:
            item.quantity += 1
            item.save()
    else:
        cart = SessionCart(request)
        cart.add(game=game, quantity=1)

    return redirect('product_detail', slug=game.slug)


@require_POST
def cart_remove(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.user.is_authenticated:
        cart = request.user.cart
        cart.items.filter(game=game).delete()
    else:
        cart = SessionCart(request)
        cart.remove(game)

    return redirect('cart_detail')


@require_POST
def cart_update(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        cart = request.user.cart
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            game=game,
            defaults={'quantity': quantity, 'price': game.price}
        )
        item.quantity = quantity
        item.save()
    else:
        cart = SessionCart(request)
        cart.add(game=game, quantity=quantity, override_quantity=True)

    return redirect('cart_detail')


@require_POST
def cart_clear(request):
    if request.user.is_authenticated:
        request.user.cart.items.all().delete()
    else:
        cart = SessionCart(request)
        cart.clear()

    return redirect('cart_detail')


# MULTI‑ITEM CHECKOUT VIEW
@require_POST
def cart_checkout(request):
    # Logged-in users → DB cart
    if request.user.is_authenticated:
        cart = request.user.cart
        cart_items = cart.items.all()
    else:
        session_cart = SessionCart(request)
        cart_items = list(session_cart)

    # Convert cart items → Stripe line items
    line_items = build_line_items_from_cart(cart_items)

    # Create Stripe session
    session = create_checkout_session_cart(line_items)

    return redirect(session.url)
