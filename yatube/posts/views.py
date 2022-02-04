from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from .models import Post, Group, User, Follow
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm


def index(request):
    # page: int = 10
    template = 'posts/index.html'
    title = 'Yatube:  Лев Толстой и все все все'
    posts = Post.objects.select_related('group').all()  # [:page]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    # SHOW_POST: int = 10
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()  # [:SHOW_POST]
    template = 'posts/group_list.html'
    title = 'Yatube-сообщества'
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)

    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе

    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    #
    # А теперь мы можем достать посты группы через related field,
    # зачем ж нам делать доп запрос
    # posts = group.posts.all()[:SHOW_POST] - мое видение


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    title = 'Профайл пользователя ' + username
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    posts_count = posts.count()
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and \
        Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'posts_count': posts_count,
        'posts': posts,
        'title': title,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post = get_object_or_404(Post, id=post_id)
    # Возвращает определённый объект из модели в зависимости
    # от значения его первичного ключа, или выбрасывает исключение Http404,
    # если данной записи не существует.
    # В нашем случае модель Post возвращает конкрутную строку из БД по id поста
    post_num = Post.objects.select_related('author').filter(author=post.author)
    count_post = post_num.count()
    template = 'posts/post_detail.html'
    title = f'Пост {post_id} {post}'
    form = CommentForm()
    # нужно добавить комментарий, относящийся к конкретному посту
    comments = post.comments.all()
    context = {
        'title': title,
        'post': post,
        'post_list': post_num,
        'count_post': count_post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    tamplate = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, tamplate, {'form': form})


@login_required
def post_edit(request, post_id):
    tamplate = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, tamplate, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    template = 'posts/comments.html'
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post': post
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    template = 'posts/follow.html'
    title = 'Посты от подписанных пользователей'
    posts = Post.objects.select_related('author').filter(
        author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'title': title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    follower = Follow.objects.filter(
        user=request.user,
        author=author
    ).exists()
    if follower is True:
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=username)
    following = get_object_or_404(Follow, user=request.user, author=author)
    following.delete()
    return redirect('posts:profile', username=username)
