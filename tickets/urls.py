from django.urls import path

from . import views


app_name = "tickets"

urlpatterns = [
    path("<int:primary_key>/", views.TicketDetailView.as_view(), name="detail"),
    path("create/", views.TicketCreateView.as_view(), name="create"),
    path("create_with_review/", views.TicketReviewCreateView.as_view(), name="create_with_review"),
    path("<int:primary_key>/edit/", views.TicketUpdateView.as_view(), name="edit"),
    path("<int:primary_key>/delete/", views.TicketDeleteView.as_view(), name="delete"),
]
