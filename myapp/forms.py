from django import forms
from models import CommentModel,UserModel, PostModel, LikeModel

class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email','username','name','password',]
        error_messages = {'username':{'required':'Please let us know what to call you.'},'name':{'required':'Name is required.'},
                          'email': {'required': 'Please provide your mail id.'},'password':{'required':'Password can not be left blank.'}}

class LogInForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username','password',]
        error_messages = {'username': {'required': 'Username can not be left blank.'},
                          'password': {'required': 'Password can not be left blank.'}}

class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image','caption']

class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['post','comment_text']