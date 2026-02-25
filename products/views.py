from django.shortcuts import render, get_object_or_404
from .models import Game, Platform, Genre

def product_list(request):
    games = Game.objects.all()
    return render(request, 'products/product_list.html', {'games': games})

def product_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    return render(request, 'products/product_detail.html', {'game': game})

def platform_list(request):
    platforms = Platform.objects.all()
    return render(request, 'products/platform_list.html', {'platforms': platforms})

def platform_detail(request, slug):
    platform = get_object_or_404(Platform, slug=slug)
    games = Game.objects.filter(platform=platform)
    return render(request, 'products/platform_detail.html', {
        'platform': platform,
        'games': games
    })

def genre_list(request):
    genres = Genre.objects.all()
    return render(request, 'products/genre_list.html', {'genres': genres})

def genre_detail(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    games = Game.objects.filter(genre=genre)
    return render(request, 'products/genre_detail.html', {
        'genre': genre,
        'games': games
    })

def categories(request):
    return render(request, 'products/categories.html')