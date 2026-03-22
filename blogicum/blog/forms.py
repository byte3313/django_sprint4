from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикации."""

    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'location', 'pub_date', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={
                'rows': 5,
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите заголовок'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст публикации',
            'category': 'Категория',
            'location': 'Местоположение',
            'pub_date': 'Дата и время публикации',
            'image': 'Изображение',
        }
        help_texts = {
            'pub_date': 'Если установить дату и время в будущем — '
                        'можно делать отложенные публикации.',
            'image': 'Загрузите изображение для публикации (опционально)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = False
        self.fields['image'].required = False


class CommentForm(forms.ModelForm):
    """Форма для добавления и редактирования комментария."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Введите ваш комментарий...',
                'class': 'form-control'
            }),
        }
        labels = {
            'text': 'Комментарий',
        }
