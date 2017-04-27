from django import forms

from products.models import Comment


class CommentForm(forms.ModelForm):

    rating = forms.DecimalField(label='Rating (0-10)')
    class Meta:
        model = Comment
        exclude = ('date', 'commenter', 'product', 'edit_date', 'edit_amount')
        widgets = {
            'positive': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'negative': forms.Textarea(attrs={'rows': 4, 'cols': 15}),
            'body': forms.Textarea(attrs={'rows': 8, 'cols': 15}),
        }
