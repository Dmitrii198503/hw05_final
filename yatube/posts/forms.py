from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Defines form of the post"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Defines form of the comment"""
    class Meta:
        model = Comment
        fields = ('text', )
