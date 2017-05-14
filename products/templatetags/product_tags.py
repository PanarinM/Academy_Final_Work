from django import template

from products.models import Category

register = template.Library()


@register.simple_tag(name='get_categories')
def get_objects():
    return Category.objects.all()


@register.simple_tag(name='get_cart_count')
def get_cart_count(request):
    items = request.session.get("cart", {})
    counter = 0
    for item in items:
        counter += items[item]
    return counter
