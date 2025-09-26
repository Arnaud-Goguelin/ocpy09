from django.urls import path

from . import views


app_name = "feed"

urlpatterns = [
    path("subscriptions/", views.SubscriptionLandingView.as_view(), name="subscriptions"),
]
