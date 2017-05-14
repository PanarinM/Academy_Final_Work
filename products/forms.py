from django import forms

from django.core.exceptions import ValidationError

from products.models import Comment

def validate_positive(value):
    if value < 0:
        raise ValidationError('%(value)s is not positive!', params={'value': value})

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


class AddToCartForm(forms.Form):
    counter = forms.IntegerField(widget=forms.NumberInput, label="Amount", validators=[validate_positive])
