from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        labels = {
            "text": "Введите текст",
            "group": "Выберите группу",
            "image": "Загрузите картинку",
        }
        help_texts = {
            "text": "Ваш текст",
            "group": "Необязательное поле",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Напишите комментарий",
        }
        help_texts = {
            "text": "Ваш комментарий",
        }
