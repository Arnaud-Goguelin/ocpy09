from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest
    from django.db.models import QuerySet


class UserOwnershipMixin:
    """
    Generic mixin that filters any model with a 'user' field to the current user.

    This mixin should be used with views that need to ensure users can only
    access objects they own (UpdateView, DeleteView, etc.)

    Usage:
        class MyUpdateView(LoginRequiredMixin, UserOwnershipMixin, UpdateView):
            model = MyModel
            # ...
    """

    request: "HttpRequest"
    user_field: str = 'user'  # Personnalisable si le champ s'appelle autrement

    def get_queryset(self) -> "QuerySet":
        """Filter queryset to only include objects owned by the current user."""
        queryset = super().get_queryset()
        filter_kwargs = {self.user_field: self.request.user}
        return queryset.filter(**filter_kwargs)
