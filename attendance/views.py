from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role in ["manager", "admin"]:
            attendance = Attendance.objects.all().order_by("-date")
        else:
            attendance = Attendance.objects.filter(
                employee=request.user
            ).order_by("-date")

        serializer = AttendanceSerializer(
            attendance,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.role == "employee":
            serializer = AttendanceSerializer(data=request.data)

            if serializer.is_valid():
                attendance = serializer.save(
                    employee=request.user
                )

                return Response(
                    AttendanceSerializer(attendance).data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.role in ["manager", "admin"]:

            employee_id = request.data.get("employee")

            if not employee_id:
                return Response(
                    {"error": "Employee ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            employee = get_object_or_404(
                User,
                pk=employee_id
            )

            serializer = AttendanceSerializer(
                data=request.data
            )

            if serializer.is_valid():
                attendance = serializer.save(
                    employee=employee
                )

                return Response(
                    AttendanceSerializer(attendance).data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"error": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN
        )


class AttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_attendance(self, request, pk):
        if request.user.role in ["manager", "admin"]:
            return get_object_or_404(
                Attendance,
                pk=pk
            )

        return get_object_or_404(
            Attendance,
            pk=pk,
            employee=request.user
        )

    def get(self, request, pk):
        attendance = self.get_attendance(
            request,
            pk
        )

        serializer = AttendanceSerializer(
            attendance
        )

        return Response(
            serializer.data
        )

    def put(self, request, pk):
        if request.user.role not in ["manager", "admin"]:
            return Response(
                {
                    "error": "Only managers and admins can update attendance."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        attendance = get_object_or_404(
            Attendance,
            pk=pk
        )

        serializer = AttendanceSerializer(
            attendance,
            data=request.data
        )

        if serializer.is_valid():
            attendance = serializer.save()

            return Response(
                AttendanceSerializer(attendance).data,
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
                    "error": "Only admins can delete attendance."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        attendance = get_object_or_404(
            Attendance,
            pk=pk
        )

        attendance.delete()

        return Response(
            {
                "message": "Attendance deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )