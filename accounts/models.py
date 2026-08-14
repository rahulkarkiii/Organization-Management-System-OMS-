from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
    ("employee", "Employee"),
    ("manager", "Manager"),
    ("admin", "Admin"),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default="employee"
    )

    def __str__(self):
        return self.username