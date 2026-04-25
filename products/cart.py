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

        # Get current quantity in cart (0 if not present)
        current_qty = self.cart.get(game_id, {}).get('quantity', 0)

        # DIGITAL ITEMS IGNORE STOCK
        if game.is_digital:
            if override_quantity:
                new_qty = quantity
            else:
                new_qty = current_qty + quantity

        else:
            # PHYSICAL ITEMS MUST RESPECT STOCK
            if override_quantity:
                new_qty = min(quantity, game.stock)
            else:
                new_qty = min(current_qty + quantity, game.stock)

        # Save back to session cart
        self.cart[game_id] = {
            'quantity': new_qty,
            'price': str(game.price),
        }

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
