import logging

from django import forms
from django.contrib.auth import get_user_model

from .models import Subscription


logger = logging.getLogger("feed")
User = get_user_model()


class CreateSubscriptionForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "The user's name you want to follow",
                "id": "id_subscription",
            }
        ),
        label="username to follow",
    )

    class Meta:
        model = Subscription
        fields = []

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist as error:
            logger.error(f"User {username} does not found.")
            raise forms.ValidationError("This user does not exist.") from error

        if user_to_follow == self.user:
            raise forms.ValidationError("You can not follow yourself.")

        if self.user.check_if_following(user_to_follow):
            raise forms.ValidationError("You already follow this user.")

        return user_to_follow

    def save(self, commit=True):
        # Create the Subscription instance without saving yet
        subscription = super().save(commit=False)

        # Set the follower and followed
        subscription.follower = self.user
        subscription.followed = self.cleaned_data["username"]

        if commit:
            subscription.save()

        return subscription
