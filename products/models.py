from django.core.exceptions import ValidationError
from django.db import models

from users.models import User
from utils import get_file_path


def validate_rating(value):
    if value > 10 or value < 0:
        raise ValidationError("%(value)s is not a valid rating. Rating must be 0 >= value <= 10",
                              params={"value": value}, )


class Category(models.Model):
    category_name = models.CharField(max_length=40)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name


class Product(models.Model):
    manufacturer = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    photo = models.FileField(upload_to=get_file_path)
    category = models.ForeignKey(Category, related_name="category")
    description = models.TextField(blank=True, null=True, default="There is no description for this product!")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("manufacturer", "name")

    def __str__(self):
        return "{}  {}  {}".format(self.manufacturer, self.name, self.category)


class Attribute(models.Model):
    category = models.ForeignKey(Category, related_name="attribute_for_category")
    name = models.CharField(max_length=40)
    dimension = models.CharField(max_length=10)

    def __str__(self):
        return "{}, {}".format(self.category, self.name)


class AttributeValue(models.Model):
    product = models.ForeignKey(Product, related_name="product_for_value")
    attribute = models.ForeignKey(Attribute, related_name="attribute_for_value")
    value = models.CharField(max_length=80)

    class Meta:
        unique_together = ("product", "attribute")

    def __str__(self):
        return self.value


class Comment(models.Model):
    author = models.ForeignKey(User, related_name="username_of_commenter")
    product = models.ForeignKey(Product, related_name="commented_product", null=True)
    positive = models.TextField(blank=True, null=True)
    negative = models.TextField(blank=True, null=True)
    body = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, validators=[validate_rating,])
    date = models.DateTimeField(auto_now_add=True, null=True)
    edit_date = models.DateTimeField(blank=True, null=True)
    edit_amount = models.IntegerField(default=0)

    class Meta:
        unique_together = ("author", "product")

    def __str__(self):
        return "{} {} {}".format(self.author, self.product, self.rating)


class ShoppingCart(models.Model):
    owner = models.ForeignKey(User, related_name="prod_owner")
    item = models.ForeignKey(Product, related_name="product_in_cart", null=True)
    counter = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("owner", "item")

    def __str__(self):
        return "{}  {}  {}".format(self.owner, self.item, self.counter)
