from django.db import models
from django.conf import settings

class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ("low","Low"),
        ("normal","Normal"),
        ("high","High"),
        ("urgent","Urgent"),
    ]
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="normal",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="announcements_created",
    )
    target_department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="announcements",
    )
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
            return self.title