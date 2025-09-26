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
                "placeholder": "Nom d'utilisateur à suivre",
                "id": "id_subscription",
            }
        ),
        label="Nom d'utilisateur",
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
            logger.info(f"User found: {username}")
        except User.DoesNotExist as error:
            logger.warning(f"Attempt from {self.user.username} to follow {username}")
            raise forms.ValidationError("This user does not exist.") from error

        if user_to_follow == self.user:
            logger.warning(f"Attempt from {self.user.username} to follow itself.")
            raise forms.ValidationError("You can not follow yourself.")

        if self.user.check_if_following(user_to_follow):
            logger.warning(f"Attempt from {self.user.username} to follow {username} twice.")
            raise forms.ValidationError("You already follow this user.")

        logger.info(f"Attempt successful from {self.user.username} to follow {username}")
        # TODO try to return Subscription instance directly
        return username

    # TODO: 'save' method could be done automatically by django
    def save(self, commit=True):
        username = self.cleaned_data["username"]
        user_to_follow = User.objects.get(username=username)

        subscription = Subscription(follower=self.user, followed=user_to_follow)

        if commit:
            subscription.save()
            logger.info(f"Subscription created for {self.user.username} now following {username}")

        return subscription
