from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.models import User

from .form import CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tickets:create")


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
