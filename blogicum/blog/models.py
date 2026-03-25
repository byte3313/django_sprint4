from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        _('Опубликовано'),
        default=True,
        help_text=_(
            'Снимите галочку, чтобы скрыть публикацию.'
        )
    )
    created_at = models.DateTimeField(
        _('Добавлено'),
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(
        _('Заголовок'),
        max_length=256
    )
    description = models.TextField(
        _('Описание')
    )
    slug = models.SlugField(
        _('Идентификатор'),
        unique=True,
        help_text=_(
            'Идентификатор страницы для URL; разрешены символы латиницы, '
            'цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        _('Название места'),
        max_length=256
    )

    class Meta:
        verbose_name = _('местоположение')
        verbose_name_plural = _('Местоположения')

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        _('Заголовок'),
        max_length=256
    )
    text = models.TextField(
        _('Текст')
    )
    pub_date = models.DateTimeField(
        _('Дата и время публикации'),
        help_text=_(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор публикации'),
        related_name='posts'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Местоположение'),
        related_name='posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Категория'),
        related_name='posts'
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='posts_images/',
        blank=True,
        null=True,
        help_text=_('Загрузите изображение для публикации')
    )

    class Meta:
        verbose_name = _('публикация')
        verbose_name_plural = _('Публикации')
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.category is None:
            default_cat, _ = Category.objects.get_or_create(
                slug='uncategorized',
                defaults={
                    'title': 'Без категории',
                    'description': 'Категория по умолчанию',
                    'is_published': True,
                }
            )
            self.category = default_cat
        super().save(*args, **kwargs)


class Comment(PublishedModel):
    """Модель комментария к публикации."""

    text = models.TextField(
        _('Текст комментария'),
        help_text=_('Введите текст комментария')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('Автор комментария'),
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Публикация'),
        related_name='comments'
    )

    class Meta:
        verbose_name = _('комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий от {self.author} к "{self.post}"'
