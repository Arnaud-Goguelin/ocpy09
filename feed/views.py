import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .form import CreateSubscriptionForm
from .models import Subscription


logger = logging.getLogger("feed")


class SubscriptionLandingView(LoginRequiredMixin, CreateView):
    template_name = "feed/subscription_landing.html"
    model = Subscription
    form_class = CreateSubscriptionForm
    success_url = reverse_lazy("feed:subscriptions")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update(
            {
                "following": user.following.select_related("followed"),
                "followers": user.followers.select_related("follower"),
            }
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, f"You now follow {form.cleaned_data['username']} !")
        logger.info(f"Attempt successful from {self.request.user.username} to follow {form.cleaned_data['username']}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Attempt from {self.request.user.username} to follow {form.cleaned_data['username']} failed.")
        return super().form_invalid(form)
