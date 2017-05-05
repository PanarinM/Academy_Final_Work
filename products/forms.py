from django import forms

from products.models import Comment, ShoppingCart


class CommentForm(forms.ModelForm):

    rating = forms.DecimalField(label="Rating (0-10)")

    class Meta:
        model = Comment
        exclude = ("date", "author", "product", "edit_date", "edit_amount")
        widgets = {
            "positive": forms.Textarea(attrs={"rows": 4, "cols": 15}),
            "negative": forms.Textarea(attrs={"rows": 4, "cols": 15}),
            "body": forms.Textarea(attrs={"rows": 8, "cols": 15}),
        }


class AddToCartForm(forms.ModelForm):

    class Meta:
        model = ShoppingCart
        exclude = ("owner", "item")
        widgets = {
            "counter": forms.TextInput(attrs={"size": "1"}),
        }
