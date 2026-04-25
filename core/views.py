from django.shortcuts import render
from products.models import Game, Platform, Genre, PlatformFamily
from django.db.models import Count

def home(request):
    games = Game.objects.filter(featured=True)

    families = PlatformFamily.objects.all().order_by("name")

    genres = (
        Genre.objects
        .annotate(game_count=Count('game'))
        .filter(game_count__gt=0)
        .order_by('name')
    )

    return render(request, "core/home.html", {
        "games": games,
        "families": families,
        "genres": genres,
    })
