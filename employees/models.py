from django.db import models
from django.conf import settings

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )
    address = models.CharField(
        max_length=100,
        blank=True,
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
    )
    joined_date = models.DateField(
        auto_now_add=True,
    )
    position = models.CharField(
        max_length=100,
        blank=True,
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        default=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    def __str__(self):
        return f"{self.user.username} - {self.employee_id}"