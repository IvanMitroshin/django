from django.contrib import admin
from .models import Workplace


class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ("table_number", "employee", "floor")
    list_filter = ("floor",)
    search_fields = ("table_number", "employee__last_name", "employee__first_name")
    list_select_related = ("employee",)

    fieldsets = (
        ("Основная информация", {"fields": ("table_number", "employee")}),
        ("Дополнительная информация", {"fields": ("floor",), "classes": ("collapse",)}),
    )


admin.site.register(Workplace, WorkplaceAdmin)
