from django.urls import path
from .views import (
     DepartmentsListCreateView,
     DepartmentDetailView,
)

urlpatterns = [
    path(
        "",
        DepartmentsListCreateView.as_view(),
        name="departments-list_create",
    ),
    path(
        "<int:pk>/",
        DepartmentDetailView.as_view(),
        name="department-detail",
    )
]