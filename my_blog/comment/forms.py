from django import forms
from .models import Comment


# 评论表单类
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']