from django import forms

from .models import Ticket


class CustomTicketForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Book's Title",
                "id": "id_title",
            }
        ),
        label="Title",
    )
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Ticket's content",
                "id": "id_content",
            }
        ),
        label="Content",
        required=False,
    )
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                "accept": "image/webp,image/png",
                "id": "id_image",
            }
        ),
        label="Load an image",
        required=False,
    )

    class Meta:
        model = Ticket
        fields = ["title", "content", "image"]
