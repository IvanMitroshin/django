from django.db import models
from employees.models import Employee


class Workplace(models.Model):
    table_number = models.CharField(
        max_length=20, unique=True, verbose_name="Номер стола"
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

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
