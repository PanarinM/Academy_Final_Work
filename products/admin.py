from django.contrib import admin

from products.models import Product, Category, Comment, Attribute, AttributeValue


class AttributeAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "dimension")


class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute", "value")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "product", "date")


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "manufacturer", "category", "price", "rating", "views")


admin.site.register(Product, ProductAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
