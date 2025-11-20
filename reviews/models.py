from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from tickets.models import Ticket


class Review(models.Model):
    """
    Represents a review left by a user for a book.

    This model stores information about a specific review, including its title,
    rating, content, the user who created it, and the timestamp of its creation.

    :ivar title: The title of the review.
    :type title: str
    :ivar rating: The numeric rating provided in the review, which is constrained to a
                 range of 0 to 5.
    :type rating: int
    :ivar content: Additional detailed text description or commentary provided by the
                   user in the review.
    :type content: str
    :ivar user: A reference to the user model, indicating the owner of the review.
    :type user: ForeignKey
    :ivar time_created: The timestamp indicating when the review was created.
    :type time_created: datetime
    """

    title = models.CharField("Title", max_length=128)
    rating = models.IntegerField("Rating", default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    content = models.TextField("Content", max_length=2048, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="review")
    time_created = models.DateTimeField("Created the", auto_now_add=True)

    class Meta:
        ordering = ["-time_created"]
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
