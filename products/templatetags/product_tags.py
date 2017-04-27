from django import template

from products.models import Category, ShoppingCart

register = template.Library()


@register.simple_tag(name='get_categories')
def get_objects():
    return Category.objects.all()


@register.simple_tag(name='get_cart_count')
def get_cart_count(user):
    items = ShoppingCart.objects.filter(owner_id=user.id)
    counter = 0
    for item in items:
        counter += item.counter
    return counter
