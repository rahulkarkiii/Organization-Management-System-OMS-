from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from accounts.models import User
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.role == "admin":
            notifications = Notification.objects.all()

        else:
            notifications = Notification.objects.filter(
                recipient=request.user
            )

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(serializer.data)


    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can create notifications."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        recipient_id = request.data.get("recipient")

        if not recipient_id:
            return Response(
                {
                    "error": "Recipient ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        recipient = get_object_or_404(
            User,
            pk=recipient_id
        )

        serializer = NotificationSerializer(
            data=request.data
        )

        if serializer.is_valid():

            notification = serializer.save(
                recipient=recipient
            )

            return Response(
                NotificationSerializer(
                    notification
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class NotificationDetailView(APIView):
    permission_classes = (IsAuthenticated,)


    def get_notification(self, request, pk):
        if request.user.role == "admin":
            return get_object_or_404(
                Notification,
                pk=pk
            )

        return get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )


    def get(self, request, pk):

        notification = self.get_notification(
            request,
            pk
        )

        serializer = NotificationSerializer(
            notification
        )

        return Response(serializer.data)


    def put(self, request, pk):

        notification = self.get_notification(
            request,
            pk
        )

        if request.user.role != "admin":

            if set(request.data.keys()) != {"is_read"}:
                return Response(
                    {
                        "error": (
                            "You can only mark your notification "
                            "as read or unread."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            notification.is_read = request.data.get(
                "is_read"
            )

            notification.save()

            return Response(
                NotificationSerializer(
                    notification
                ).data,
                status=status.HTTP_200_OK
            )

        serializer = NotificationSerializer(
            notification,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    def delete(self, request, pk):

        notification = self.get_notification(
            request,
            pk
        )
        notification.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )