from datetime import datetime
from decimal import Decimal
from functools import reduce
from reportlab.lib.pagesizes import A4, inch, portrait
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
import operator
from io import BytesIO

from django.db.utils import IntegrityError
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from django.core.mail import EmailMessage


from products.forms import CommentForm, AddToCartForm
from products.models import Product, Comment, ShoppingCart, HistoryOfPurchases
from utils import gen_page_list
from core.models import Configuration


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
        return render(request, "single_product.html", {"prod": prod, "comments": comments,
                                                       "commentform": commentform, "cartform": cartform})

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
        return render(request, "single_product.html", {"prod": prod, "comments": comments,
                                                       "commentform": commentform, "cartform": cartform})


class ProdByCat(View):
    def get(self, request, cat_name):
        products = list(Product.objects.filter(category__category_name=cat_name).order_by("-views"))
        filters = {}
        for product in products:
            for attribute, value in product._get_filters().items():
                filters.setdefault(attribute, set())
                filters[attribute].update(value)

        filtered_products = []

        def filterfunc(prod, filter_, value):
            if filter_ in prod._get_filters():
                if value in prod._get_filters()[filter_]:
                    return True
                else:
                    return False
            else:
                return False

        for filter_ in filters:
            if filter_ in request.GET:
                filtered_products += [prod for prod in products if filterfunc(prod, filter_, request.GET.get(filter_))]

        if len(filtered_products) > 0:
            products = list(set(filtered_products))

        paginator = Paginator(products, 10)
        page = request.GET.get('page', 1)
        try:
            prods = paginator.page(page)
        except PageNotAnInteger:
            prods = paginator.page(1)
        except EmptyPage:
            prods = paginator.page(paginator.num_pages)

        page_numbers = gen_page_list(int(page), paginator.num_pages)
        return render(request, "products_by_cat.html", {"products": prods,
                                                        "page_numbers": page_numbers,
                                                        "filters": filters})


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
            return render(request, "single_product.html",
                          {"prod": product, "comments": comments, "commentform": commentform, "cartform": cartform})
        else:
            cart = request.session.get("cart", {})
            if cartform.is_valid():
                cart[str(product.id)] = cart.setdefault(str(product.id), 0) + cartform.cleaned_data.get("counter", 0)
                request.session['cart'] = cart
                return HttpResponseRedirect(next_)
            return render(request, "single_product.html",
                          {"prod": product, "comments": comments, "commentform": commentform, "cartform": cartform})


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


def gen_pdf(request, *args):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="somefilename.pdf"'

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10, leftMargin=10, topMargin=30, bottomMargin=18)
    doc.pagesize = portrait(A4)
    elements = []

    style = TableStyle([('VALIGN', (0, 0), (0, -1), 'TOP'),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.blue),
                        ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                        ('TEXTCOLOR', (0, -1), (-1, -1), colors.green),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                        ])
    header_style = TableStyle([('VALIGN', (0, 0), (3, -1), 'TOP'),
                               ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
                               ('SIZE', (0, 0), (0, 3), 15),
                               ('SIZE', (3, 0), (3, 0), 20)
                               ])
    try:
        logo = Image(".{}".format(Configuration.objects.all()[0].logo.url))
        logo.drawHeight = 2*inch*logo.drawHeight / logo.drawWidth
        logo.drawWidth = 2*inch
    except OSError:
        logo = """here will be logo 
                  image when media
                  is ready!"""

    header_data = [[logo, "", "", request.get_host()],
                   ["", "", "",  Configuration.objects.all()[0].privacy_policy],
                   ]

    data = [["Product id", "Product name", "Amount", "Price", "Sub/Total"]]

    if request.user.is_authenticated:
        header_data.append([request.user.username, "", "", ""])
        header_data.append([request.user.email, "", "", ""])
        header_data.append(["", "", "", ""])
        header_data.append(["", "", "", ""])
        products = Product.objects.filter(product_in_cart__owner=request.user).order_by("id")
        total_cost = 0
        for item in products:
            item.counter = item.product_in_cart.get().counter
            data.append([item.id,
                         item.name,
                         item.counter,
                         "{} $".format(item.price),
                         "{} $".format(item.price*item.counter)])
            total_cost += item.price * item.counter
        data.append([" ", " ", " ", " ", "{} $".format(total_cost)])
        header = Table(data=header_data, colWidths=[150, 75, 75, 150])
        header.setStyle(tblstyle=header_style)
        t = Table(data=data, colWidths=[150, 150, 50, 50, 50])
        t.setStyle(tblstyle=style)
        elements.append(header)
        elements.append(t)

    else:
        header_data.append(["", "", "", ""])
        header_data.append([args[0], "", "", ""])
        header_data.append(["", "", "", ""])
        header_data.append(["", "", "", ""])
        cart = request.session.get("cart", {})
        total_cost = 0
        for item in cart:
            try:
                product = Product.objects.get(id=item)
                product.counter = cart[item]
                data.append(
                    [product.id, product.name, product.counter,
                     "{} $".format(product.price),
                     "{} $".format(product.price * product.counter)])
                total_cost += Decimal(cart[item]) * product.price
            except Product.DoesNotExist:
                continue
        data.append([" ", " ", " ", " ", "{} $".format(total_cost)])
        header = Table(data=header_data, colWidths=[150, 75, 75, 150])
        header.setStyle(tblstyle=header_style)
        t = Table(data=data, colWidths=[150, 150, 50, 50, 50])
        t.setStyle(tblstyle=style)
        elements.append(header)
        elements.append(t)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response, pdf


def generate_text_for_history(items):
    output = []
    overall_price = 0
    for item in items:
        total_price = item.item.price*item.counter
        item_desc = "name:{}, manufacturer:{}, price:{}$, amount:{}, total price:{}$".format(item.item.name,
                                                                                             item.item.manufacturer,
                                                                                             item.item.price,
                                                                                             item.counter,
                                                                                             total_price)
        overall_price += total_price
        output.append(item_desc)
    output.append("overall price: {}$".format(overall_price))
    return " \n".join(output)


class CheckoutPdfView(View):
    def get(self, request):
        anon_email = request.GET.get("anon_mail")
        response, pdf = gen_pdf(request, anon_email)
        if request.user.is_authenticated:
            try:
                user_items = ShoppingCart.objects.filter(owner_id=request.user.id)
                text = generate_text_for_history(user_items)
                HistoryOfPurchases.objects.create(user=request.user, history=text)
                for item in user_items:
                    item.delete()
                email = EmailMessage("Hello, {}!".format(request.user.username), "Here is your checkout pdf!",
                                     to=[request.user.email])
                email.attach('checkout.pdf', pdf, 'application/pdf')
                email.send()
            except IntegrityError:
                HttpResponseRedirect(reverse("home"))
        else:
            email = EmailMessage("Hello, Anon!", "Here is your checkout pdf!",
                                 to=[anon_email])
            email.attach('checkout.pdf', pdf, 'application/pdf')
            email.send()
        return response


class SearchView(View):
    def get(self, request):
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            products = Product.objects.filter(
                reduce(operator.and_, (Q(name__icontains=q) for q in query_list)) |
                reduce(operator.and_, (Q(manufacturer__icontains=q) for q in query_list)) |
                reduce(operator.and_, (Q(description__icontains=q) for q in query_list))
            ).order_by("-views")
        else:
            products = Product.objects.all().order_by("-views")
        paginator = Paginator(products, 10)
        page = request.GET.get('page', 1)
        try:
            prods = paginator.page(page)
        except PageNotAnInteger:
            prods = paginator.page(1)
        except EmptyPage:
            prods = paginator.page(paginator.num_pages)

        page_numbers = gen_page_list(int(page), paginator.num_pages)
        return render(request, "search_template.html", {"products": prods,
                                                        "page_numbers": page_numbers,
                                                        "query": query})
