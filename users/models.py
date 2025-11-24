from django.contrib.auth.models import AbstractUser
from django.db import models

from feed.models import Subscription


class User(AbstractUser):
    bio = models.TextField(blank=True)

    def follow(self, user: "User"):
        Subscription.objects.get_or_create(follower=self, followed=user)

    def unfollow(self, user: "User"):
        Subscription.objects.filter(follower=self, followed=user).delete()

    def check_if_following(self, user):
        return Subscription.objects.filter(follower=self, followed=user).exists()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def followers_count(self):
        return self.followers.count()

    def __str__(self):
        return f"{self.username}"
