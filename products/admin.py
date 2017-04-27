from django.contrib import admin
from django.contrib.postgres.fields import JSONField

from prettyjson import PrettyJSONWidget

from products.models import Product, Category, Comment, ShoppingCart


class JsonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }


admin.site.register(Product, JsonAdmin)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(ShoppingCart)
