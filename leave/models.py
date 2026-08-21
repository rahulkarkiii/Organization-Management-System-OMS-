from django.db import models
from django.conf import settings

class Leave(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("annual", "Annual Leave"),
        ("sick", "Sick Leave"),
        ("casual", "Casual Leave"),
        ("unpaid", "Unpaid Leave"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave",
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LEAVE_TYPE_CHOICES,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    manager_remark = models.TextField(
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.employee} - {self.leave_type} -  {self.leave_type} - {self.start_date}"