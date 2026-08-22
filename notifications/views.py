from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from departments.models import Department
from employees.models import Employee

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        notifications = Notification.objects.select_related(
            "recipient",
        )

        if request.user.role == "admin":
            return notifications.all()

        return notifications.filter(
            recipient=request.user,
        )

    def get(self, request):
        notifications = self.get_queryset(request)

        serializer = NotificationSerializer(
            notifications,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        user = request.user

        if user.role == "employee":
            return Response(
                {
                    "error": (
                        "Employees are not allowed "
                        "to create notifications."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        recipient_id = request.data.get("recipient")

        if not recipient_id:
            return Response(
                {
                    "error": "Recipient ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        recipient = get_object_or_404(
            User,
            pk=recipient_id,
        )

        if user.role == "manager":
            if recipient.role != "employee":
                return Response(
                    {
                        "error": (
                            "Managers can only create "
                            "notifications for employees."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                managed_department = user.managed_department
            except Department.DoesNotExist:
                return Response(
                    {
                        "error": (
                            "Manager is not assigned "
                            "to a department."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                employee = Employee.objects.get(
                    user=recipient,
                )
            except Employee.DoesNotExist:
                return Response(
                    {
                        "error": "Employee record not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if employee.department_id != managed_department.id:
                return Response(
                    {
                        "error": (
                            "You can only create notifications "
                            "for employees in your department."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = NotificationSerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = serializer.save(
            recipient=recipient,
        )

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_201_CREATED,
        )



