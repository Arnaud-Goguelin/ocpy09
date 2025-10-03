from django.urls import path

from . import views


app_name = "reviews"

urlpatterns = [
    path("create/<int:ticket_id>/", views.ReviewCreateView.as_view(), name="create"),
    path("<int:primary_key>/edit/", views.ReviewUpdateView.as_view(), name="edit"),
    path("<int:primary_key>/delete/", views.ReviewDeleteView.as_view(), name="delete"),
]
