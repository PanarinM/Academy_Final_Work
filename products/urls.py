from django.conf.urls import url

from products.views import OneProduct, ProdByCat, DelComment, EditComment, ShoppingCartView, AddToCartView, DeleteFromShoppingCart, AddOneToCart, RemoveOneFromCart

urlpatterns = [
    url(r'^(?P<prod_id>[\d]+)/$', OneProduct.as_view(), name="single_product"),
    url(r'^(?P<cat_name>[\w]+)/$', ProdByCat.as_view(), name="prod_by_cat"),
    url(r'^delcomment/(?P<comment_id>[\d]+)/$', DelComment.as_view(), name="delete_comment"),
    url(r'^editcomment/(?P<comment_id>[\d]+)/$', EditComment.as_view(), name="edit_comment"),
    url(r'^checkout/shoppingcart/$', ShoppingCartView.as_view(), name='shoppingcart'),
    url(r'^checkout/shoppingcart/del/(?P<prod_id>[\d]+)$', DeleteFromShoppingCart.as_view(), name='del_shoppingcart'),
    url(r'^checkout/shoppingcart/pl/(?P<prod_id>[\d]+)$', AddOneToCart.as_view(), name='plus_shoppingcart'),
    url(r'^checkout/shoppingcart/mn/(?P<prod_id>[\d]+)$', RemoveOneFromCart.as_view(), name='minus_shoppingcart'),
    url(r'^checkout/shoppingcart/add/(?P<prod_id>[\d]+)$', AddToCartView.as_view(), name='add_to_shoppingcart'),
]
