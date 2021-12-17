from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


# Главная страница.

def paginator(request, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists
        context['following'] = following
        return render(request, template, context)
    # Здесь код запроса к модели и создание словаря контекста
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    # Здесь код запроса к модели и создание словаря контекста
    posts = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = posts.comments.all()
    context = {
        'posts': posts,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        return render(request, template, {'form': form})
    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    posts = get_object_or_404(Post, id=post_id)
    if request.user != posts.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=posts)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'is_edit': True,
        'form': form
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        if not Follow.objects.filter(author=author,
                                     user=request.user).exists():
            Follow.objects.create(author_id=author.id, user_id=request.user.id)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
