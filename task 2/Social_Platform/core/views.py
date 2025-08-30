from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Post, Comment, Like, Follow, Profile
from django.utils import timezone

def index(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('feed')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        login(request, user)
        return redirect('feed')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def feed_view(request):
    # Get posts from users that the current user follows
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(user__in=following_users).order_by('-created_at')
    
    # Also include user's own posts
    user_posts = Post.objects.filter(user=request.user)
    posts = (posts | user_posts).distinct().order_by('-created_at')
    
    return render(request, 'feed.html', {'posts': posts})

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    
    return render(request, 'profile.html', {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Post.objects.create(user=request.user, content=content)
            messages.success(request, 'Post created successfully!')
        return redirect('feed')
    return redirect('feed')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        post.likes_count -= 1
        liked = False
    else:
        post.likes_count += 1
        liked = True
    
    post.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes_count
        })
    
    return redirect('feed')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            messages.success(request, 'Comment added successfully!')
    return redirect('feed')

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        messages.error(request, 'You cannot follow yourself')
        return redirect('profile', username=username)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        follow.delete()
        followed = False
        messages.info(request, f'Unfollowed {username}')
    else:
        followed = True
        messages.success(request, f'Now following {username}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'followed': followed})
    
    return redirect('profile', username=username)
