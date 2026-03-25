from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Category, Location, Post, Comment

User = get_user_model()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('name',)
    ordering = ('-created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category',
                    'is_published', 'pub_date', 'created_at')
    list_filter = ('is_published', 'pub_date',
                   'created_at', 'category', 'location')
    search_fields = ('title', 'text', 'author__username')
    readonly_fields = ('created_at', 'author')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'text', 'image')
        }),
        ('Параметры публикации', {
            'fields': ('author', 'category', 'location', 'pub_date')
        }),
        ('Статус', {
            'fields': ('is_published', 'created_at')
        }),
    )
    ordering = ('-pub_date',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'post')
    search_fields = ('author__username', 'post__title', 'text')
    readonly_fields = ('created_at', 'author', 'post')
    fieldsets = (
        ('Информация о комментарии', {
            'fields': ('author', 'post', 'text')
        }),
        ('Статус', {
            'fields': ('is_published', 'created_at')
        }),
    )
    ordering = ('-created_at',)
