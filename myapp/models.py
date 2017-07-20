# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import uuid
from django.core.validators import RegexValidator
# Create your models here.

class UserModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=120,)
    username = models.CharField(max_length=120, validators=[RegexValidator(regex='^.{4,}$', message='Usename should be atleast 4 character long.', code='min_length')])
    password = models.CharField(max_length=40, validators=[RegexValidator(regex='^.{5,}$', message='Password should be atleast 6 character long.', code='min_length')])
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class SessionToken(models.Model):
    user = models.ForeignKey(UserModel)
    session_token = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.session_token = uuid.uuid4()

class PostModel(models.Model):
    has_liked = models.BooleanField(default=False)
    user = models.ForeignKey(UserModel)
    image = models.FileField(upload_to = 'user_images')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    dirty = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))

    @property
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('-created_on')

class LikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class CommentModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    comment_text = models.CharField(max_length=500)
    created_on  = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


