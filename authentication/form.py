import logging

from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


logger = logging.getLogger("authentication")


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

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if User.objects.filter(username=username).exists():
            logger.warning(f"Attemps to create a new account with an existing username: {username}")
            raise forms.ValidationError("This user name already exists.")

        logger.info(f"Username validated in signup for: {username}")
        return username

    def clean_password2(self):
        password2 = super().clean_password2()
        username = self.cleaned_data.get("username")
        if username:
            logger.debug(f"Validate password for {username}")
        return password2

    def save(self, commit=True):
        user = super().save(commit=commit)
        logger.info(f"New user created: {user.username}")
        return user
