from django.core.management.base import BaseCommand

from products.models import Product, Category

from random import choice
from string import ascii_lowercase


class Command(BaseCommand):
    help = "Creates 30 random products"

    def handle(self, *args, **options):
        categories = Category.objects.all()
        for item in range(30):
            name = ''.join(choice(ascii_lowercase) for i in range(15))
            Product.objects.create(manufacturer="SONY",
                                   name=name,
                                   price=10,
                                   category=choice(categories))