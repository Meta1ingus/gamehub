from django.shortcuts import render, get_object_or_404, redirect
from .models import Game, Platform, Genre, PlatformFamily
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from .cart import Cart
from django.db.models import Q, Count
from django.contrib import messages
from django.urls import reverse
from core.stripe_service import create_checkout_session
from django.contrib.auth import login

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

    # Filtering (use slugs)
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

    # Dynamic Filtering
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


def product_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)

    return render(request, "products/product_detail.html", {
        "game": game,
    })

def platform_list(request):
    platforms = Platform.objects.all()
    return render(request, 'products/platform_list.html', {'platforms': platforms})


def platform_detail(request, slug):
    platform = get_object_or_404(Platform, slug=slug)
    return redirect(f"{reverse('product_list')}?platform={platform.slug}")

def platform_family(request, family_slug):
    family = get_object_or_404(PlatformFamily, slug=family_slug)

    platforms = (
        family.platforms
        .annotate(game_count=Count("game"))
        .order_by("name")
    )

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


from django.db.models import Count

def categories(request):
    platforms = (
        Platform.objects
        .annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('name')
    )

    genres = (
        Genre.objects
        .annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('name')
    )

    return render(request, 'products/categories.html', {
        'platforms': platforms,
        'genres': genres,
    })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Auto-login the user
            login(request, user)

            messages.success(request, "Your account has been created.")

            # Redirect to homepage (storefront behaviour)
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@require_POST
def create_checkout_session_view(request, slug):
    game = get_object_or_404(Game, slug=slug)

    # 1. Create the Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_amount=game.price,
        is_paid=False,
    )

    # 2. Create the OrderItem
    OrderItem.objects.create(
        order=order,
        game=game,
        quantity=1,
        price=game.price,
    )

    # 3. Create Stripe session (passing the order)
    session = create_checkout_session(game, order)

    # 4. Save session ID
    order.stripe_session_id = session.id
    order.save()

    # 5. Redirect to Stripe
    return redirect(session.url)

@require_POST
def cart_checkout(request):
    # Logged-in users → DB cart
    if request.user.is_authenticated:
        cart = request.user.cart
        cart_items = cart.items.all()
    else:
        session_cart = SessionCart(request)
        cart_items = list(session_cart)

    # 1. Calculate total
    total = sum(item.price * item.quantity for item in cart_items)

    # 2. Create the Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_amount=total,
        is_paid=False,
    )

    # 3. Create OrderItems
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            game=item.game,
            quantity=item.quantity,
            price=item.price,
        )

    # 4. Convert cart items → Stripe line items
    line_items = build_line_items_from_cart(cart_items)

    # 5. Create Stripe session (passing the order)
    session = create_checkout_session_cart(line_items, order)

    # 6. Save session ID
    order.stripe_session_id = session.id
    order.save()

    # 7. Redirect to Stripe
    return redirect(session.url)

