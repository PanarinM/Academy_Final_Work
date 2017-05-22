from django.contrib import admin

from products.models import Product, Category, Comment, Attribute, AttributeValue, ShoppingCart, HistoryOfPurchases


class AttributeAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "dimension")


class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute", "value")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("owner", "item", "counter")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "product", "date")


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer", "category", "price", "rating", "views")


class HistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "date")


admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
admin.site.register(HistoryOfPurchases, HistoryAdmin)
