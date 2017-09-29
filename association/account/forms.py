from django.contrib.auth.forms import UserCreationForm, UsernameField, SetPasswordForm
from django import forms

from .models import User


class CustomUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")
        field_classes = {'username': UsernameField}


class ResendEmailForm(forms.Form):
    email = forms.EmailField(label='Your email address:', max_length=100)


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(label='Your username', max_length=255)
    email = forms.EmailField(label='Your email address', max_length=100)
