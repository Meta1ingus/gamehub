from django.shortcuts import render
from .models import Game

def product_list(request):
    games = Game.objects.all()
    return render(request, 'products/product_list.html', {'games': games})