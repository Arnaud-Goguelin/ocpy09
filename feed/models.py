from django.conf import settings
from django.db import models


class Subscription(models.Model):
    # follower = all the users followed by one user
    follower = models.ForeignKey(
        # in literevu.settings.py AUTH_USER_MODEL = "users.User"
        # so foreing key is "users.User"
        # using settings.AUTH_USER_MODEL avoid circular import with User class
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        # understand here: on user following many users
    )

    # followed = all the users following one user
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
        # understand here: the many followers of one user
    )

    # this unique constraint ensure that a user can't follow twice the same user'
    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower} is following {self.followed}"
