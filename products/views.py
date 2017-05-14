from datetime import datetime

from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from products.forms import CommentForm, AddToCartForm
from products.models import Product, Comment, ShoppingCart
from utils import gen_page_list
from decimal import Decimal


class Home(View):
    def get(self, request):
        products = Product.objects.order_by("-views")
        paginator = Paginator(products, 10)
        page = request.GET.get('page', 1)
        try:
            prods = paginator.page(page)
        except PageNotAnInteger:
            prods = paginator.page(1)
        except EmptyPage:
            prods = paginator.page(paginator.num_pages)

        page_numbers = gen_page_list(int(page), paginator.num_pages)
        return render(request, "home.html", {"products": prods, "page_numbers": page_numbers})


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
        commentform = CommentForm()
        cartform = AddToCartForm()
        return render(request, "single_product.html", {"prod": prod, "comments": comments, "commentform": commentform, "cartform": cartform})

    def post(self, request, prod_id):
        commentform = CommentForm(request.POST)
        cartform = AddToCartForm()
        prod = get_object_or_404(Product, pk=prod_id)
        comments = Comment.objects.filter(product_id=prod_id)
        if commentform.is_valid():
            author = request.user
            product = Product.objects.get(pk=prod_id)
            pos = commentform.cleaned_data["positive"]
            neg = commentform.cleaned_data["negative"]
            body = commentform.cleaned_data["body"]
            rating = commentform.cleaned_data["rating"]
            comm = Comment(author=author,
                           product=product,
                           positive=pos,
                           negative=neg,
                           body=body,
                           rating=rating)
            try:
                comm.save()
            except IntegrityError:
                commentform.add_error("positive", "You already added the comment. Edit the existing one!")
        return render(request, "single_product.html", {"prod": prod, "comments": comments, "commentform": commentform, "cartform": cartform})


class ProdByCat(View):
    def get(self, request, cat_name):
        products = Product.objects.filter(category__category_name=cat_name).order_by("-views")
        paginator = Paginator(products, 10)
        page = request.GET.get('page', 1)
        try:
            prods = paginator.page(page)
        except PageNotAnInteger:
            prods = paginator.page(1)
        except EmptyPage:
            prods = paginator.page(paginator.num_pages)

        page_numbers = gen_page_list(int(page), paginator.num_pages)
        return render(request, "products_by_cat.html", {"products": prods, "page_numbers": page_numbers})


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
        if request.user.is_authenticated:
            products = Product.objects.filter(product_in_cart__owner=request.user).order_by("id")
            total_cost = 0
            for item in products:
                item.counter = item.product_in_cart.get().counter
                total_cost += item.price * item.counter
            return render(request, "cart.html", {"products": products, "total": total_cost})
        else:
            cart = request.session.get("cart", {})
            products = []
            total_cost = 0
            for item in cart:
                try:
                    product = Product.objects.get(id=item)
                    product.counter = cart[item]
                    products.append(product)
                    total_cost += Decimal(cart[item]) * product.price
                except Product.DoesNotExist:
                    continue
            return render(request, "cart.html", {"products": products, "total": total_cost})


class AddToCartView(View):
    def post(self, request, prod_id):
        next_ = request.GET.get("next") if request.GET.get("next") is not None else reverse("home")
        product = get_object_or_404(Product, pk=prod_id)
        comments = Comment.objects.filter(product_id=product.id)
        cartform = AddToCartForm(request.POST)
        commentform = CommentForm()
        if request.user.is_authenticated:
            user = request.user
            if cartform.is_valid():
                counter = cartform.cleaned_data.get("counter", 0)
                cart = ShoppingCart(owner=user, item=product, counter=counter)
                try:
                    cart.save()
                except IntegrityError:
                    cart = ShoppingCart.objects.get(owner=user, item=product)
                    cart.counter += counter
                    try:
                        cart.save()
                    except IntegrityError:
                        HttpResponseRedirect(next_)
            return render(request, "single_product.html", {"prod": product, "comments": comments, "commentform": commentform, "cartform": cartform})
        else:
            cart = request.session.get("cart", {})
            if cartform.is_valid():
                cart[str(product.id)] = cart.setdefault(str(product.id), 0) + cartform.cleaned_data.get("counter", 0)
                request.session['cart'] = cart
                return HttpResponseRedirect(next_)
            return render(request, "single_product.html", {"prod": product, "comments": comments, "commentform": commentform, "cartform": cartform})


class DeleteFromShoppingCart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.delete()
        else:
            cart = request.session.get("cart", {})
            cart.pop(str(prod_id), None)
            request.session['cart'] = cart
        return HttpResponseRedirect(reverse("shoppingcart"))


class RemoveOneFromCart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.counter -= 1
            item.save()
        else:
            cart = request.session.get("cart", {})
            cart[str(prod_id)] -= 1
            request.session['cart'] = cart
        return HttpResponseRedirect(reverse("shoppingcart"))


class AddOneToCart(View):
    def get(self, request, prod_id):
        if request.user.is_authenticated:
            item = ShoppingCart.objects.get(item_id=prod_id)
            item.counter += 1
            item.save()
        else:
            cart = request.session.get("cart", {})
            cart[str(prod_id)] += 1
            request.session['cart'] = cart
        return HttpResponseRedirect(reverse("shoppingcart"))
