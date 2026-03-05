from django.shortcuts import render, get_object_or_404, redirect
from .models import Game, Platform, Genre
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.http import require_POST
from .cart import Cart
from django.db.models import Q, Count
from django.contrib import messages

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
    per_page = request.GET.get("per_page", 12)  # default 12
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
    return render(request, 'products/product_detail.html', {'game': game})

def platform_list(request):
    platforms = Platform.objects.all()
    return render(request, 'products/platform_list.html', {'platforms': platforms})

def platform_detail(request, slug):
    platform = get_object_or_404(Platform, slug=slug)
    return redirect(f"{reverse('product_list')}?platform={platform.slug}")


def genre_list(request):
    genres = Genre.objects.all()
    return render(request, 'products/genre_list.html', {'genres': genres})

def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    return redirect(f"{reverse('product_list')}?genre={genre.slug}")

def categories(request):
    platforms = Platform.objects.annotate(game_count=Count('game'))
    genres = Genre.objects.annotate(game_count=Count('game'))

    return render(request, 'products/categories.html', {
        'platforms': platforms,
        'genres': genres,
    })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created. You can now log in.")
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
