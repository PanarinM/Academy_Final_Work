import json
from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.formatters.html import HtmlFormatter
import re
from datetime import datetime

from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.views import View
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.utils import IntegrityError

from products.models import Product, Comment, ShoppingCart
from products.forms import CommentForm


def JsonPrettifier(data):
    response = json.dumps(data, sort_keys=True, indent=3)
    format_ = HtmlFormatter(style='friendly')
    response = highlight(response, JsonLexer(), format_)
    response = re.sub(r'[{,}]', "", response)
    response = re.sub(r'&quot;', "", response)
    style = "<style>" + format_.get_style_defs() + "</style>"
    return mark_safe(style+response)


class Home(View):
    def get(self, request):
        prods = Product.objects.order_by('views')[:10]
        for item in prods:
            item.attributes = JsonPrettifier(item.attributes)
        return render(request, 'home.html', {'products': prods})


class OneProduct(View):
    def get(self, request, prod_id):
        prod = get_object_or_404(Product, pk=prod_id)
        prod.views += 1
        comments = Comment.objects.filter(product_id=prod_id)
        rating = [float(i.rating) for i in comments]
        try:
            prod.rating = '{:.1f}'.format(sum(rating)/len(rating))
        except ZeroDivisionError:
            prod.rating = 0
        prod.save()
        prod.attributes = JsonPrettifier(prod.attributes)
        form = CommentForm()
        return render(request, 'single_product.html', {'prod': prod, 'comments': comments, 'form': form})

    def post(self, request, prod_id):
        form = CommentForm(request.POST)
        prod = get_object_or_404(Product, pk=prod_id)
        prod.attributes = JsonPrettifier(prod.attributes)
        comments = Comment.objects.filter(product_id=prod_id)
        if form.is_valid():
            commenter = request.user
            product = Product.objects.get(pk=prod_id)
            pos = form.cleaned_data['positive']
            neg = form.cleaned_data['negative']
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']
            comm = Comment(commenter=commenter,
                           product=product,
                           positive=pos,
                           negative=neg,
                           body=body,
                           rating=rating)
            try:
                comm.save()
            except IntegrityError:
                form.add_error('positive', 'You already added the comment. Edit the existing one!')
        return render(request, 'single_product.html', {'prod': prod, 'comments': comments, 'form': form})


class ProdByCat(View):
    def get(self, request, cat_name):
        prods = Product.objects.filter(category__category_name=cat_name)
        for item in prods:
            item.attributes = JsonPrettifier(item.attributes)
        return render(request, 'products_by_cat.html', {'products': prods})


class Del_Comment(View):
    def get(self, request, comment_id):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        if request.user.is_authenticated:
            comment = Comment.objects.get(pk=comment_id)
            comment.delete()
        return HttpResponseRedirect(next_)


class Edit_comment(View):
    def get(self, request, comment_id):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.commenter_id == request.user.id or request.user.is_admin:
            form = CommentForm(instance=comment)
            return render(request, 'edit_comment.html', {'form': form, 'next': next_, 'comment': comment})
        HttpResponseRedirect(reverse('home'))

    def post(self, request, comment_id):
        next_ = request.GET.get('next') if request.GET.get('next') is not None else reverse('home')
        form = CommentForm(request.POST)
        comment_old = Comment.objects.get(pk=comment_id)
        if form.is_valid() and (request.user.is_admin or comment_old.commenter_id == request.user.id):
            comment_old.positive = form.cleaned_data['positive']
            comment_old.negative = form.cleaned_data['negative']
            comment_old.body = form.cleaned_data['body']
            comment_old.rating = form.cleaned_data['rating']
            comment_old.edit_amount += 1
            comment_old.edit_date = datetime.now()
            comment_old.save()
        return HttpResponseRedirect(next_)


class Shopping_Cart(View):
    def get(self, request):
        prods = Product.objects.filter(product_in_cart__owner=request.user).order_by('id')
        total_cost = 0
        for item in prods:
            item.attributes = JsonPrettifier(item.attributes)
            total_cost += item.price*item.product_in_cart.get().counter
        if request.user.is_authenticated:
            return render(request, 'cart.html', {'products': prods, "total": total_cost})
        HttpResponseRedirect(reverse('home'))


class Delete_From_Cart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.delete()
        return HttpResponseRedirect(reverse('shoppingcart'))


class Minus_From_Cart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.counter -= 1
            item.save()
        return HttpResponseRedirect(reverse('shoppingcart'))


class Plus_From_Cart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.counter += 1
            item.save()
        return HttpResponseRedirect(reverse('shoppingcart'))

