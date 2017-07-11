# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    age = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    has_verified_mobile = models.BooleanField(default=False)

class UserModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=120)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
