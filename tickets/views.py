from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from reviews.form import ReviewForm
from reviews.models import Review

from .form import CustomTicketForm
from .models import Ticket


class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "tickets/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = "tickets/ticket_detail.html"
    context_object_name = "ticket"


class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_form.html"
    success_url = reverse_lazy("tickets:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TicketUpdateView(LoginRequiredMixin, UpdateView):
    model = Ticket
    template_name = "tickets/ticket_form.html"
    form_class = CustomTicketForm
    context_object_name = "ticket"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("tickets:detail", kwargs={"primary_key": self.object.primary_key})


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "tickets/ticket_confirm_delete.html"
    context_object_name = "ticket"
    success_url = reverse_lazy("tickets:list")

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)


class TicketReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Class-Based View pour créer un Ticket avec sa Review en même temps
    en utilisant les InlineFormSets de Django
    """

    model = Ticket
    form_class = CustomTicketForm
    template_name = "tickets/ticket_review_form.html"
    success_url = reverse_lazy("tickets:list")

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
