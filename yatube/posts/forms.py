from .models import Post, Comment
from django import forms


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        help_texts = {
            'text': ('Введите текст'),
            'group': ('Выберите группу для поста'),
            'image': ('Загрузите изображение')
        }
        labels = {
            'text': ('Текст поста'),
            'group': ('Группа поста'),
            'image': ('Изображение для поста')
        }
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if data == '':
            raise forms.ValidationError('Введите текст')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        help_texts = {
            'text': ('Введите текст')
        }
        labels = {
            'text': ('Текст комментария')
        }
        fields = ('text',)
