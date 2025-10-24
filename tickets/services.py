import logging
from typing import Optional, Tuple

from django.contrib.auth import get_user_model
from django.db import transaction
from django.forms import inlineformset_factory

from reviews.form import ReviewForm
from reviews.models import Review
from .form import CustomTicketForm
from .models import Ticket

User = get_user_model()
logger = logging.getLogger("tickets")


class TicketReviewService:
    """
    Service class for handling ticket and review operations.
    Centralizes business logic for ticket-review workflows.
    """

    @staticmethod
    def review_formset(nb_of_empty_form : int):
        """Create and return a review formset for ticket-review operations."""
        return inlineformset_factory(
            parent_model=Ticket,
            model=Review,
            form=ReviewForm,
            fields=["title", "rating", "content"],
            extra=nb_of_empty_form,
            max_num=1,
            min_num=1,
            validate_min=True,
            can_delete=False,
            )

    @staticmethod
    def create_ticket_with_review(ticket_form, review_formset, user) -> Tuple[bool, Optional[Ticket], list]:
        """
        Create a ticket with an associated review in a single transaction.

        :param ticket_form: Validated ticket form
        :param review_formset: Review formset
        :param user: User creating the ticket and review
        :return: Tuple (success, ticket_instance, errors)
        """
        errors = []

        try:
            # use transaction.atomic context to delete all read or write request to db if an error occurs
            with transaction.atomic():
                # reminder, self.object is a Ticket instance (cf. view class attribute)
                # first validate and save Ticket instance as it is the parent in Ticket-Review relationship
                # complete from form data, link it to the current user and save it in db

                # Create and save ticket
                ticket = ticket_form.save(commit=False)
                ticket.user = user
                ticket.save()

                # Process review formset
                if review_formset.is_valid():
                    # pass above Ticket instance to ReviewFormSet instance retrieved in context
                    review_formset.instance = ticket
                    # Review instances are already linked to Ticket instance thanks to inlineformset_factory
                    reviews = review_formset.save(commit=False)

                    for review in reviews:
                        review.user = user
                        review.save()

                    return True, ticket, errors

                else:
                    errors.extend(review_formset.non_form_errors())
                    for form in review_formset:
                        if form.errors:
                            errors.extend(form.errors.values())

                    return False, None, errors

        except Exception as error:
            logger.error(f"Error creating ticket with review for user {user.username}: {error}")
            return False, None, [f"An error occurred: {error}"]

    @staticmethod
    def update_ticket_with_review(ticket, ticket_form, review_formset) -> Tuple[bool, Optional[Ticket], list]:
        """
        Update a ticket with its associated review in a single transaction.

        :param ticket: Existing ticket instance
        :param ticket_form: Validated ticket form
        :param review_formset: Review formset
        :return: Tuple (success, ticket_instance, errors)
        """
        errors = []

        try:
            # use transaction.atomic context to rollback all database operations if an error occurs
            with transaction.atomic():
                # Save the ticket form (self.object in view is already set by UpdateView)
                updated_ticket = ticket_form.save()

                # validate and save Review instance
                if review_formset.is_valid():
                    # Review instances are already linked to Ticket instance thanks to inlineformset_factory
                    reviews = review_formset.save(commit=False)

                    # Update user for any new reviews (though in update mode, reviews should already exist)
                    for review in reviews:
                        if not review.user_id: # Only set user if not already set
                            review.user = updated_ticket.user
                        review.save()

                    # Handle many-to-many relationships if any
                    review_formset.save_m2m()

                    return True, updated_ticket, errors

                else:
                    errors.extend(review_formset.non_form_errors())
                    for form in review_formset:
                        if form.errors:
                            errors.extend(form.errors.values())

                    logger.warning(f"Review formset validation failed during update: {errors}")
                    return False, None, errors

        except Exception as error:
            logger.error(f"Error updating ticket with review: {error}")
            return False, None, [f"An error occurred: {error}"]

    @staticmethod
    def prepare_context(context : dict, formset_class, title: str, request, instance=None):
        """
        Prepare review formset for context based on request type.

        :param formset_class: The formset class to instantiate
        :param request: HTTP request object
        :param instance: Ticket instance (None for create, existing for update)
        :return: Formset instance
        """

        # reminder:
        # at this point instance (Ticket instance) is None as it is not created yet in POST request
        # yet in PUT request (UpdateView) instance is the existing Ticket instance
        if request.POST:
            # re display form with data from POST request in case or error and invalid form
            context["review_formset"] = formset_class(request.POST, instance=instance)
        else:
            context["review_formset"] = formset_class(instance=instance)

        context["title"] = title

        return context
