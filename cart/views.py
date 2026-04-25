from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Game
from products.cart import Cart as SessionCart
from .models import Cart, CartItem
from orders.models import Order, OrderItem

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

        # ⭐ STOCK‑AWARE LOGIC
        if not created:
            if game.is_digital:
                item.quantity += 1
            else:
                item.quantity = min(item.quantity + 1, game.stock)
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

        # ⭐ STOCK‑AWARE LOGIC
        if game.is_digital:
            item.quantity = quantity
        else:
            item.quantity = min(quantity, game.stock)

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
    # 1. Get cart items (DB or session)
    if request.user.is_authenticated:
        cart = request.user.cart
        cart_items = cart.items.all()
    else:
        session_cart = SessionCart(request)
        cart_items = list(session_cart)

    # STOCK VALIDATION BEFORE CHECKOUT
    from django.contrib import messages
    for item in cart_items:
        game = item.game

        # DIGITAL ITEMS IGNORE STOCK
        if not game.is_digital:
            if item.quantity > game.stock:
                messages.error(request, f"Not enough stock for {game.title}.")
                return redirect("cart_detail")

    # 2. Calculate total
    total_amount = sum(item.total_price for item in cart_items)

    # 3. Create the Order (unpaid for now)
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_amount=total_amount,
        is_paid=False,
    )

    # 4. Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            game=item.game,
            quantity=item.quantity,
            price=item.price,
        )

    # 5. Build Stripe line items
    line_items = build_line_items_from_cart(cart_items)

    # 6. Create Stripe session (NOW passing order)
    session = create_checkout_session_cart(line_items, order)

    # 7. Save Stripe session ID to the order
    order.stripe_session_id = session.id
    order.save()

    # 8. Redirect to Stripe
    return redirect(session.url)
