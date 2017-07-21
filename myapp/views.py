# -*- coding: utf-8 -*-


from __future__ import unicode_literals
from project_sb.settings import BASE_DIR
from imgurpython import ImgurClient
from imgurkey import client_id,client_secret,sendgrid_key, cloudapi_key,cloudapi_secret, clari_key
from django.shortcuts import render, redirect
from forms import SignUpForm, LogInForm, PostForm, LikeForm, CommentForm, UpvoteForm
from models import CommentModel,UserModel, SessionToken, PostModel, LikeModel, UpvoteModel
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
import sendgrid
import cloudinary.uploader
import cloudinary.api
from clarifai.rest import ClarifaiApp



#list for clean image classifiaction.
dirty = ['GARBAGE','POLLUTION','WASTE','TRASH','LITTER']


# Create your views here.
#clarifai and cloudinary setup..........................................................................................
#.......................................................................................................................
app = ClarifaiApp(api_key=clari_key)
model = app.models.get('general-v1.3')

cloudinary.config(
  cloud_name = "instaclonecloud",
  api_key = cloudapi_key,
  api_secret = cloudapi_secret
)
#.......................................................................................................................



                                ###############SIGNUP VIEW##########



#method for signup template.............................................................................................
#.......................................................................................................................
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            #fetchin the signup form....................................................................................
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password'])
            user = UserModel(name = name, email = email, password = password, username = username)
            user.save()

            #sending user a welcome mail................................................................................
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

            #redirecting user accordingly...............................................................................
            return redirect('/login/')

        #handling form error and get request............................................................................
        else:
            errors = form.errors
            return render(request, 'index.html', {'form': form, 'errors':errors})

    elif request.method == 'GET':
        form = SignUpForm()

    return render(request, 'index.html', {'form': form})
#.......................................................................................................................



                                #########LOGIN_VIEW#########



#method for login template..............................................................................................
#.......................................................................................................................
def login_view(request):
    getform = LogInForm()
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            #fetching the form details..................................................................................
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = UserModel.objects.filter(username = username).first()
            if user:
                #authenticating user and creating session...............................................................
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
        #handling form error............................................................................................
        else:
            errors = form.errors
            return render(request, 'login.html', {'form':getform,"errors":errors})


    return render(request, 'login.html', {'form': getform})
#.......................................................................................................................



                                    ########FEED_VIEW############



#method for feedview....................................................................................................
#.......................................................................................................................
def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all()
        if len(posts) > 0:
            #setting has_liked value for all posts for current user.....................................................
            posts = posts.order_by('-created_on')
            for post in posts:
                existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
                if existing_like:
                    post.has_liked = True

            #setting has_upvote value in comment model for current user.................................................
            comments = CommentModel.objects.all()
            if len(comments) > 0:
                for comment in comments:
                    existing_vote = UpvoteModel.objects.filter(comment_id = comment.id, user =user).first()
                    if existing_vote:
                        comment.has_upvote = True

            #rendering the feed page with posts.........................................................................
            return render(request, 'feed.html', {'posts' : posts,'comments':comments})
        else:
            return render(request, 'feed1.html')
    #if user is not logged in...........................................................................................
    else:
        return redirect('/login/')
#.......................................................................................................................



                                ##########CHECK_VALIDATION##########



#method for checking validation or session for user.....................................................................
#.......................................................................................................................
def check_validation(request):
    if request.COOKIES.get('session_token'):
        #filtering session model entries with cookies details...........................................................
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            #allowing for only one day..................................................................................
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None
#.......................................................................................................................



                                ##############POST_VIEW##################



#method for post template...............................................................................................
#.......................................................................................................................
def post_view(request):
    user = check_validation(request)
    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            #fetching image and caption from the form...................................................................
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(image=image, caption=caption, user=user)
                post.save()

                #uploading image on imgur cloud.........................................................................
                client = ImgurClient(client_id, client_secret)
                path = str(BASE_DIR + '/' + post.image.url)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                #uploding image on cloudinary cloud.....................................................................
                #path = str(BASE_DIR + '/' + post.image.url)
                #upload = cloudinary.uploader.upload(path)
                #pdb.set_trace()
                #post.image_url = upload['url']
                #post.save()

                #doing the image analysis with the clarifai api.........................................................
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

                #redirecting again to feed..............................................................................
                return redirect('/feed/')
        #handling get request...........................................................................................
        else:
            form = PostForm()
            return render(request, 'post.html', {'form': form})
    #if user is not logged in...........................................................................................
    else:
        return redirect('/login/')
#.......................................................................................................................



                        #############LIKE_VIEW###############



#like_view method for like button no template...........................................................................
#.......................................................................................................................
def like_view(request):
    user = check_validation(request)
    if user and request.method == "POST":
        form = LikeForm(request.POST)
        if form.is_valid():
            #fetching like or unlike....................................................................................
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            #checking for like or unlike................................................................................
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
            else:
                existing_like.delete()
            #redirecting again to feed view.............................................................................
            return redirect('/feed/')
        else:
            return render(request, 'feed1.html')
    else:
        return redirect('/login/')
#.......................................................................................................................



                            ############UPVOTE_VIEW###############



#method for upvoting a comment notemplate...............................................................................
#.......................................................................................................................
def upvote_view(request):
    user = check_validation(request)
    if user and request.method == "POST":
        form = UpvoteForm(request.POST)
        if form.is_valid():
            #fetching upvote ordownvote.................................................................................
            comment_id = form.cleaned_data.get('comment').id
            existing_vote = UpvoteModel.objects.filter(comment_id = comment_id, user=user).first()
            #checking forupvote or downvote.............................................................................
            if not existing_vote:
                UpvoteModel.objects.create(comment_id = comment_id, user=user)
            else:
                existing_vote.delete()

            #redirecting again to the feed view.........................................................................
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/signup/')
#.......................................................................................................................



                            ##############COMMENT_VIEW#############



#method for comment updation no unique template.........................................................................
#.......................................................................................................................
def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            #fetching comment text and post.............................................................................
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            #after saving comment again redirecting to feed view........................................................
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    #if user is not logged in...........................................................................................
    else:
        return redirect('/login/')
#.......................................................................................................................



                                   ##########LOGOUT#########



#method for logout button in feed view..................................................................................
#.......................................................................................................................
def logout_view(request):
    response = redirect('/signup/')
    #deleting cookies forcurrent user...................................................................................
    response.delete_cookie('session_token')
    return response
#.......................................................................................................................



                                 ########USER_VIEW############
                            #(http://127.0.0.1:8000/user/?q=name1)#
                            #(http://127.0.0.1:8000/user/?q=name2)#
                            #(http://127.0.0.1:8000/user/?q=name3)#



#method for accepting query in url for a specific user..................................................................
#.......................................................................................................................
def user_view(request):
    #fetching the query from url........................................................................................
    username = request.GET.get('q', '')
    #finding user indatabase............................................................................................
    user = UserModel.objects.filter(username = username).first()
    if user:
        #fetching post posted onlyby this user..........................................................................
        posts = PostModel.objects.filter(user=user)
        if posts:
            return render(request, 'oneuser.html', {'posts':posts})

    return redirect('/signup/')
#.......................................................................................................................