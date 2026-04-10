from django.shortcuts import render
from products.models import Game, Platform, Genre
from django.db.models import Count

def home(request):
    games = Game.objects.filter(featured=True)

    manufacturers = (
        Platform.objects
        .values('manufacturer', 'manufacturer_slug')
        .annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('manufacturer')
    )

    genres = (
        Genre.objects
        .annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('name')
    )

    return render(request, "core/home.html", {
        "games": games,
        "manufacturers": manufacturers,
        "genres": genres,
    })