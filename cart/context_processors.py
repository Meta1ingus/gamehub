from products.cart import Cart as SessionCart
from cart.models import Cart as UserCart

def cart_item_count(request):
    if request.user.is_authenticated:
        try:
            return {'cart_item_count': request.user.cart.total_quantity()}
        except UserCart.DoesNotExist:
            return {'cart_item_count': 0}
    else:
        cart = SessionCart(request)
        return {'cart_item_count': cart.get_total_quantity()}