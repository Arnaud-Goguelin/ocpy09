import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.models import User

from .form import CustomUserCreationForm


logger = logging.getLogger("authentication")


class CustomLoginView(LoginView):
    template_name = "authentication/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        # it is necessary to overwrite get_success_url in login view as priorité order for this particular view has
        # changed in django
        return reverse_lazy("feed:feed_posts")

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.error(f"Unexpected error in log in. \nError: {form.errors}")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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

        messages.success(self.request, f"Welcome {self.object.username} ! Your account has been created.")
        return response

    def form_invalid(self, form):
        logger.error(f"Unexpected error in sign up. \nError: {form.errors}")
        return super().form_invalid(form)
