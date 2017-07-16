# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from imgurpython import ImgurClient
from project_sb.settings import BASE_DIR
from imgurkey import client_id,client_secret
from django.shortcuts import render, redirect
from forms import SignUpForm, LogInForm, PostForm, LikeForm, CommentForm
from models import CommentModel,UserModel, SessionToken, PostModel, LikeModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
# Create your views here.

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            user = UserModel(name = name, email = email, password = password, username = username)
            user.save()
            return redirect('/login/')
        else:
            return render(request, 'feed1.html')

    elif request.method == 'GET':
        form = SignUpForm()

    return render(request, 'index.html', {'form': form})





def login_view(request):
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = UserModel.objects.filter(username = username).first()
            if user:
                if check_password(password,user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()

                    response = redirect('feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    print "Invalid User"

    elif request.method == "GET":
        form = LogInForm()
    return render(request, 'login.html', {'form': form})





def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all()
        if len(posts) > 0:
            posts = posts.order_by('-created_on')
            for post in posts:
                existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
                if existing_like:
                    post.has_liked = True
            return render(request, 'feed.html', {'posts' : posts})
        else:
            return render(request, 'feed1.html')

    else:
        return redirect('/login/')




def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None




def post_view(request):
    user = check_validation(request)
    if user:
        if request.method == 'GET':
            form = PostForm()
            return render(request, 'post.html', {'form' : form})

        elif request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(image=image, caption=caption, user=user)
                post.save()

                client = ImgurClient(client_id, client_secret)
                path = str(BASE_DIR +'/'+ post.image.url)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                return redirect('/feed/')

    else:
        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == "POST":
        form = LikeForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()

            return redirect('/feed/')
        else:
            return render(request, 'feed1.html')
    else:
        return redirect('/login/')

def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            return redirect('/feed/')
        else:
            return redirect('/feed/')
        pass
    else:
        return redirect('/login/')