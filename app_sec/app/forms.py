from django import forms

from app import models


class LoginForm(forms.Form):
    username = forms.CharField(label='Your Name', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))

    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))


class CreateAccountForm(forms.Form):
    username = forms.CharField(label='Your Name', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
    repeat_password = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))


class WikiForm(forms.Form):
    title = forms.CharField(label="Title", max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
    img_url = forms.URLField(label="Image URL", max_length=500, widget=forms.TextInput(
        attrs={'class': 'form-control form-field not-mucha-area'},
    ), validators=[models.img_validator])
    content = forms.CharField(label="Content", widget=forms.Textarea(
        attrs={'class': 'form-control form-field mucha-area'}
    ))


class CommentForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea(
        attrs={'class': 'form-control form-field mucha-area'}
    ))


class ChangePasswordForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
    repeat_password = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(
        attrs={'class': 'form-control form-field not-mucha-area'}
    ))
