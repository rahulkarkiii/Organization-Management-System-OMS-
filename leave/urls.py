from django.urls import path
from .views import (
    LeaveListCreateView,
    LeaveDetailView, LeaveManagementView,
)
urlpatterns = [
    path(
        "",
        LeaveListCreateView.as_view(),
        name="Leave-List-Create"
    ),
    path(
        "manage/",
        LeaveManagementView.as_view(),
        name="Leave-Management"
    ),
    path(
        "manage/<int:pk>/",
        LeaveManagementView.as_view(),
        name="Leave-Management-Detail"
    ),
    path(
        "<int:pk>/",
        LeaveDetailView.as_view(),
        name="Leave-Detail"
    )
]