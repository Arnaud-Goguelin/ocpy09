from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import User


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('tickets:list')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('authentication:login')


class SignUpView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'authentication/signup.html'
    success_url = reverse_lazy('authentication:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return redirect('tickets:list')
