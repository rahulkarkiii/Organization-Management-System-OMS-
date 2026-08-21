from django.urls import path

from .views import (
    LeaveListCreateView,
    LeaveDetailView,
    LeaveManagementView,
)


urlpatterns = [
    path(
        "",
        LeaveListCreateView.as_view(),
        name="leave-list-create",
    ),
    path(
        "manage/",
        LeaveManagementView.as_view(),
        name="leave-management",
    ),
    path(
        "manage/<int:pk>/",
        LeaveManagementView.as_view(),
        name="leave-management-detail",
    ),
    path(
        "<int:pk>/",
        LeaveDetailView.as_view(),
        name="leave-detail",
    ),
]