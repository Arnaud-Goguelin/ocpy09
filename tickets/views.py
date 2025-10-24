from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from reviews.form import ReviewForm
from reviews.models import Review

from .form import CustomTicketForm
from .models import Ticket
from .services import TicketReviewService


class UserTicketMixin:
    """
    Mixin that filters tickets to only show those belonging to the current user.

    This mixin should be used with views that need to ensure users can only
    access their own tickets (UpdateView, DeleteView, etc.)
    """

    def get_queryset(self):
        """Filter queryset to only include tickets owned by the current user."""
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("feed:user_posts")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UserTicketMixin, UpdateView):
    model = Ticket
    template_name = "tickets/ticket_form.html"
    form_class = CustomTicketForm
    context_object_name = "ticket"
    success_url = reverse_lazy("feed:user_posts")


class TicketDeleteView(LoginRequiredMixin, UserTicketMixin, DeleteView):
    model = Ticket
    template_name = "tickets/ticket_confirm_delete.html"
    context_object_name = "ticket"
    success_url = reverse_lazy("feed:user_posts")


class TicketReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Represents a view for creating a ticket along with an associated review. This view
    is restricted to authenticated users and provides functionality to handle form
    validation, submission, and context preparation necessary for creating both a
    ticket and its review efficiently.

    This class uses a ReviewFormSet for managing review forms and interacts with
    the TicketReviewService to execute the creation process.
    """

    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_review_form.html"
    success_url = reverse_lazy("feed:user_posts")

    def __init__(self, **kwargs):
        # init formset
        super().__init__(**kwargs)
        self.ReviewFormSet = TicketReviewService.review_formset(nb_of_empty_form=1)

    def get_context_data(self, **kwargs):
        """
        Get the context data for the view and update it on whether there is
        POST request or a GET request, and set the ReviewFormSet accordingly.
        """
        context = super().get_context_data(**kwargs)
        return TicketReviewService.prepare_context(context, self.ReviewFormSet, "Create Ticket with Review",
                                                   self.request, self.object)

    def form_valid(self, form):
        """
        Handles the form validation and submission process for creating a ticket and its
        associated review.
        """

        # Do not fetch review_formset from context here as in context
        # self.object (Ticket instance) is None, it is not created yet.
        # Moreover transaction.atomic context below will ensure it is not created in case or error.
        # Thus instanciate review_formset here with instance=None is more explicit and comprehensive.
        review_formset = self.ReviewFormSet(self.request.POST, instance=None)

        success, ticket, errors = TicketReviewService.create_ticket_with_review(
            form, review_formset, self.request.user
            )

        if success:
            self.object = ticket
            # reminder: parent form_valid method return success message and redirect to success_url
            messages.success(
                self.request,
                f'Ticket "{ticket.title}" and its review created successfully.'
            )
            return super().form_valid(form)
        else:
            # Add service errors to form
            for error in errors:
                messages.error(self.request, error)
            return super().form_invalid(form)


class TicketReviewUpdateView(LoginRequiredMixin, UserTicketMixin, UpdateView):
    """
    The TicketReviewUpdateView class allows updating a Ticket and its associated Review through
    a web form.
    """

    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_review_form.html"
    success_url = reverse_lazy("feed:user_posts")
    context_object_name = "ticket"

    def __init__(self, **kwargs):
        # init formset
        super().__init__(**kwargs)
        # no need of empty form in update mode
        self.ReviewFormSet = TicketReviewService.review_formset(nb_of_empty_form=0)


    def get_context_data(self, **kwargs):
        """
        Get the context data for the view and update it based on whether there is
        POST request or a GET request, and set the ReviewFormSet accordingly.
        """
        context = super().get_context_data(**kwargs)
        return TicketReviewService.prepare_context(context, self.ReviewFormSet, "Update Ticket with Review", self.object)

    def form_valid(self, form):
        """
        Handles the form validation for updating a ticket and its associated review.
        """

        # For UpdateView, use the existing ticket instance
        review_formset = self.ReviewFormSet(self.request.POST, instance=self.object)

        success, ticket, errors = TicketReviewService.update_ticket_with_review(
            self.object, form, review_formset
            )

        if success:
            messages.success(
                self.request,
                f'Ticket "{ticket.title}" and its review updated successfully.'
                )
            return super().form_valid(form)
        else:
            for error in errors:
                messages.error(self.request, error)
            return super().form_invalid(form)
