from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
      (
        "Organization Information",
        {
            "fields": ("role",)
        }
      ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
      (
        "Organization Information",
        {
            "fields": ("email","role")
        }
      ),
    )