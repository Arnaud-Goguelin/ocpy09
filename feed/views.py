import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView

from reviews.models import Review
from tickets.models import Ticket

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
        messages.success(self.request, f"{self.request.user.username} now follow {form.cleaned_data['username']} !")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.error(f"Attempt from {self.request.user.username} to follow {form.data['username']} failed.")
        return super().form_invalid(form)


class SubscriptionDeleteView(LoginRequiredMixin, DeleteView):
    """
    View used to unsubscribe (delete a Subscription).
    Only allows deletion of subscriptions where the current user is the follower.
    """

    model = Subscription
    success_url = reverse_lazy("feed:subscriptions")

    def get_queryset(self):
        # Restrict deletion to the subscriptions of the logged-in user
        return Subscription.objects.filter(follower=self.request.user)

    def delete(self, request, *args, **kwargs):
        subscription = self.get_object()
        username = subscription.followed.username
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"You no longer follow {username}.")
        return response


class UserPostsView(LoginRequiredMixin, ListView):
    template_name = "feed/user_posts.html"
    context_object_name = "posts"
    # pagination won't work because of merging 2 queryset with not same attributes
    # normalize them (create a dict) would be too complex as we would loose relationship between objects

    def get_queryset(self):
        current_user = self.request.user

        user_reviews = Review.objects.filter(user=current_user).select_related("ticket", "user")
        user_tickets = Ticket.objects.filter(user=current_user).select_related("user").prefetch_related("review")

        posts = sorted([*user_reviews, *user_tickets], key=lambda x: x.time_created, reverse=True)

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class FeedPostsView(LoginRequiredMixin, ListView):
    template_name = "feed/feed_posts.html"
    context_object_name = "posts"
    # pagination won't work because of merging 2 queryset with not same attributes
    # normalize them (create a dict) would be too complex as we would loose relationship between objects

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
            .prefetch_related("review")
        )

        # Reviews in response to current user's tickets (even if reviewer is not followed)
        reviews_on_current_user_tickets = (
            Review.objects.filter(ticket__user=current_user)
            .exclude(user_id__in=users_ids_to_get_posts_from)  # Exclude already fetched reviews
            .select_related("ticket", "user")
        )

        posts = sorted(
            [*reviews_on_current_user_tickets, *followed_users_reviews, *followed_users_tickets],
            key=lambda x: x.time_created,
            reverse=True,
        )

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
