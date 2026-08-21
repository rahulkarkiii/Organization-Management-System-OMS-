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


class TaskDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_task(self, request, pk):
        task = get_object_or_404(
            Task.objects.select_related(
                "employee",
            ),
            pk=pk,
        )

        if request.user.role == "admin":
            return task

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return None

            try:
                employee = Employee.objects.get(
                    user=task.employee
                )
            except Employee.DoesNotExist:
                return None

            if employee.department_id != department.id:
                return None

            return task

        if task.employee_id == request.user.id:
            return task

        return None

    def get(self, request, pk):
        task = self.get_task(
            request,
            pk,
        )

        if task is None:
            return Response(
                {
                    "error": "Task not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(task)

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role == "employee":
            return Response(
                {
                    "error": "Employees cannot modify tasks."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        task = self.get_task(
            request,
            pk,
        )

        if task is None:
            return Response(
                {
                    "error": "Task not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(
            task,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                TaskSerializer(task).data,
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
                    "error": "Only admins can delete tasks."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        task = get_object_or_404(
            Task,
            pk=pk,
        )

        task.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )