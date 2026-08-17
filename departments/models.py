from django.db import models

class Department(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,

    )
    description = models.CharField(
        max_length=255,
        blank=True
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
