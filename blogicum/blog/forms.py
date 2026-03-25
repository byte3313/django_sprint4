from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования публикации."""

    class Meta:
        model = Post
        exclude = ['author', 'is_published', 'created_at']
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
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст публикации',
            'category': 'Категория',
            'location': 'Местоположение',
            'pub_date': 'Дата и время публикации',
            'image': 'Изображение',
            'is_published': 'Опубликовано',
        }
        help_texts = {
            'pub_date': 'Если установить дату и время в будущем — '
                        'можно делать отложенные публикации.',
            'image': 'Загрузите изображение для публикации (опционально)',
            'title': 'Введите заголовок (макс. 256 символов)',
            'text': 'Введите основной текст публикации',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = False
        self.fields['image'].required = False
        self.fields['category'].required = True
        self.fields['category'].queryset = self.fields[
            'category'].queryset.filter(
            is_published=True
        )
        self.fields['location'].queryset = self.fields[
            'location'].queryset.filter(
            is_published=True
        )

    def clean_title(self):
        """Валидация заголовка."""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError(
                'Заголовок не может быть пустым.')
        if len(title) < 3:
            raise ValidationError(
                'Заголовок должен содержать минимум 3 символа.')
        return title

    def clean_text(self):
        """Валидация текста публикации."""
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise ValidationError('Текст публикации не может быть пустым.')
        if len(text) < 10:
            raise ValidationError(
                'Текст должен содержать минимум 10 символов.')
        return text

    def clean_category(self):
        """Валидация категории."""
        category = self.cleaned_data.get('category')
        if category and not category.is_published:
            raise ValidationError('Выбранная категория недоступна.')
        return category

    def clean_location(self):
        """Валидация местоположения."""
        location = self.cleaned_data.get('location')
        if location and not location.is_published:
            raise ValidationError('Выбранное местоположение недоступно.')
        return location


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

    def clean_text(self):
        """Валидация текста комментария."""
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise ValidationError('Комментарий не может быть пустым.')
        if len(text) < 2:
            raise ValidationError(
                'Комментарий должен содержать минимум 2 символа.')
        return text
