from rest_framework import serializers
from .models import Department
from django.contrib.auth import get_user_model

User = get_user_model()
class DepartmentSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="manager"),
        allow_null=True,
        required=False,
    )

    manager_name = serializers.CharField(
        source="manager.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "manager",
            "manager_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "manager_name",
            "created_at",
            "updated_at",
        ]
