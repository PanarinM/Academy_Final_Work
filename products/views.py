from datetime import datetime

from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.views import View

from products.forms import CommentForm
from products.models import Product, Comment, ShoppingCart


class Home(View):
    def get(self, request):
        prods = Product.objects.order_by("views")[:10]
        return render(request, "home.html", {"products": prods})


class OneProduct(View):
    def get(self, request, prod_id):
        prod = get_object_or_404(Product, pk=prod_id)
        prod.views += 1
        comments = Comment.objects.filter(product_id=prod_id)
        rating = [float(i.rating) for i in comments]
        try:
            prod.rating = "{:.1f}".format(sum(rating) / len(rating))
        except ZeroDivisionError:
            prod.rating = 0
        prod.save()
        form = CommentForm()
        return render(request, "single_product.html", {"prod": prod, "comments": comments, "form": form})

    def post(self, request, prod_id):
        form = CommentForm(request.POST)
        prod = get_object_or_404(Product, pk=prod_id)
        comments = Comment.objects.filter(product_id=prod_id)
        if form.is_valid():
            author = request.user
            product = Product.objects.get(pk=prod_id)
            pos = form.cleaned_data["positive"]
            neg = form.cleaned_data["negative"]
            body = form.cleaned_data["body"]
            rating = form.cleaned_data["rating"]
            comm = Comment(author=author,
                           product=product,
                           positive=pos,
                           negative=neg,
                           body=body,
                           rating=rating)
            try:
                comm.save()
            except IntegrityError:
                form.add_error("positive", "You already added the comment. Edit the existing one!")
        return render(request, "single_product.html", {"prod": prod, "comments": comments, "form": form})


class ProdByCat(View):
    def get(self, request, cat_name):
        prods = Product.objects.filter(category__category_name=cat_name)
        return render(request, "products_by_cat.html", {"products": prods})


class DelComment(View):
    def get(self, request, comment_id):
        next_ = request.GET.get("next") if request.GET.get("next") is not None else reverse("home")
        if request.user.is_authenticated:
            comment = Comment.objects.get(pk=comment_id)
            comment.delete()
        return HttpResponseRedirect(next_)


class EditComment(View):
    def get(self, request, comment_id):
        next_ = request.GET.get("next") if request.GET.get("next") is not None else reverse("home")
        comment = get_object_or_404(Comment, pk=comment_id)
        if comment.author_id == request.user.id or request.user.is_admin:
            form = CommentForm(instance=comment)
            return render(request, "edit_comment.html", {"form": form, "next": next_, "comment": comment})
        HttpResponseRedirect(reverse("home"))

    def post(self, request, comment_id):
        next_ = request.GET.get("next") if request.GET.get("next") is not None else reverse("home")
        form = CommentForm(request.POST)
        comment_old = Comment.objects.get(pk=comment_id)
        if form.is_valid() and (request.user.is_admin or comment_old.author_id == request.user.id):
            comment_old.positive = form.cleaned_data["positive"]
            comment_old.negative = form.cleaned_data["negative"]
            comment_old.body = form.cleaned_data["body"]
            comment_old.rating = form.cleaned_data["rating"]
            comment_old.edit_amount += 1
            comment_old.edit_date = datetime.now()
            comment_old.save()
        return HttpResponseRedirect(next_)


class ShoppingCartView(View):
    def get(self, request):
        prods = Product.objects.filter(product_in_cart__owner=request.user).order_by("id")
        total_cost = 0
        for item in prods:
            total_cost += item.price*item.product_in_cart.get().counter
        if request.user.is_authenticated:
            return render(request, "cart.html", {"products": prods, "total": total_cost})
        HttpResponseRedirect(reverse("home"))


class DeleteFromCart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.delete()
        return HttpResponseRedirect(reverse("shoppingcart"))


class RemoveOneFromCart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.counter -= 1
            item.save()
        return HttpResponseRedirect(reverse("shoppingcart"))


class AddOneToCart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.counter += 1
            item.save()
        return HttpResponseRedirect(reverse("shoppingcart"))
