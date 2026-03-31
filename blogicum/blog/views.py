from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.http import Http404
from django.db.models import Count, Q
from django.urls import reverse
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def _paginate_queryset(request, queryset, per_page=None):
    """Возвращает страницу объектов с пагинацией."""
    if per_page is None:
        per_page = settings.POSTS_PER_PAGE
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Главная страница со списком публикаций."""
    post_list = Post.objects.published().select_related(
        'author', 'category', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    # Поиск по заголовку и тексту
    search_query = request.GET.get('q', '').strip()
    if search_query:
        post_list = post_list.filter(
            Q(title__icontains=search_query) | Q(text__icontains=search_query)
        )

    page_obj = _paginate_queryset(request, post_list)
    return render(request, 'blog/index.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })


def profile(request, username):
    """Страница пользователя со списком его публикаций."""
    author = get_object_or_404(User, username=username)

    post_list = Post.objects.published(request.user).filter(
        author=author
    ).select_related(
        'category', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    # Фильтрация по категориям
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        post_list = post_list.filter(category__slug=category_filter)

    page_obj = _paginate_queryset(request, post_list)

    return render(request, 'blog/profile.html', {
        'profile': author,
        'page_obj': page_obj,
        'category_filter': category_filter
    })


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя."""
    form = UserChangeForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('blog:profile', username=request.user.username)

    return render(
        request, 'blog/user.html', {'form': form, 'profile': request.user}
    )


@login_required
def post_create(request):
    """Создание новой публикации."""
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, 'Публикация успешно создана!')
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})


def post_detail(request, post_id):
    """Страница отдельной публикации с комментариями."""
    post = get_object_or_404(Post, id=post_id)

    if not (
        post.is_published
        and post.category
        and post.category.is_published
        and post.pub_date <= timezone.now()
    ):
        if request.user != post.author:
            raise Http404("Пост не найден")

    comments = post.comments.select_related(
        'author'
    ).all().order_by('created_at')
    comment_form = (
        CommentForm() if request.user.is_authenticated else None
    )

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': comment_form
    })


def post_edit(request, post_id):
    """Редактирование публикации - доступно только авторизованным авторам."""
    if not request.user.is_authenticated:
        return redirect(reverse('login') + '?next=' + request.path)

    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request,
                       'У вас нет прав для редактирования этой публикации.')
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Публикация успешно обновлена!')
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/create.html', {'form': form, 'post': post})


@login_required
def post_delete(request, post_id):
    """Удаление публикации."""
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error(request, 'У вас нет прав для удаления этой публикации.')
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация успешно удалена!')
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html',
                  {'post': post, 'delete_mode': True})


@login_required
def add_comment(request, post_id):
    """Добавление комментария к публикации."""
    post = get_object_or_404(Post, id=post_id)

    if not (
        post.is_published
        and post.category
        and post.category.is_published
        and post.pub_date <= timezone.now()
    ):
        if request.user != post.author:
            messages.error(
                request, 'Невозможно добавить комментарий к этой публикации.')
            return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        messages.success(request, 'Комментарий успешно добавлен!')

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    post = get_object_or_404(Post, id=post_id)

    if comment.author != request.user:
        messages.error(
            request, 'У вас нет прав для редактирования этого комментария.')
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Комментарий успешно обновлен!')
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
        'post': post,
        'post_id': post_id,
        'comment_id': comment_id,
        'delete_mode': False
    })


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    post = get_object_or_404(Post, id=post_id)

    if comment.author != request.user:
        messages.error(
            request, 'У вас нет прав для удаления этого комментария.')
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Комментарий успешно удален!')
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment,
        'post': post,
        'post_id': post_id,
        'comment_id': comment_id,
        'delete_mode': True
    })


def category_posts(request, category_slug):
    """Страница категории со списком публикаций."""
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    post_list = Post.objects.published().filter(
        category=category
    ).select_related(
        'author', 'location'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    # Поиск по заголовку в категории
    search_query = request.GET.get('q', '').strip()
    if search_query:
        post_list = post_list.filter(
            Q(title__icontains=search_query) | Q(text__icontains=search_query)
        )

    page_obj = _paginate_queryset(request, post_list)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
        'search_query': search_query
    })
