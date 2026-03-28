from django.urls import path
from . import views

app_name = "employees"

urlpatterns = [
    path("", views.guest_employee_list, name="guest_list"),
    path("employees/", views.employee_list, name="full_list"),
    path("employees/add/", views.employee_create, name="add"),
    path("employees/<int:pk>/edit/", views.employee_update, name="edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="delete"),
]