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
                "placeholder": "Your pseudo",
                "id": "id_username_signup",
            }
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "long password with multiples characters",
                "id": "id_password_signup_1",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "repeat the password",
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
            raise forms.ValidationError("This user name already exists.")

        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The passwords don't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=commit)
        return user
