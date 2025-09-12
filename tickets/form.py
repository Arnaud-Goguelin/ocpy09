from django import forms

from .models import Ticket


class CustomTicketForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Titre du livre",
                "id": "id_title",
            }
        ),
        label="Titre",
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "from-text-area",
                "placeholder": "Description du livre",
                "rows": "6",
                "id": "id_description",
            }
        ),
        label="Description",
        required=False,
    )
    image = forms.ImageField(
        widget=forms.FileInput(
            attrs={
                "class": "form-input",
                "accept": "image/webp,image/png",
                "id": "id_image",
            }
        ),
        label="Télécharger une image",
        required=False,
    )

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
