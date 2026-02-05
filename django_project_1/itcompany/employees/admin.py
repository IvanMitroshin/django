from django.contrib import admin
from .models import Employee, Skill, EmployeeSkill


class EmployeeSkillInline(admin.TabularInline):
    model = EmployeeSkill
    extra = 1


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "middle_name", "gender")
    inlines = [EmployeeSkillInline]


class SkillAdmin(admin.ModelAdmin):
    list_display = ("get_name_display",)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Skill, SkillAdmin)

