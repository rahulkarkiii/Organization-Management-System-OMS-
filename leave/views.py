from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from departments.models import Department
from employees.models import Employee
from .models import Leave
from .serializers import LeaveSerializer


class LeaveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        if request.user.role == "admin":
            return Leave.objects.select_related(
                "employee",
            ).all().order_by("-created_at")

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return Leave.objects.none()

            employee_user_ids = Employee.objects.filter(
                department=department,
            ).values_list(
                "user_id",
                flat=True,
            )

            return Leave.objects.filter(
                employee_id__in=employee_user_ids,
            ).select_related(
                "employee",
            ).order_by("-created_at")

        return Leave.objects.filter(
            employee=request.user,
        ).select_related(
            "employee",
        ).order_by("-created_at")

    def get(self, request):
        leaves = self.get_queryset(request)

        serializer = LeaveSerializer(
            leaves,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            leave = serializer.save(
                employee=request.user,
            )

            return Response(
                LeaveSerializer(leave).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LeaveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave(self, request, pk):
        if request.user.role == "admin":
            return get_object_or_404(
                Leave.objects.select_related(
                    "employee",
                ),
                pk=pk,
            )

        if request.user.role == "manager":
            try:
                department = request.user.managed_department
            except Department.DoesNotExist:
                return None

            employee_user_ids = Employee.objects.filter(
                department=department,
            ).values_list(
                "user_id",
                flat=True,
            )

            return Leave.objects.filter(
                pk=pk,
                employee_id__in=employee_user_ids,
            ).select_related(
                "employee",
            ).first()

        return Leave.objects.filter(
            pk=pk,
            employee=request.user,
        ).select_related(
            "employee",
        ).first()

    def get(self, request, pk):
        leave = self.get_leave(
            request,
            pk,
        )

        if leave is None:
            return Response(
                {"error": "Leave not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LeaveSerializer(leave)

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role != "employee":
            return Response(
                {
                    "error": (
                        "Only employees can update their "
                        "own leave requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        leave = self.get_leave(
            request,
            pk,
        )

        if leave is None:
            return Response(
                {"error": "Leave not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if leave.status != "pending":
            return Response(
                {
                    "error": (
                        "Only pending leave requests "
                        "can be updated."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = LeaveSerializer(
            leave,
            data=request.data,
        )

        if serializer.is_valid():
            leave = serializer.save()

            return Response(
                LeaveSerializer(leave).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        if request.user.role != "employee":
            return Response(
                {
                    "error": (
                        "Only employees can cancel "
                        "their own leave requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        leave = self.get_leave(
            request,
            pk,
        )

        if leave is None:
            return Response(
                {"error": "Leave not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if leave.status != "pending":
            return Response(
                {
                    "error": (
                        "Only pending leave requests "
                        "can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        leave.status = "cancelled"
        leave.save()

        return Response(
            {"message": "Leave cancelled successfully."},
            status=status.HTTP_200_OK,
        )


