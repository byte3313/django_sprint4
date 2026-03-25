from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'
    verbose_name = _('Блог')

    def ready(self):
        try:
            from django.db.utils import OperationalError, ProgrammingError
            from .models import Category

            if not Category.objects.filter(slug='uncategorized').exists():
                Category.objects.create(
                    title='Без категории',
                    slug='uncategorized',
                    description='Категория по умолчанию',
                    is_published=True,
                )
        except (OperationalError, ProgrammingError):
            pass
