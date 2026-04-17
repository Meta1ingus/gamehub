from decimal import Decimal
from django.conf import settings
from .models import Game


class SessionCartItem:
    """
    A lightweight object representing a single item in the session cart.
    Matches the interface of OrderItem so checkout logic works consistently.
    """
    def __init__(self, game, price, quantity):
        self.game = game
        self.price = price
        self.quantity = quantity

    @property
    def total_price(self):
        return self.price * self.quantity


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
        """
        Yield CartItem objects instead of dicts.
        This makes the session cart compatible with OrderItem.
        """
        game_ids = self.cart.keys()
        games = Game.objects.filter(id__in=game_ids)

        for game in games:
            item = self.cart[str(game.id)]
            price = Decimal(item['price'])
            quantity = item['quantity']

            yield SessionCartItem(
                game=game,
                price=price,
                quantity=quantity
            )

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())
