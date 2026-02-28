from django.shortcuts import render
from products.models import Game

def home(request):
    games = Game.objects.filter(featured=True)
    return render(request, "core/home.html", {"games": games})