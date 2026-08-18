from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Leave
from .serializers import LeaveSerializer

class LeaveListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaves = Leave.objects.filter(
            employee=request.user,
        ).order_by('-created_at')
        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            leave = serializer.save(
                employee=request.user
            )
            return Response(
                LeaveSerializer(leave).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LeaveDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_leave(self, request, pk):
        return get_object_or_404(
            Leave,
            pk=pk,
            employee=request.user
        )

    def get(self, request, pk):
        leave = self.get_leave(request, pk)
        serializer = LeaveSerializer(leave)
        return Response(serializer.data)

    def put(self, request, pk):
        leave = self.get_leave(request, pk)
        if leave.status != "pending":
            return Response(
                {
                    "error": "Only pending leave requests can be updated."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = LeaveSerializer(
            leave,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(LeaveSerializer(leave).data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def delete(self, request, pk):
        leave = self.get_leave(request, pk)
        if leave.status != "pending":
            return Response(
                {
                    "error": "Only pending leave requests can be cancelled."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        leave.status = "cancelled"
        leave.save()
        return Response(
            {
                "message": "Leaves cancelled successfully."
            },
            status=status.HTTP_200_OK
        )

class LeaveManagementView(APIView):
    permission_classes = [IsAuthenticated]

    def check_manager(self, request):
        if request.user.role not in ["manager", "admin"]:
            return Response(
                {
                    "error": "Only managers and admins can manage leave requests."
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return None

    def get(self, request):
        error = self.check_manager(request)
        if error:
            return error

        leaves = Leave.objects.filter(
            status="pending"
        ).order_by("-created_at")

        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

    def put(self, request, pk):
        error = self.check_manager(request)
        if error:
            return error

        leave = get_object_or_404(
            Leave,
            pk=pk
        )

        if leave.status != "pending":
            return Response(
                {
                    "error": "Only pending leave requests can be reviewed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data.get("status")
        manager_remark = request.data.get("manager_remark", "")

        if new_status not in ["approved", "rejected"]:
            return Response(
                {
                    "error": "Status must be approved or rejected."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        leave.status = new_status
        leave.manager_remark = manager_remark
        leave.save()

        return Response(
            LeaveSerializer(leave).data,
            status=status.HTTP_200_OK
        )