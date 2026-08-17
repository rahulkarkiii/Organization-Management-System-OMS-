from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from employees.models import Employee
from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tasks= Task.objects.filter(
            employee=request.user
        ).order_by("-created_at")

        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            task = serializer.save(employee=request.user)

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
        return get_object_or_404(
            Task,
            pk=pk,
            employee=request.user
        )

    def get(self, request, pk):
        task = self.get_task(request, pk)

        serializer = TaskSerializer(task)

        return Response(serializer.data)

    def put(self, request, pk):
        task = self.get_task(request, pk)

        serializer = TaskSerializer(
            task,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        task = self.get_task(request, pk)

        task.delete()

        return Response(
            {"message": "Task deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )