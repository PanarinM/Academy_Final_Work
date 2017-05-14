from django import template

from products.models import Category, ShoppingCart

register = template.Library()


@register.simple_tag(name='get_categories')
def get_objects():
    return Category.objects.all()


@register.simple_tag(name='get_cart_count')
def get_cart_count(request):
    if request.user.is_authenticated:
        items = ShoppingCart.objects.filter(owner_id=request.user.id)
        counter = 0
        for item in items:
            counter += item.counter
    else:
        items = request.session.get("cart", {})
        counter = 0
        for item in items:
            counter += items[item]
    return counter
