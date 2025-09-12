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
    success_url = reverse_lazy("feed:subscriptions")

    def form_valid(self, form):
        user = form.get_user()
        logger.info(f"Connexion réussie pour l'utilisateur: {user.username}")
        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.cleaned_data.get("username", "Inconnu")
        logger.warning(f"Tentative de connexion échouée pour: {username}")
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.debug(f"Utilisateur déjà connecté redirigé: {request.user.username}")
        return super().get(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("authentication:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info(f"Déconnexion de l'utilisateur: {request.user.username}")
        return super().dispatch(request, *args, **kwargs)


class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "authentication/signup.html"
    success_url = reverse_lazy("authentication:login")

    def form_valid(self, form):
        logger.debug(f"Formulaire d'inscription valide pour: {form.cleaned_data.get('username')}")
        response = super().form_valid(form)

        login(self.request, self.object)
        logger.info(f"Inscription et connexion automatique réussies pour: {self.object.username}")

        messages.success(self.request, f"Bienvenue {self.object.username} ! Votre compte a été créé avec succès.")
        return response

    def form_invalid(self, form):
        username = form.cleaned_data.get("username", "Inconnu")
        logger.warning(f"Échec de l'inscription pour: {username}. Erreurs: {form.errors}")
        return super().form_invalid(form)
