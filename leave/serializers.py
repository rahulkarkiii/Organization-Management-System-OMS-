from rest_framework import serializers
from .models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "manager_remark",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "employee",
            "status",
            "manager_remark",
            "created_at",
            "updated_at"
        ]
    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date must be greater than start date."
            )
        return data