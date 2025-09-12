from django.conf import settings
from django.db import models


class Ticket(models.Model):
    """
    Represents a support ticket or post that can be created by a user.

    This model is used to store information about tickets:
        the title,
        the description,
        the associated user,
        and the time they were created.
    Tickets are ordered by their creation time in descending order.

    :ivar title: The title of the ticket.
    :type title: str
    :ivar description: An optional detailed description of the ticket.
    :type description: str
    :ivar user: The user associated with the ticket. This is a foreign key reference
         to the user model specified in project settings.
    :type user: ForeignKey
    :ivar time_created: The date and time when the ticket was created. Automatically
         assigned when the ticket is created.
    :type time_created: datetime
    """

    title = models.CharField("Title", max_length=128)
    description = models.TextField("Description", max_length=2048, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    time_created = models.DateTimeField("Created the", auto_now_add=True)

    class Meta:
        ordering = ["-time_created"]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"Ticket: {self.title}"
