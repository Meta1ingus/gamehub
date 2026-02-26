from decimal import Decimal
from django.conf import settings
from .models import Game


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if cart is None:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, game, quantity=1, override_quantity=False):
        game_id = str(game.id)

        if game_id not in self.cart:
            self.cart[game_id] = {
                'quantity': 0,
                'price': str(game.price),
            }

        if override_quantity:
            self.cart[game_id]['quantity'] = quantity
        else:
            self.cart[game_id]['quantity'] += quantity

        self.save()

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def remove(self, game):
        game_id = str(game.id)
        if game_id in self.cart:
            del self.cart[game_id]
            self.save()

    def __iter__(self):
        game_ids = self.cart.keys()
        games = Game.objects.filter(id__in=game_ids)

        cart = self.cart.copy()
        for game in games:
            item = cart[str(game.id)]
            item['game'] = game
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        from decimal import Decimal
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())