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


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("feed:user_posts")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = "tickets/ticket_form.html"
    form_class = CustomTicketForm
    context_object_name = "ticket"
    success_url = reverse_lazy("feed:user_posts")

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "tickets/ticket_confirm_delete.html"
    context_object_name = "ticket"
    success_url = reverse_lazy("feed:user_posts")

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)


# TODO keep as simplest as possible and put logic in a service.py file to make unit test easier
class TicketReviewCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new ticket with an associated review.

    This class-based view allows users who are logged in to create a new ticket
    and optionally one associated review. It utilizes a formset to handle the review
    creation alongside the ticket. Upon successful submission, the view saves the ticket
    and its associated review(s) and redirects to the specified success URL.

    It ensures atomicity during ticket and review creation, so if any part of the
    transaction fails, no changes are committed to the database.

    :ivar model: The model associated with the view, which is `Ticket`.
    :type model: Model
    :ivar form_class: The form used for creating a ticket.
    :type form_class: ModelForm
    :ivar template_name: The path to the template used to render this view.
    :type template_name: str
    :ivar success_url: The URL to redirect to on successful creation of the ticket.
    :type success_url: str
    """

    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_review_form.html"
    success_url = reverse_lazy("feed:user_posts")

    def __init__(self, **kwargs):
        # init formset
        super().__init__(**kwargs)
        self.ReviewFormSet = inlineformset_factory(
            parent_model=Ticket,
            model=Review,
            form=ReviewForm,
            fields=["title", "rating", "content"],
            extra=1,  # nb of empty form to display
            max_num=1,  # max 1 review
            min_num=1,  # min 1 review required
            validate_min=True,
            can_delete=False,
        )

    def get_context_data(self, **kwargs):
        """
        Get the context data for the view and update it on whether there is
        POST request or a GET request, and set the ReviewFormSet accordingly.

        :param kwargs: Keyword arguments passed to the method.
        :return: Dictionary containing the context data for the view.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        # reminder: at this point self.object (Ticket instance) is None as it is not created yet
        if self.request.POST:
            # re display form with data from POST request in case or error and invalid form
            context["review_formset"] = self.ReviewFormSet(self.request.POST, instance=self.object)
        else:
            context["review_formset"] = self.ReviewFormSet(instance=self.object)

        context["title"] = "Create Ticket with Review"
        return context

    def form_valid(self, form):
        """
        Validate and process a submitted form, along with an associated review formset,
        within a database transaction to ensure atomicity. If all components of the form
        and formset are valid, it saves the ticket, associates reviews with the user,
        and commits the data to the database. If the review formset is invalid, the
        process is aborted and the invalid form is returned.

         :param form: The ticket form to be validated and saved.
        :type form: ModelForm
        :return: HTTP response object indicating the result of the form processing.
        :rtype: HttpResponse
        """

        # Do not fetch review_formset from context here as in context
        # self.object (Ticket instance) is None, it is not created yet.
        # Moreover transaction.atomic context below will ensure it is not created in case or error.
        # Thus instanciate review_formset here with instance=None is more explicit and comprehensive.
        review_formset = self.ReviewFormSet(self.request.POST, instance=None)

        # use transaction.atomic context to delete all read or write request to db if an error occurs
        with transaction.atomic():
            # reminder, self.object is a Ticket instance (cf. model attribute)
            # first validate and save Ticket instance as it is the parent in Ticket-Review relationship
            # complete from form data, link it to the current user and save it in db
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()

            # validate and save Review instance
            if review_formset.is_valid():
                # pass above Ticket instance to ReviewFormSet instance retrieved in context
                review_formset.instance = self.object
                # Review instances are already linked to Ticket instance thanks to inlineformset_factory
                reviews = review_formset.save(commit=False)

                # keep a for loop to respect docs standards
                # and to support a possible change of max_num in review_formset
                # and a loop on a list of 1 item is not costly in terms of performance
                for review in reviews:
                    review.user = self.request.user
                    review.save()

                # reminder: parent form_valid method return success message and redirect to success_url
                messages.success(self.request, f'Ticket "{self.object.title}" and its review created successfully.')
                return super().form_valid(form)
            else:
                messages.error(self.request, "Please correct the errors below.")
                # reminder: parent form_invalid method return error message
                return super().form_invalid(form)


class TicketReviewUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing ticket with an associated review.

    This class-based view allows users who are logged in to update an existing ticket
    and its associated review. It utilizes a formset to handle the review
    update alongside the ticket. Upon successful submission, the view saves the ticket
    and its associated review(s) and redirects to the specified success URL.

    It ensures atomicity during ticket and review update, so if any part of the
    transaction fails, no changes are committed to the database.

    :ivar model: The model associated with the view, which is `Ticket`.
    :type model: Model
    :ivar form_class: The form used for updating a ticket.
    :type form_class: ModelForm
    :ivar template_name: The path to the template used to render this view.
    :type template_name: str
    :ivar success_url: The URL to redirect to on successful update of the ticket.
    :type success_url: str
    """

    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_review_form.html"
    success_url = reverse_lazy("feed:user_posts")
    context_object_name = "ticket"

    def __init__(self, **kwargs):
        # init formset
        super().__init__(**kwargs)
        self.ReviewFormSet = inlineformset_factory(
            parent_model=Ticket,
            model=Review,
            form=ReviewForm,
            fields=["title", "rating", "content"],
            extra=0,  # no extra empty form for update
            max_num=1,  # max 1 review
            min_num=1,  # min 1 review required
            validate_min=True,
            can_delete=False,
        )

    def get_queryset(self):
        """
        Filter the queryset to only include tickets owned by the current user.

        :return: Queryset of tickets filtered by user.
        :rtype: QuerySet
        """
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Get the context data for the view and update it based on whether there is
        POST request or a GET request, and set the ReviewFormSet accordingly.

        :param kwargs: Keyword arguments passed to the method.
        :return: Dictionary containing the context data for the view.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        # In UpdateView, self.object is the existing Ticket instance
        if self.request.POST:
            # re display form with data from POST request in case of error and invalid form
            context["review_formset"] = self.ReviewFormSet(self.request.POST, instance=self.object)
        else:
            context["review_formset"] = self.ReviewFormSet(instance=self.object)

        context["title"] = "Update Ticket and Review"
        return context

    def form_valid(self, form):
        """
        Validate and process a submitted form, along with an associated review formset,
        within a database transaction to ensure atomicity. If all components of the form
        and formset are valid, it updates the ticket and associated review, and commits
        the data to the database. If the review formset is invalid, the process is
        aborted and the invalid form is returned.

         :param form: The ticket form to be validated and saved.
        :type form: ModelForm
        :return: HTTP response object indicating the result of the form processing.
        :rtype: HttpResponse
        """

        # For UpdateView, use the existing ticket instance
        review_formset = self.ReviewFormSet(self.request.POST, instance=self.object)

        # use transaction.atomic context to rollback all database operations if an error occurs
        with transaction.atomic():
            # Save the ticket form (self.object is already set by UpdateView)
            self.object = form.save()

            # validate and save Review instance
            if review_formset.is_valid():
                # Review instances are already linked to Ticket instance thanks to inlineformset_factory
                reviews = review_formset.save(commit=False)

                # Update user for any new reviews (though in update mode, reviews should already exist)
                for review in reviews:
                    if not review.user_id:  # Only set user if not already set
                        review.user = self.request.user
                    review.save()

                # Save any deleted reviews (though can_delete=False in our case)
                review_formset.save_m2m()

                messages.success(self.request, f'Ticket "{self.object.title}" and its review updated successfully.')
                return super().form_valid(form)
            else:
                messages.error(self.request, "Please correct the errors below.")
                return super().form_invalid(form)
