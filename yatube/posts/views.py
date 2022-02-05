from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginator_def


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_def(request, posts)
    context = {
        "page_obj": page_obj,
    }

    template = "posts/index.html"
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_def(request, posts)
    context = {
        "group": group,
        "page_obj": page_obj,
    }

    template = "posts/group_list.html"
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        follow = Follow.objects.filter(user=request.user, author=author)
        follow_count = follow.count()
        if follow_count != 0:
            following = True
    posts = author.posts.all()
    page_obj = paginator_def(request, posts)
    context = {
        "author": author,
        "page_obj": page_obj,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts = post.author.posts.all()
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        "post": post,
        "posts_count": posts.count(),
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.save(commit=False)
        form.instance.author = request.user
        form.save()
        return redirect("posts:profile", username=request.user)
    context = {
        "form": form,
        "groups": groups,
    }

    template = "posts/create_post.html"
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    groups = Group.objects.all()
    is_edit = True
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)

    context = {
        "form": form,
        "is_edit": is_edit,
        "groups": groups,
    }

    template = "posts/create_post.html"
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect("posts:post_detail", post_id=post_id)
    comments = Comment.objects.filter(post_id=post_id)
    context = {
        "form": form,
        "comments": comments,
    }

    template = "posts/post_detail.html"
    return render(request, template, context)


@login_required
def follow_index(request):
    following_authors = Follow.objects.filter(user=request.user).values(
        "author"
    )
    posts = Post.objects.filter(author__in=following_authors)
    page_obj = paginator_def(request, posts)
    context = {
        "page_obj": page_obj,
    }
    template = "posts/follow.html"
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    follow_count = follow.count()
    if author != request.user and follow_count == 0:
        Follow.objects.create(user=request.user, author=author)
    return redirect("posts:follow_index")


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:follow_index")
