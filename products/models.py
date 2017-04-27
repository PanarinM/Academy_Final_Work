from django.db import models
from django.contrib.postgres.fields import JSONField
from utils import get_file_path
from django.core.exceptions import ValidationError

from users.models import User


def validate_rating(value):
    if value > 10 or value < 0:
        raise ValidationError('%(value)s is not a valid rating. Rating must be 0 >= value <= 10', params={'value': value},)


class Category(models.Model):
    category_name = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.category_name


class Product(models.Model):
    manufacturer = models.CharField(max_length=40, blank=False, null=False)
    name = models.CharField(max_length=40, blank=False, null=False)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    photo = models.FileField(upload_to=get_file_path)
    category = models.ForeignKey(Category, related_name='category')
    attributes = JSONField()
    description = models.TextField(blank=True, null=True, default='There is no description for this product!')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('manufacturer', 'name')

    def __str__(self):
        return '{} {} {}'.format(self.manufacturer, self.name, self.category)


class Comment(models.Model):
    commenter = models.ForeignKey(User, related_name='username_of_commenter')
    product = models.ForeignKey(Product, related_name='commented_product', null=True)
    positive = models.TextField(blank=True, null=True)
    negative = models.TextField(blank=True, null=True)
    body = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[validate_rating,])
    date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(blank=True, null=True)
    edit_amount = models.IntegerField(default=0)

    class Meta:
        unique_together = ('commenter', 'product')

    def __str__(self):
        return '{} {} {}'.format(self.commenter, self.product, self.rating)


class ShoppingCart(models.Model):
    owner = models.OneToOneField(User, related_name='cart_owner')
    items = models.ManyToManyField(Product, related_name='products_in_cart')

    def __str__(self):
        return '{}, items count({})'.format(self.owner, self.items.count())

    @property
    def item_count(self):
        return self.items.count()
