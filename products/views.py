from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login

# Models
from .models import Game, Platform, Genre, PlatformFamily
from checkout.models import Order, OrderItem

# Session cart
from products.cart import Cart as SessionCart

# Stripe helpers
from core.stripe_service import (
    create_checkout_session,
    create_checkout_session_cart,
    build_line_items_from_cart,
)

# PRODUCT LISTING

def product_list(request):
    games = Game.objects.all()

    # Search
    query = request.GET.get('q')
    if query:
        games = games.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(platform__name__icontains=query) |
            Q(genre__name__icontains=query)
        )

    # Filtering
    platform_slug = request.GET.get('platform')
    if platform_slug:
        games = games.filter(platform__slug=platform_slug)

    genre_slug = request.GET.get('genre')
    if genre_slug:
        games = games.filter(genre__slug=genre_slug)

    # Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        games = games.order_by('price')
    elif sort == 'price_desc':
        games = games.order_by('-price')
    elif sort == 'title_asc':
        games = games.order_by('title')
    elif sort == 'title_desc':
        games = games.order_by('-title')

    # Dynamic filtering
    platforms = Platform.objects.all()
    genres = Genre.objects.all()

    # Pagination
    per_page = request.GET.get("per_page", 12)
    if per_page == "all":
        per_page = games.count()
    else:
        per_page = int(per_page)

    paginator = Paginator(games, per_page)
    page_number = request.GET.get("page")
    games = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'games': games,
        'current_sort': sort,
        'current_platform': platform_slug,
        'current_genre': genre_slug,
        'query': query,
        'platforms': platforms,
        'genres': genres,
    })

# PRODUCT DETAIL

def product_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, "products/product_detail.html", {"game": game})

# PLATFORM / GENRE VIEWS

def platform_list(request):
    platforms = Platform.objects.all()
    return render(request, 'products/platform_list.html', {'platforms': platforms})


def platform_detail(request, slug):
    platform = get_object_or_404(Platform, slug=slug)
    return redirect(f"{reverse('product_list')}?platform={platform.slug}")


def platform_family(request, family_slug):
    family = get_object_or_404(PlatformFamily, slug=family_slug)
    platforms = family.platforms.annotate(game_count=Count("game")).order_by("name")

    return render(request, "products/platform_family.html", {
        "family": family,
        "platforms": platforms,
    })


def genre_list(request):
    genres = Genre.objects.all()
    return render(request, 'products/genre_list.html', {'genres': genres})


def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    return redirect(f"{reverse('product_list')}?genre={genre.slug}")

# CATEGORIES PAGE

def categories(request):
    platforms = (
        Platform.objects.annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('name')
    )

    genres = (
        Genre.objects.annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('name')
    )

    return render(request, 'products/categories.html', {
        'platforms': platforms,
        'genres': genres,
    })

# USER REGISTRATION

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

# BUY NOW CHECKOUT

@require_POST
def create_checkout_session_view(request, slug):
    game = get_object_or_404(Game, slug=slug)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_amount=game.price,
        is_paid=False,
    )

    OrderItem.objects.create(
        order=order,
        game=game,
        quantity=1,
        price=game.price,
    )

    session = create_checkout_session(game, order)

    order.stripe_session_id = session.id
    order.save()

    return redirect(session.url)

# CART CHECKOUT

@require_POST
def cart_checkout(request):
    # Logged-in users → DB cart
    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        cart_items = cart.items.all() if cart else []
    else:
        session_cart = SessionCart(request)
        cart_items = list(session_cart)

    # Stock validation
    for item in cart_items:
        game = item.game
        if not game.is_digital and item.quantity > game.stock:
            messages.error(request, f"Not enough stock for {game.title}.")
            return redirect("cart_detail")

    # Calculate total
    total_amount = sum(item.total_price for item in cart_items)

    # Create order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_amount=total_amount,
        is_paid=False,
    )

    # Create order items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            game=item.game,
            quantity=item.quantity,
            price=item.price,
        )

    # Stripe line items
    line_items = build_line_items_from_cart(cart_items)

    # Create Stripe session
    session = create_checkout_session_cart(line_items, order)

    order.stripe_session_id = session.id
    order.save()

    return redirect(session.url)