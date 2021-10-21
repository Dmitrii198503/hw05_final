from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Group, Follow
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required


User = get_user_model()


def group_posts(request, slug):
    """Shows posts upon request by group"""
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'group': group,
               'page_obj': page_obj, }
    return render(request, template, context)


def index(request):
    """Shows 10 posts by publication date order"""
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    """Shows current author posts"""
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.all()
    count_posts = posts_list.count()
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = author.following.exists()
    context = {
        'author': author,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Shows post details"""
    post = get_object_or_404(Post, pk=post_id)
    chars_10 = post.text[:10]
    pub_date = post.pub_date
    posts_list = post.author.posts.all()
    count_posts = posts_list.count()
    comments_list = post.comments.all()
    paginator = Paginator(comments_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = CommentForm()
    context = {
        'chars_10': chars_10,
        'pub_date': pub_date,
        'post': post,
        'count_posts': count_posts,
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Creates new post"""
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Changes post"""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'GET' and request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request,
                  'posts/create_post.html',
                  {'form': form, 'post': post, "is_edit": 'is_edit'})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    authors_posts_list = Post.objects.filter(author__in=authors)
    paginator = Paginator(authors_posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    Follow.objects.get(user=user, author=author).delete()
    return redirect('posts:profile', username)
