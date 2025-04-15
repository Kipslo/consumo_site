from django.contrib.auth.models import User
from django import forms

class LoginForm(forms.Form):
    usuário = forms.CharField(max_length=30)
    senha = forms.CharField(max_length=30, widget=forms.PasswordInput())