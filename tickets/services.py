import logging

from django.contrib.auth import get_user_model
from django.db import DatabaseError, transaction
from django.forms import inlineformset_factory

from reviews.form import ReviewForm
from reviews.models import Review

from .models import Ticket


User = get_user_model()
logger = logging.getLogger("tickets")


class TicketReviewService:
    """
    Service class for handling ticket and review operations.
    Centralizes business logic for ticket-review workflows.
    """

    @staticmethod
    def review_formset(nb_of_empty_form: int):
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
    def create_ticket_with_review(ticket_form, review_formset, user) -> tuple[bool, Ticket | None, list]:
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

                # Validate review formset
                if not review_formset.is_valid():
                    # collect errors
                    errors.extend(review_formset.non_form_errors())
                    for form in review_formset:
                        if form.errors:
                            # extract error messages
                            for field, error_list in form.errors.items():
                                errors.append(f"{field}: {', '.join(error_list)}")

                    logger.error(f"Review formset validation failed: {errors}")

                    # raise exception to rollback transaction
                    raise DatabaseError("Review validation failed")

                # Process review formset
                # pass above Ticket instance to ReviewFormSet instance retrieved in context
                review_formset.instance = ticket
                # Review instances are already linked to Ticket instance thanks to inlineformset_factory
                reviews = review_formset.save(commit=False)

                for review in reviews:
                    review.user = user
                    review.save()

                return True, ticket, errors

        except DatabaseError:
            # rollback transaction and return error message
            return False, None, errors

        except Exception as error:
            logger.error(f"Error creating ticket with review for user {user.username}: {error}")
            return False, None, [f"An error occurred: {error}"]

    @staticmethod
    def prepare_context(context: dict, formset_class, title: str, request, instance=None):
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
            context["review_formset"] = formset_class(
                request.POST or None,
                instance=instance,
                queryset=Review.objects.filter(ticket=instance),
            )

        context["title"] = title

        return context
