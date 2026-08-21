from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from departments.models import Department
from employees.models import Employee
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        if request.user.role == "admin":
            return Attendance.objects.select_related(
                "employee",
            ).all().order_by("-date")

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return Attendance.objects.none()

            employee_user_ids = Employee.objects.filter(
                department=department,
            ).values_list(
                "user_id",
                flat=True,
            )

            return Attendance.objects.filter(
                employee_id__in=employee_user_ids,
            ).select_related(
                "employee",
            ).order_by("-date")

        return Attendance.objects.filter(
            employee=request.user,
        ).order_by("-date")

    def get(self, request):
        attendance = self.get_queryset(request)

        serializer = AttendanceSerializer(
            attendance,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.role == "employee":
            serializer = AttendanceSerializer(
                data=request.data,
            )

            if serializer.is_valid():
                attendance = serializer.save(
                    employee=request.user,
                )

                return Response(
                    AttendanceSerializer(attendance).data,
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.role not in ["manager", "admin"]:
            return Response(
                {"error": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employee_id = request.data.get("employee")

        if not employee_id:
            return Response(
                {"error": "Employee ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        employee = get_object_or_404(
            User,
            pk=employee_id,
            role="employee",
        )

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return Response(
                    {
                        "error": "Manager is not assigned to a department."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            try:
                employee_record = Employee.objects.get(
                    user=employee,
                )
            except Employee.DoesNotExist:
                return Response(
                    {
                        "error": "Employee record not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if employee_record.department_id != department.id:
                return Response(
                    {
                        "error": (
                            "You can only create attendance "
                            "for employees in your department."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = AttendanceSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            attendance = serializer.save(
                employee=employee,
            )

            return Response(
                AttendanceSerializer(attendance).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class AttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_attendance(self, request, pk):
        attendance = get_object_or_404(
            Attendance.objects.select_related(
                "employee",
            ),
            pk=pk,
        )

        if request.user.role == "admin":
            return attendance

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return None

            try:
                employee = Employee.objects.get(
                    user=attendance.employee,
                )
            except Employee.DoesNotExist:
                return None

            if employee.department_id != department.id:
                return None

            return attendance

        if attendance.employee_id == request.user.id:
            return attendance

        return None

    def get(self, request, pk):
        attendance = self.get_attendance(
            request,
            pk,
        )

        if attendance is None:
            return Response(
                {"error": "Attendance not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AttendanceSerializer(
            attendance,
        )

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role == "employee":
            return Response(
                {
                    "error": (
                        "Employees cannot update attendance."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        attendance = self.get_attendance(
            request,
            pk,
        )

        if attendance is None:
            return Response(
                {"error": "Attendance not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AttendanceSerializer(
            attendance,
            data=request.data,
        )

        if serializer.is_valid():
            attendance = serializer.save()

            return Response(
                AttendanceSerializer(attendance).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can delete attendance."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        attendance = get_object_or_404(
            Attendance,
            pk=pk,
        )

        attendance.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )