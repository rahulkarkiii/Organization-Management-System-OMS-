from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,

    )
    description = models.CharField(
        max_length=255,
        blank=True
    )
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_department",
        limit_choices_to={"role": "manager"},
    )

    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return self.name
