from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .models import User


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Bob", "id": "id_username_signup"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "complicated_secret_password", "id": "id_password_signup_1"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-input", "placeholder": "complicated_secret_password", "id": "id_password_signup_2"}
        )
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tickets:list")


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("authentication:login")


class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "authentication/signup.html"
    success_url = reverse_lazy("authentication:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
