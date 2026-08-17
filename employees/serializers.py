from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "employee_id",
            "phone_number",
            "address",
            "date_of_birth",
            "joining_date",
            "position",
            "salary",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "joining_date",
            "created_at",
            "updated_at"
        ]