from django.urls import path

from . import views


app_name = "feed"

urlpatterns = [
    path("subscription/", views.SubscriptionLandingView.as_view(), name="subscriptions"),
    path("user_posts/", views.UserPostsView.as_view(), name="user_posts"),
    path("", views.FeedPostsView.as_view(), name="feed_posts")
]
