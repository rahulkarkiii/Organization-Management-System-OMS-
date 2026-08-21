from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from departments.models import Department
from employees.models import Employee
from .serializers import EmployeeSerializer


class EmployeesListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        if request.user.role == "admin":
            return Employee.objects.select_related(
                "user",
                "department",
            ).all()

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return Employee.objects.none()

            return Employee.objects.select_related(
                "user",
                "department",
            ).filter(
                department=department
            )

        return Employee.objects.select_related(
            "user",
            "department",
        ).filter(
            user=request.user
        )

    def get(self, request):
        employees = self.get_queryset(request)

        serializer = EmployeeSerializer(
            employees,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can create employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EmployeeSerializer(data=request.data)

        if serializer.is_valid():
            employee = serializer.save()

            return Response(
                EmployeeSerializer(employee).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class EmployeeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_employee(self, request, pk):
        employee = get_object_or_404(
            Employee.objects.select_related(
                "user",
                "department",
            ),
            pk=pk,
        )

        if request.user.role == "admin":
            return employee

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return None

            if employee.department_id != department.id:
                return None

            return employee

        if employee.user_id == request.user.id:
            return employee

        return None

    def get(self, request, pk):
        employee = self.get_employee(request, pk)

        if employee is None:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeSerializer(employee)

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can update employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employee = self.get_employee(request, pk)

        if employee is None:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = EmployeeSerializer(
            employee,
            data=request.data,
        )

        if serializer.is_valid():
            employee = serializer.save()

            return Response(
                EmployeeSerializer(employee).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can delete employees."},
                status=status.HTTP_403_FORBIDDEN,
            )

        employee = self.get_employee(request, pk)

        if employee is None:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        employee.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )