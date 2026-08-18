from django.db import models
from accounts.models import User

class Attendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("half_day", "Half Day"),
    ]
    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="attendance"
    )
    date = models.DateField()
    check_in =models.TimeField(
        null=True,
        blank=True,
    )
    check_out =models.TimeField(
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="present",
    )
    remarks = models.CharField(
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.date}"
