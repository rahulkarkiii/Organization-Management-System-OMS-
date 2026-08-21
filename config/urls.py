from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/employees/", include("employees.urls")),
    path("api/departments/", include("departments.urls")),
    path("api/tasks/", include("tasks.urls")),
    path("api/attendance/", include("attendance.urls")),
    path("api/leaves/", include("leave.urls")),
    path("api/announcements/", include("announcements.urls")),
    path("api/notifications/", include("notifications.urls")),
]
