# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from datetime import datetime
from myapp.forms import SignUpForm

# Create your views here.

def signup_view(request):
    if request.method == "GET":
        signup_form = SignUpForm()
        return render(request, 'index.html', {'signup_form': signup_form})