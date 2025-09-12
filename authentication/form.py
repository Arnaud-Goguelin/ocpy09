from django import forms
from django.contrib.auth.forms import UserCreationForm

from authentication.models import User


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Bob",
                "id": "id_username_signup",
            }
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "mot de passe long et à multiples caractères",
                "id": "id_password_signup_1",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "répéter mot de passe",
                "id": "id_password_signup_2",
            }
        )
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")
