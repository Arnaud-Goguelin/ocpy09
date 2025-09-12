from django.db import models
from django.conf import settings


class Subscription(models.Model):
    follower= models.ForeignKey(
        # in literevu.settings.py AUTH_USER_MODEL = "users.User"
        # so foreing key is "users.User"
        # using settings.AUTH_USER_MODEL avoid circular import with User class
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'
        )
    followed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'
        )

    class Meta:
        unique_together = ('follower', 'followed')

