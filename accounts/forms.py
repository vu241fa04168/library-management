from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'you@example.com',
            'required': 'required',
            'id': 'email',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply standard autocomplete and id fields to standard UserCreationForm inputs
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({
                'autocomplete': 'username',
                'placeholder': 'Choose a username',
                'id': 'username',
            })
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'autocomplete': 'new-password',
                'placeholder': 'Create a password',
                'id': 'new-password',
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'autocomplete': 'new-password',
                'placeholder': 'Confirm your password',
                'id': 'confirm-password',
            })


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'autocomplete': 'username',
            'placeholder': 'Enter your username',
            'required': 'required',
            'id': 'username',
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Enter your password',
            'required': 'required',
            'id': 'current-password',
        })
    )
