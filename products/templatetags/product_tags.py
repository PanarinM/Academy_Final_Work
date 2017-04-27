from django import template

from products.models import Category

register = template.Library()


@register.simple_tag(name='get_categories')
def get_objects():
    return Category.objects.all()
