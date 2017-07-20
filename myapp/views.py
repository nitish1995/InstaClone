# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from project_sb.settings import BASE_DIR
from imgurpython import ImgurClient
from imgurkey import client_id,client_secret,sendgrid_key, cloudapi_key,cloudapi_secret, clari_key
from django.shortcuts import render, redirect
from forms import SignUpForm, LogInForm, PostForm, LikeForm, CommentForm
from models import CommentModel,UserModel, SessionToken, PostModel, LikeModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
import sendgrid
import cloudinary.uploader
import cloudinary.api
from clarifai.rest import ClarifaiApp
import pdb

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

dirty = ['GARBAGE','POLLUTION','WASTE','TRASH','LITTER']


# Create your views here.

app = ClarifaiApp(api_key=clari_key)
model = app.models.get('general-v1.3')

cloudinary.config(
  cloud_name = "instaclonecloud",
  api_key = cloudapi_key,
  api_secret = cloudapi_secret
)



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


            subject = "Welcome to Swach Bharat"
            from_email = "chauhannitish1995@gmail.com"
            from_name = "Nitish Chauhan"
            message = "Your account is successfully created."
            my_client = sendgrid.SendGridAPIClient(apikey=sendgrid_key)
            payload = {
                "personalizations":[{
                    "to":[{"email":email }],
                    "subject": subject
                }],
                "from": {
                    "email": from_email,
                    "name": from_name
                },
                "content": [{
                    "type":"text/html",
                    "value": message
                }]
            }
            response = my_client.client.mail.send.post(request_body=payload)


            return redirect('/login/')
        else:
            errors = form.errors
            return render(request, 'index.html', {'form': form, 'errors':errors})

    elif request.method == 'GET':
        form = SignUpForm()

    return render(request, 'index.html', {'form': form})





def login_view(request):
    getform = LogInForm()
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
                    message = "Wrong Password."
                    return render(request, 'login.html', {'form':getform,"login_error":message})
            else:
                message = "User does not exist."
                return render(request, 'login.html', {'form':getform,"login_error":message})
        else:
            errors = form.errors
            return render(request, 'login.html', {'form':getform,"errors":errors})


    return render(request, 'login.html', {'form': getform})





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
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(image=image, caption=caption, user=user)
                post.save()

                client = ImgurClient(client_id, client_secret)
                path = str(BASE_DIR + '/' + post.image.url)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                #path = str(BASE_DIR + '/' + post.image.url)
                #upload = cloudinary.uploader.upload(path)
                #pdb.set_trace()
                #post.image_url = upload['url']
                #post.save()

                response = model.predict_by_url(post.image_url)
                response = response['outputs'][0]['data']['concepts']
                is_dirty = False
                for word in dirty:
                    for imgword in response:
                        image_word = imgword['name']
                        image_word = image_word.upper()
                        if image_word == word:
                            is_dirty = True
                            break

                if is_dirty:
                    post.dirty = True
                    post.save()

                return redirect('/feed/')
        else:
            form = PostForm()
            return render(request, 'post.html', {'form': form})

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


def logout_view(request):
    response = redirect('/signup/')
    response.delete_cookie('session_token')
    return response


def user_view(request):
    username = request.GET.get('q', '')
    user = UserModel.objects.filter(username = username).first()
    if user:
        posts = PostModel.objects.filter(user=user)
        if posts:
            return render(request, 'oneuser.html', {'posts':posts})

    return redirect('/signup/')