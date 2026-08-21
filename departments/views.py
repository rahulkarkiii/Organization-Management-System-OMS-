from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer

class DepartmentsListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        departments = Department.objects.select_related("manager").order_by("-created_at")
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admin can create departments."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            department =serializer.save()
            return Response(
                DepartmentSerializer(department).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class DepartmentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_department(self, pk):
        return get_object_or_404(
            Department.objects.select_related("manager"),
            pk=pk
        )

    def get(self, request, pk):
        department = self.get_department(pk)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    def put(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can update departments."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        department = self.get_department(pk)
        serializer = DepartmentSerializer(
            department,
            data=request.data
        )
        if serializer.is_valid():
            department= serializer.save()
            return Response(
                DepartmentSerializer(department).data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        if request.user.role != "admin":
            return Response(
                {
                    "error": "Only admins can update departments."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        department = self.get_department(pk)
        serializer = DepartmentSerializer(
            department,
            data=request.data,
            partial=True,

        )
        if serializer.is_valid():
            department = serializer.save()
            return Response(
                DepartmentSerializer(department).data,
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
                    "error": "Only admins can delete departments."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        department = self.get_department(pk)
        department.delete()
        return Response(
            {"message": "Department deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )