from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Attendance
from .serializers import AttendanceSerializer

class AttendanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attendance = Attendance.objects.filter(
            employee=request.user
        ).order_by("-date")
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            attendance= serializer.save(
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

class AttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get_attendance(self, request, pk):
        return get_object_or_404(
            Attendance,
            pk=pk,
            employee=request.user
        )
    def get(self, request, pk):
        attendance = self.get_attendance(request, pk)
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    def put(self, request, pk):
        attendance = self.get_attendance(request, pk)
        serializer = AttendanceSerializer(
            attendance,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                AttendanceSerializer(attendance).data
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def delete(self, request, pk):
        attendance = self.get_attendance(request, pk)
        attendance.delete()
        return Response(
            {"message": "Attendance deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )