from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from accounts.models import User
from departments.models import Department
from employees.models import Employee
from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self, request):
        if request.user.role == "admin":
            return Task.objects.select_related(
                "employee",
            ).all().order_by("-created_at")

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return Task.objects.none()

            employee_user_ids = Employee.objects.filter(
                department=department
            ).values_list(
                "user_id",
                flat=True,
            )

            return Task.objects.filter(
                employee_id__in=employee_user_ids
            ).select_related(
                "employee",
            ).order_by("-created_at")

        return Task.objects.filter(
            employee=request.user
        ).order_by("-created_at")

    def get(self, request):
        tasks = self.get_queryset(request)

        serializer = TaskSerializer(
            tasks,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.role == "employee":
            return Response(
                {
                    "error": "Employees cannot create tasks."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        employee_id = request.data.get("employee")

        if not employee_id:
            return Response(
                {
                    "error": "Employee ID is required."
                },
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
                    user=employee
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
                        "error": "You can only create tasks for employees in your department."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer = TaskSerializer(
            data=request.data
        )

        if serializer.is_valid():
            task = serializer.save(
                employee=employee
            )

            return Response(
                TaskSerializer(task).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


