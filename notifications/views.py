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

class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_notification(self, request, pk):
        notifications = Notification.objects.select_related(
            "recipient",
        )

        if request.user.role == "admin":
            return get_object_or_404(
                notifications,
                pk=pk,
            )

        return get_object_or_404(
            notifications,
            pk=pk,
            recipient=request.user,
        )

    def get(self, request, pk):
        notification = self.get_notification(
            request,
            pk,
        )

        serializer = NotificationSerializer(
            notification,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        notification = self.get_notification(
            request,
            pk,
        )

        if request.user.role != "admin":
            if set(request.data.keys()) != {"is_read"}:
                return Response(
                    {
                        "error": (
                            "You can only mark your "
                            "notification as read or unread."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not isinstance(
                request.data.get("is_read"),
                bool,
            ):
                return Response(
                    {
                        "error": (
                            "is_read must be true or false."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            notification.is_read = request.data["is_read"]

            notification.save(
                update_fields=[
                    "is_read",
                    "updated_at",
                ],
            )

            return Response(
                NotificationSerializer(notification).data,
                status=status.HTTP_200_OK,
            )

        serializer = NotificationSerializer(
            notification,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        notification = serializer.save()

        return Response(
            NotificationSerializer(notification).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        return self.patch(request, pk)

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can delete notifications."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        notification = get_object_or_404(
            Notification,
            pk=pk,
        )

        notification.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


