# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from forms import SignUpForm, LogInForm
from models import UserModel, SessionToken
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
            return render(request, 'success.html')

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
    return render(request, 'feed.html')



def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None
