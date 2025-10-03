from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    title = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Review's title",
                "class": "form-control",
                "id": "id_review_title",
            }
        ),
        label="Review's title",
    )

    rating = forms.IntegerField(
        widget=forms.Select(
            choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(0, 6)],
            attrs={
                "class": "form-control",
                "id": "id_review_rating",
            },
        ),
        label="Rating",
    )

    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Review's content",
                "class": "form-control",
                "rows": 4,
                "id": "id_review_content",
            }
        ),
        label="Review's content",
        required=False,
    )

    class Meta:
        model = Review
        fields = ["title", "rating", "content"]
