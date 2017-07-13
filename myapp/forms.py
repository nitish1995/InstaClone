from django import forms
from models import UserModel, PostModel

class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email','username','name','password',]

class LogInForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username','password',]

class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image','caption']