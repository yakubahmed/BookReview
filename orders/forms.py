from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpFormt(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True,  widget=forms.TextInput(attrs={'class':'form-control','placeholder':'your first namr'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'yout last name'}))
    email = forms.EmailField(max_length=254, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email address'}))
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'USername'}))
    password1 = forms.CharField(max_length=254, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(max_length=254, widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm password'}))
    

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
