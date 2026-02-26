from django.shortcuts import render, get_object_or_404, redirect
from .models import Game, Platform, Genre
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm

def product_list(request):
    # Only show featured games on the storefront
    featured_games = Game.objects.filter(featured=True)

    paginator = Paginator(featured_games, 9)  # 9 featured games per page
    page_number = request.GET.get('page')
    games_page = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'games': games_page,
    })

def product_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'products/product_detail.html', {'game': game})

def platform_list(request):
    platforms = Platform.objects.all()
    return render(request, 'products/platform_list.html', {'platforms': platforms})

def platform_detail(request, slug):
    platform = get_object_or_404(Platform, slug=slug)
    games = Game.objects.filter(platform=platform).order_by('title')
    return render(request, 'products/platform_detail.html', {
        'platform': platform,
        'games': games
    })

def genre_list(request):
    genres = Genre.objects.all()
    return render(request, 'products/genre_list.html', {'genres': genres})

def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    games = Game.objects.filter(genre=genre).order_by('title')
    return render(request, 'products/genre_detail.html', {
        'genre': genre,
        'games': games
    })

def categories(request):
    platforms = Platform.objects.all()
    genres = Genre.objects.all()

    return render(request, 'products/categories.html', {
        'platforms': platforms,
        'genres': genres,
    })

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})