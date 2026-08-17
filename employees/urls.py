from django.urls import path
from .views import (
    EmployeesListCreateView,
    EmployeeDetailView,
)

urlpatterns = [
    path(
        "",
        EmployeesListCreateView.as_view(),
        name="employees-list-create",
    ),
    path(
        "<int:pk>/",
        EmployeeDetailView.as_view(),
        name="employee-detail",
    ),

]