import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from reviews.models import Review
from tickets.models import Ticket
from .form import CreateSubscriptionForm
from .models import Subscription


logger = logging.getLogger("feed")


class SubscriptionLandingView(LoginRequiredMixin, CreateView):
    template_name = "feed/subscription_landing.html"
    model = Subscription
    form_class = CreateSubscriptionForm
    success_url = reverse_lazy("subscriptions")

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
        logger.warning(f"Attempt from {self.request.user.username} to follow {form.data['username']} failed.")
        return super().form_invalid(form)


class UserPostsView(LoginRequiredMixin, ListView):
    template_name = "feed/user_posts.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        user_reviews = Review.objects.filter(user=user).select_related('ticket', 'user')
        user_tickets = Ticket.objects.filter(user=user).select_related('user').prefetch_related('reviews')

        posts = sorted(
            [*user_reviews, *user_tickets],
            key=lambda x: x.time_created,
            reverse=True
            )

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
