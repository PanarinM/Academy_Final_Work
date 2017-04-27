from django.conf.urls import url

from products.views import OneProduct, ProdByCat, Del_Comment, Edit_comment, Shopping_Cart


urlpatterns = [
    url(r'^(?P<prod_id>[\d]+)/$', OneProduct.as_view(), name="single_product"),
    url(r'^(?P<cat_name>[\w]+)/$', ProdByCat.as_view(), name="prod_by_cat"),
    url(r'^delcomment/(?P<comment_id>[\d]+)/$', Del_Comment.as_view(), name="delete_comment"),
    url(r'^editcomment/(?P<comment_id>[\d]+)/$', Edit_comment.as_view(), name="edit_comment"),
    url(r'^checkout/shoppingcart/$', Shopping_Cart.as_view(), name='shoppingcart'),
    # url(r'^shoppingcart/$', Shopping_Cart.as_view(), name="shoppingcart"),
]
