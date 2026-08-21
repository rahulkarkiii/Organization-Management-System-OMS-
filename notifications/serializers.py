from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(
        source="recipient.get_full_name",
        read_only=True
    )
    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "recipient_name",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recipient",
            "recipient_name",
            "created_at",
            "updated_at"
        ]