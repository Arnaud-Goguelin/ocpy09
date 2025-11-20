import io
import logging
import os
import uuid

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from PIL import Image


logger = logging.getLogger("tickets")


def ticket_image_upload_path(instance: "Ticket", filename: str):
    """Generate upload path for ticket images."""
    return f"tickets/user_{instance.user.id}/{uuid.uuid4()}-{filename}"


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
    :ivar content: An optional detailed description of the ticket.
    :type content: str
    :ivar image: An optional image associated with the ticket.
    :type image: ImageField
    :ivar user: The user associated with the ticket. This is a foreign key reference
         to the user model specified in project settings.
    :type user: ForeignKey
    :ivar time_created: The date and time when the ticket was created. Automatically
         assigned when the ticket is created.
    :type time_created: datetime
    """

    title = models.CharField("Title", max_length=128)
    content = models.TextField("Content", max_length=2048, blank=True)
    image = models.ImageField("Image", upload_to=ticket_image_upload_path, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    time_created = models.DateTimeField("Created the", auto_now_add=True)

    class Meta:
        ordering = ["-time_created"]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"Ticket: {self.title}"

    @property
    def has_review(self):
        """Check if this ticket already has at least one review."""
        return self.review.exists()

    def save(self, *args, **kwargs):
        """Override save to also process image."""
        # Process image only if it's a new upload
        if self.image and hasattr(self.image, "_committed") and not self.image._committed:
            processed_image = self._process_image(self.image)
            if processed_image:
                self.image = processed_image

        super().save(*args, **kwargs)

    def _process_image(self, image_file):
        """
        Process the uploaded image:
        - Convert to WebP
        - Resize to fit max_size while maintaining aspect ratio
        - Optimize quality
        """
        try:
            # Reset file pointer to beginning
            image_file.file.seek(0)
            # create a copy of the image in memory
            with Image.open(image_file.file) as image:
                # resize the image
                image.thumbnail((500, 500))

                # create an empty buffer to store the image
                with io.BytesIO() as output:
                    # save the image in the buffer with new format
                    image.save(output, format="webp", quality=85, optimize=True)

                    # Generate new filename
                    original_name = image_file.name
                    name_without_ext = Path(original_name).stem
                    new_name = f"{name_without_ext}.webp"

                    # Create new ContentFile
                    return ContentFile(output.getvalue(), name=new_name)

        except Exception as error:
            logger.error(f"Error processing image: {error}")
            # if failed return original file
            return image_file


@receiver(post_delete, sender=Ticket)
def delete_ticket_image_on_delete(sender, instance, **kwargs):
    """
    Delete image file from filesystem when Ticket object is deleted.
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(pre_save, sender=Ticket)
def delete_ticket_image_on_change(sender, instance, **kwargs):
    """
    Delete old image file from filesystem when Ticket image is updated.
    """
    if not instance.pk:
        # New instance, no old image to delete
        return

    try:
        old_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        # Instance doesn't exist yet
        return

    # Check if image has changed
    if old_instance.image and old_instance.image != instance.image and os.path.isfile(old_instance.image.path):
        os.remove(old_instance.image.path)
