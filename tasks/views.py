from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from accounts.models import User
from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if request.user.role in ["manager", "admin"]:
            tasks = Task.objects.all().order_by("-created_at")
        else:
            tasks = Task.objects.filter(
                employee=request.user
            ).order_by("-created_at")
        serializer = TaskSerializer(
            tasks,
            many=True
        )
        return Response(serializer.data)

    def post(self, request):
        if request.user.role == "employee":
            return Response(
                {
                    "error": "Employees cannot create tasks."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        employee_id = request.data.get("employee")
        if not employee_id:
            return Response(
                {
                    "error": "Employee ID is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        employee = get_object_or_404(
            User,
            pk=employee_id,
            role="employee"
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
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TaskDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_task(self, request, pk):
        if request.user.role in ["manager", "admin"]:
            return get_object_or_404(
                Task,
                pk=pk
            )
        return get_object_or_404(
            Task,
            pk=pk,
            employee=request.user
        )

    def get(self, request, pk):

        task = self.get_task(
            request,
            pk
        )

        serializer = TaskSerializer(task)

        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role == "employee":
            return Response(
                {
                    "error": "Employees cannot modify tasks."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        task = self.get_task(
            request,
            pk
        )
        serializer = TaskSerializer(
            task,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()

            return Response(
                TaskSerializer(task).data,
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
                    "error": "Only admins can delete tasks."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        task = get_object_or_404(
            Task,
            pk=pk
        )
        task.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )