from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

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
    fields = ["title", "description"]
    context_object_name = "ticket"

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("tickets:detail", kwargs={"primary_key": self.object.primary_key})


class TicketDeleteView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "tickets/ticket_confirm_delete.html"
    context_object_name = "ticket"
    success_url = reverse_lazy("tickets:list")

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)
