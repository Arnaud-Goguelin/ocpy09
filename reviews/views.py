from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView

from tickets.models import Ticket

from .form import ReviewForm
from .models import Review


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "reviews/review_form.html"
    success_url = reverse_lazy("feed:subscriptions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_id = self.kwargs.get("ticket_id")
        if ticket_id:
            context["ticket"] = get_object_or_404(Ticket, pk=ticket_id)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        ticket_id = self.kwargs.get("ticket_id")
        if ticket_id:
            form.instance.ticket = get_object_or_404(Ticket, pk=ticket_id)
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    template_name = "reviews/review_form.html"
    form_class = ReviewForm
    context_object_name = "review"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object and self.object.ticket:
            context["ticket"] = self.object.ticket
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy("feed:subscriptions")


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "reviews/reviews_confirm_delete.html"
    context_object_name = "review"
    success_url = reverse_lazy("feed:subscriptions")

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
