from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Department
from .serializers import DepartmentSerializer

class DepartmentsListCreateView(APIView):
    def get(self, request):
        departments = Department.objects.all().order_by("-created_at")
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class DepartmentDetailView(APIView):
    def get_department(self, pk):
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return None

    def get(self, request, pk):
        department = self.get_department(pk)
        if department is None:
            return Response(
                {"error": "Department not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = DepartmentSerializer(department)
        return Response(serializer.data)

    def put(self, request, pk):
        department = self.get_department(pk)
        if department is None:
            return Response(
                {"error": "Department not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = DepartmentSerializer(
            department,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        department = self.get_department(pk)
        if department is None:
            return Response(
                {"error": "Department not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        department.delete()
        return Response(
            {"message": "Department deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )