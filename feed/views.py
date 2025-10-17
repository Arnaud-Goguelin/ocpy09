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
        messages.success(self.request, f"{self.request.user.username} now follow {form.cleaned_data['username']} !")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.error(f"Attempt from {self.request.user.username} to follow {form.data['username']} failed.")
        return super().form_invalid(form)


class UserPostsView(LoginRequiredMixin, ListView):
    template_name = "feed/user_posts.html"
    context_object_name = "posts"
    # TODO: pagination won't work because of merging 2 queries, we may limit the list
    # TODO: add update button in template
    paginate_by = 10

    def get_queryset(self):
        current_user = self.request.user

        user_reviews = Review.objects.filter(user=current_user).select_related("ticket", "user")
        user_tickets = Ticket.objects.filter(user=current_user).select_related("user").prefetch_related("reviews")

        posts = sorted([*user_reviews, *user_tickets], key=lambda x: x.time_created, reverse=True)

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class FeedPostsView(LoginRequiredMixin, ListView):
    template_name = "feed/feed_posts.html"
    context_object_name = "posts"
    # TODO: pagination won't work because of merging 2 queries, we may limit the list
    paginate_by = 10

    def get_queryset(self):
        current_user = self.request.user

        users_ids_followed_by_current_user = Subscription.objects.filter(follower=current_user).values_list(
            "followed_id",
            flat=True,  # avoid a list of tuples, result will be a list of ids
        )

        users_ids_to_get_posts_from = [current_user.id, *users_ids_followed_by_current_user]

        # select_related() (relation one to one) and prefetch_related() (relation many to many) are used to avoid
        # multiple queries
        followed_users_reviews = Review.objects.filter(user_id__in=users_ids_to_get_posts_from).select_related(
            "ticket", "user"
        )
        followed_users_tickets = (
            Ticket.objects.filter(user_id__in=users_ids_to_get_posts_from)
            .select_related("user")
            .prefetch_related("reviews")
        )

        posts = sorted([*followed_users_reviews, *followed_users_tickets], key=lambda x: x.time_created, reverse=True)

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
