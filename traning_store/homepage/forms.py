from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={"rows": 5, "cols": 20})
        }
