from django.urls import path

from . import views


app_name = "tickets"

urlpatterns = [
    path("<int:pk>/", views.TicketDetailView.as_view(), name="detail"),
    path("create/", views.TicketCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.TicketUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.TicketDeleteView.as_view(), name="delete"),
    path("create_with_review/", views.TicketReviewCreateView.as_view(), name="create_with_review"),
    path("update_with_review/", views.TicketReviewUpdateView.as_view(), name="edit_with_review"),
]
