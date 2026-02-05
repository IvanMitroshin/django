from django.db import models
from django.contrib.auth.models import User
import os

class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="Пользователь",
    )

    GENDER_CHOICES = [
        ("M", "Мужской"),
        ("F", "Женский"),
    ]

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Skill(models.Model):
    SKILL_CHOICES = [
        ("frontend", "Фронтенд"),
        ("backend", "Бэкенд"),
        ("testing", "Тестирование"),
        ("project_management", "Управление проектами"),
        ("design", "Дизайн"),
        ("devops", "DevOps"),
        ("mobile", "Мобильная разработка"),
        ("databases", "Базы данных"),
        ("ml", "Машинное обучение"),
    ]

    name = models.CharField(max_length=50, choices=SKILL_CHOICES, verbose_name="Навык")

    def __str__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"


class EmployeeSkill(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="Сотрудник",
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name="Навык")
    level = models.IntegerField(
        verbose_name="Уровень освоения",
        choices=[(i, str(i)) for i in range(1, 11)],
        default=1,
    )

    def __str__(self):
        return f"{self.employee} - {self.skill} (уровень {self.level})"

    class Meta:
        verbose_name = "Навык сотрудника"
        verbose_name_plural = "Навыки сотрудников"
        unique_together = ["employee", "skill"]


class EmployeeImage(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Сотрудник",
    )
    image = models.ImageField(
        upload_to="employees/%Y/%m/%d/", verbose_name="Изображение"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядковый номер")

    class Meta:
        verbose_name = "Изображение сотрудника"
        verbose_name_plural = "Изображения сотрудников"
        ordering = ["order"]
        unique_together = ["employee", "order"]

    def __str__(self):
        return f"Изображение {self.order} для {self.employee}"

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
