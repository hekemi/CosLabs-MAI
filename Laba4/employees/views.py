from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmployeeForm
from .models import Employee


def guest_employee_list(request):
    employees = Employee.objects.all()
    return render(request, "employees/guest_list.html", {"employees": employees})


@login_required
@permission_required("employees.view_employee", raise_exception=True)
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "employees/full_list.html", {"employees": employees})


@login_required
@permission_required("employees.add_employee", raise_exception=True)
def employee_create(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("employees:full_list")
    else:
        form = EmployeeForm()
    return render(request, "employees/form.html", {"form": form, "title": "Добавить сотрудника"})


@login_required
@permission_required("employees.change_employee", raise_exception=True)
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect("employees:full_list")
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "employees/form.html", {"form": form, "title": "Изменить сотрудника"})


@login_required
@permission_required("employees.delete_employee", raise_exception=True)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        return redirect("employees:full_list")
    return render(request, "employees/delete_confirm.html", {"employee": employee})
