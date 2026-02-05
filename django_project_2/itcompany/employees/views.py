from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee


def home(request):
    employees = Employee.objects.prefetch_related("skills").all()[:6]
    return render(request, "home.html", {"employees": employees})


def employee_list(request):
    employees = Employee.objects.prefetch_related("skills").all()
    return render(request, "employees/employee_list.html", {"employees": employees})


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(
        Employee.objects.prefetch_related("skills", "images"), pk=pk
    )
    return render(request, "employees/employee_detail.html", {"employee": employee})
