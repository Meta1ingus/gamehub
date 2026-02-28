from django.shortcuts import render
from products.models import Game, Platform, Genre

def home(request):
    games = Game.objects.filter(featured=True)
    platforms = Platform.objects.all()
    genres = Genre.objects.all()

    return render(request, "core/home.html", {
        "games": games,
        "platforms": platforms,
        "genres": genres,
    })