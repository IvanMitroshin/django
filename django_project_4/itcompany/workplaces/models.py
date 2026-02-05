from django.db import models
from django.core.exceptions import ValidationError
from employees.models import Employee, EmployeeSkill


def validate_table_number(value):
    if not value:
        raise ValidationError("Номер стола не может быть пустым")
    if not value.isdigit():
        raise ValidationError("Номер стола может содержать только цифры")


class Workplace(models.Model):
    table_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Номер стола",
        validators=[validate_table_number],
    )
    floor = models.IntegerField(null=True, blank=True, verbose_name="Этаж")

    employee = models.OneToOneField(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workplace",
        verbose_name="Сотрудник",
    )

    def __str__(self):
        if self.employee:
            return f"Стол {self.table_number} - {self.employee}"
        return f"Стол {self.table_number} (свободен)"

    def clean(self):
        super().clean()

        if not self.employee:
            return

        employee_skills = EmployeeSkill.objects.filter(employee=self.employee)
        is_tester = False
        is_developer = False

        for skill in employee_skills:
            if skill.skill.is_tester:
                is_tester = True
            if skill.skill.is_developer:
                is_developer = True

        if not (is_tester or is_developer):
            return

        table_num = int(self.table_number)

        for offset in (-1, 1):
            neighbor_num = str(table_num + offset)

            neighbor = Workplace.objects.filter(table_number=neighbor_num).first()
            if not neighbor or not neighbor.employee:
                continue

            neighbor_skills = EmployeeSkill.objects.filter(employee=neighbor.employee)
            neighbor_is_tester = False
            neighbor_is_developer = False

            for skill in neighbor_skills:
                if skill.skill.is_tester:
                    neighbor_is_tester = True
                if skill.skill.is_developer:
                    neighbor_is_developer = True
                    
            if (is_tester and neighbor_is_developer) or (
                is_developer and neighbor_is_tester
            ):
                raise ValidationError(
                    f"Тестировщики и разработчики не могут сидеть за соседними столами. "
                    f"Соседний стол {neighbor_num} занят {neighbor.employee}."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
        ordering = ["table_number"]
