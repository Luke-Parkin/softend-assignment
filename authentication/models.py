from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom user model, extending the default Django user
class CustomUser(AbstractUser):
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.username
