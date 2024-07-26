from django.db import models
from uuid import uuid4
from enum import Enum


class AssetCategories(Enum):
    LAPTOP = "Laptop"
    OTHER = "Other"


class Ticket(models.Model):
    asset_id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category = models.CharField(
        max_length=255, choices=[(tag.name, tag.value) for tag in AssetCategories]
    )
    asset_title = models.CharField(max_length=255)
    user_owner = models.CharField(
        max_length=255
    )  # this will be the uuid of a user once that is implemented
    asset_description = models.TextField(blank=True)
    # When the model is created
    created_at = models.DateTimeField(auto_now_add=True)
    # When model is modified
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
