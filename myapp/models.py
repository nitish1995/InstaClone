# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import uuid
from django.core.validators import RegexValidator
# Create your models here.

#usermodel for storing user details.....................................................................................
class UserModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=120,)
    username = models.CharField(max_length=120, validators=[RegexValidator(regex='^.{4,}$',
                            message='Usename should be atleast 4 character long.', code='min_length')])
    password = models.CharField(max_length=40, validators=[RegexValidator(regex='^.{5,}$',
                            message='Password should be atleast 6 character long.', code='min_length')])
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
#.......................................................................................................................




#session model for creating session for user............................................................................
class SessionToken(models.Model):
    user = models.ForeignKey(UserModel)
    session_token = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    #creating a unique token.
    def create_token(self):
        self.session_token = uuid.uuid4()
#.......................................................................................................................




#postmodel for storing image caption and other post details.............................................................
class PostModel(models.Model):
    has_liked = models.BooleanField(default=False)
    user = models.ForeignKey(UserModel)
    image = models.FileField(upload_to = 'user_images')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    dirty = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    #for counting the number of like on specific post.
    @property
    def like_count(self):
        return len(LikeModel.objects.filter(post=self))
    #for fetching comments for specific post.
    @property
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('-created_on')
#.......................................................................................................................




#like model for storing like information................................................................................
class LikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
#.......................................................................................................................




#Comment model for storing comment details..............................................................................
class CommentModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    has_upvote = models.BooleanField(default=False)
    comment_text = models.CharField(max_length=500)
    created_on  = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
#.......................................................................................................................




#Upvote model for storing upvote detail on every comment................................................................
class UpvoteModel(models.Model):
    user = models.ForeignKey(UserModel)
    comment = models.ForeignKey(CommentModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    #counting vote for a specific comment
    @property
    def vote_count(self):
        return len(UpvoteModel.objects.filter(comment=self))
#.......................................................................................................................

