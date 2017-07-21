from django import forms
from models import CommentModel,UserModel, PostModel, LikeModel, UpvoteModel

#signup form for user basic information....................
class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email','username','name','password',]
        error_messages = {'username':{'required':'Please let us know what to call you.'},'name':{'required':'Name is required.'},
                          'email': {'required': 'Please provide your mail id.'},'password':{'required':'Password can not be left blank.'}}



#login form for ligginf in..................................
class LogInForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username','password',]
        error_messages = {'username': {'required': 'Username can not be left blank.'},
                          'password': {'required': 'Password can not be left blank.'}}



#post form for posting a image.................................
class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image','caption']



#like form for liking a image.....................................
class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']



#upvote form for upvoting a comment................................
class UpvoteForm(forms.ModelForm):
    class Meta:
        model = UpvoteModel
        fields = ['comment']



#comment form for making comment on post...........................
class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['post','comment_text']