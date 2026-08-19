from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role in ["manager", "admin"]:
            announcements = Announcement.objects.filter(
                is_active=True
            ).order_by("-created_at")

        else:
            employee_profile = getattr(
                request.user,
                "employee_profile",
                None
            )

            department = (
                employee_profile.department
                if employee_profile
                else None
            )

            if department:
                announcements = (
                    Announcement.objects.filter(
                        is_active=True,
                        target_department__isnull=True
                    )
                    | Announcement.objects.filter(
                        is_active=True,
                        target_department=department
                    )
                ).distinct().order_by("-created_at")

            else:
                announcements = Announcement.objects.filter(
                    is_active=True,
                    target_department__isnull=True
                ).order_by("-created_at")

        serializer = AnnouncementSerializer(
            announcements,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if request.user.role not in ["manager", "admin"]:
            return Response(
                {
                    "error": (
                        "Permission denied. "
                        "Only managers and admins can create announcements."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AnnouncementSerializer(
            data=request.data
        )

        if serializer.is_valid():
            announcement = serializer.save(
                created_by=request.user
            )

            return Response(
                AnnouncementSerializer(
                    announcement
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AnnouncementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_announcement(self, pk):
        return get_object_or_404(
            Announcement,
            pk=pk
        )

    def get_visible_announcement(self, request, pk):
        if request.user.role in ["manager", "admin"]:
            return get_object_or_404(
                Announcement,
                pk=pk,
                is_active=True
            )

        employee_profile = getattr(
            request.user,
            "employee_profile",
            None
        )

        department = (
            employee_profile.department
            if employee_profile
            else None
        )

        if department:
            announcements = (
                Announcement.objects.filter(
                    is_active=True,
                    target_department__isnull=True
                )
                | Announcement.objects.filter(
                    is_active=True,
                    target_department=department
                )
            ).distinct()

            return get_object_or_404(
                announcements,
                pk=pk
            )

        return get_object_or_404(
            Announcement,
            pk=pk,
            is_active=True,
            target_department__isnull=True
        )

    def check_update_permission(self, request, announcement):
        if request.user.role not in ["manager", "admin"]:
            return Response(
                {
                    "error": (
                        "Permission denied. "
                        "Only managers and admins can update announcements."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if (
            request.user.role == "manager"
            and announcement.created_by != request.user
        ):
            return Response(
                {
                    "error": (
                        "Managers can only update "
                        "their own announcements."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return None

    def get(self, request, pk):
        announcement = self.get_visible_announcement(
            request,
            pk
        )

        serializer = AnnouncementSerializer(
            announcement
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        announcement = self.get_announcement(pk)

        permission_error = self.check_update_permission(
            request,
            announcement
        )

        if permission_error:
            return permission_error

        serializer = AnnouncementSerializer(
            announcement,
            data=request.data
        )

        if serializer.is_valid():
            announcement = serializer.save()

            return Response(
                AnnouncementSerializer(
                    announcement
                ).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        announcement = self.get_announcement(pk)

        permission_error = self.check_update_permission(
            request,
            announcement
        )

        if permission_error:
            return permission_error

        serializer = AnnouncementSerializer(
            announcement,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            announcement = serializer.save()

            return Response(
                AnnouncementSerializer(
                    announcement
                ).data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can delete announcements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        announcement = self.get_announcement(pk)

        announcement.delete()

        return Response(
            {
                "message": "Announcement deleted successfully."
            },
            status=status.HTTP_200_OK
        )