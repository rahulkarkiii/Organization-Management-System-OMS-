from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from departments.models import Department
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        base_queryset = Announcement.objects.filter(
            is_active=True,
        ).select_related(
            "created_by",
            "target_department",
        )

        if request.user.role == "admin":
            return base_queryset.order_by("-created_at")

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return base_queryset.filter(
                    target_department__isnull=True,
                ).order_by("-created_at")

            return base_queryset.filter(
                target_department__isnull=True,
            ) | base_queryset.filter(
                target_department=department,
            )

        employee_profile = getattr(
            request.user,
            "employee_profile",
            None,
        )

        department = (
            employee_profile.department
            if employee_profile
            else None
        )

        if department:
            return base_queryset.filter(
                target_department__isnull=True,
            ) | base_queryset.filter(
                target_department=department,
            )

        return base_queryset.filter(
            target_department__isnull=True,
        )

    def get(self, request):
        announcements = self.get_queryset(
            request
        ).distinct().order_by(
            "-created_at"
        )

        serializer = AnnouncementSerializer(
            announcements,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
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
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AnnouncementSerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_department = serializer.validated_data.get(
            "target_department",
        )

        if request.user.role == "manager":
            try:
                managed_department = request.user.managed_department
            except Department.DoesNotExist:
                return Response(
                    {
                        "error": (
                            "Manager is not assigned to a department."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if target_department is None:
                return Response(
                    {
                        "error": (
                            "Managers can only create announcements "
                            "for their own department."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if target_department.id != managed_department.id:
                return Response(
                    {
                        "error": (
                            "You can only create announcements "
                            "for your own department."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        announcement = serializer.save(
            created_by=request.user,
        )

        return Response(
            AnnouncementSerializer(
                announcement,
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AnnouncementDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_announcement(self, pk):
        return get_object_or_404(
            Announcement.objects.select_related(
                "created_by",
                "target_department",
            ),
            pk=pk,
        )

    def get_visible_announcement(self, request, pk):
        if request.user.role == "admin":
            return get_object_or_404(
                Announcement.objects.select_related(
                    "created_by",
                    "target_department",
                ),
                pk=pk,
                is_active=True,
            )

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return get_object_or_404(
                    Announcement.objects.select_related(
                        "created_by",
                        "target_department",
                    ),
                    pk=pk,
                    is_active=True,
                    target_department__isnull=True,
                )

            announcements = Announcement.objects.filter(
                is_active=True,
            ).filter(
                target_department__isnull=True,
            ) | Announcement.objects.filter(
                is_active=True,
                target_department=department,
            )

            return get_object_or_404(
                announcements.select_related(
                    "created_by",
                    "target_department",
                ),
                pk=pk,
            )

        employee_profile = getattr(
            request.user,
            "employee_profile",
            None,
        )

        department = (
            employee_profile.department
            if employee_profile
            else None
        )

        if department:
            announcements = Announcement.objects.filter(
                is_active=True,
            ).filter(
                target_department__isnull=True,
            ) | Announcement.objects.filter(
                is_active=True,
                target_department=department,
            )

            return get_object_or_404(
                announcements.select_related(
                    "created_by",
                    "target_department",
                ),
                pk=pk,
            )

        return get_object_or_404(
            Announcement.objects.select_related(
                "created_by",
                "target_department",
            ),
            pk=pk,
            is_active=True,
            target_department__isnull=True,
        )

    def check_update_permission(
        self,
        request,
        announcement,
    ):
        if request.user.role not in ["manager", "admin"]:
            return Response(
                {
                    "error": (
                        "Permission denied. "
                        "Only managers and admins can update announcements."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
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
                status=status.HTTP_403_FORBIDDEN,
            )

        return None

    def validate_manager_department(
        self,
        request,
        target_department,
    ):
        if request.user.role != "manager":
            return None

        try:
            managed_department = request.user.managed_department
        except Department.DoesNotExist:
            return Response(
                {
                    "error": (
                        "Manager is not assigned to a department."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if target_department is None:
            return Response(
                {
                    "error": (
                        "Managers cannot create or update "
                        "company-wide announcements."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if target_department.id != managed_department.id:
            return Response(
                {
                    "error": (
                        "You can only manage announcements "
                        "for your own department."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return None

    def get(self, request, pk):
        announcement = self.get_visible_announcement(
            request,
            pk,
        )

        serializer = AnnouncementSerializer(
            announcement,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        announcement = self.get_announcement(pk)

        permission_error = self.check_update_permission(
            request,
            announcement,
        )

        if permission_error:
            return permission_error

        serializer = AnnouncementSerializer(
            announcement,
            data=request.data,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_department = serializer.validated_data.get(
            "target_department",
            announcement.target_department,
        )

        department_error = self.validate_manager_department(
            request,
            target_department,
        )

        if department_error:
            return department_error

        announcement = serializer.save()

        return Response(
            AnnouncementSerializer(
                announcement,
            ).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        announcement = self.get_announcement(pk)

        permission_error = self.check_update_permission(
            request,
            announcement,
        )

        if permission_error:
            return permission_error

        serializer = AnnouncementSerializer(
            announcement,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_department = serializer.validated_data.get(
            "target_department",
            announcement.target_department,
        )

        department_error = self.validate_manager_department(
            request,
            target_department,
        )

        if department_error:
            return department_error

        announcement = serializer.save()

        return Response(
            AnnouncementSerializer(
                announcement,
            ).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can delete announcements."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        announcement = self.get_announcement(pk)

        announcement.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
