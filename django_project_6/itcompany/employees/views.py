from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Employee


def home(request):
    total_employees = Employee.objects.count()
    latest_employees = Employee.objects.prefetch_related("skills", "images").all()[
        :4
    ]

    for employee in latest_employees:
        employee.work_days = employee.work_experience_days()
        employee.first_image = employee.images.first()

    context = {
        "employees": latest_employees,
        "total_employees": total_employees,
    }
    return render(request, "home.html", context)


def employee_list(request):
    employees_list = Employee.objects.prefetch_related("skills", "images").all()

    paginator = Paginator(employees_list, 10)
    page = request.GET.get("page", 1)

    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)

    for employee in employees:
        employee.work_days = employee.work_experience_days()
        employee.first_image = employee.images.first()

    return render(request, "employees/employee_list.html", {"employees": employees})


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(
        Employee.objects.prefetch_related("skills", "images"), pk=pk
    )

    all_images = employee.images.all()

    first_image = all_images.first() if all_images.exists() else None

    gallery_images = all_images[1:] if all_images.count() > 1 else []

    work_days = employee.work_experience_days()

    workplace = getattr(employee, "workplace", None)
    table_number = workplace.table_number if workplace else "Не назначен"

    context = {
        "employee": employee,
        "first_image": first_image,
        "gallery_images": gallery_images,
        "work_days": work_days,
        "table_number": table_number,
    }
    return render(request, "employees/employee_detail.html", context)
