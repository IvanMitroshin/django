from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Collect(models.Model):
    OCCASION_CHOICES = [
        ("birthday", "День рождения"),
        ("wedding", "Свадьба"),
        ("graduation", "Выпускной"),
        ("medical", "Лечение"),
        ("charity", "Благотворительность"),
        ("event", "Мероприятие"),
        ("other", "Другое"),
    ]

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор сбора"
    )

    title = models.CharField(max_length=200, verbose_name="Название сбора")
    occasion = models.CharField(
        max_length=20, choices=OCCASION_CHOICES, verbose_name="Повод"
    )
    description = models.TextField(verbose_name="Описание")
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Целевая сумма",
    )
    current_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Собрано"
    )
    cover_image = models.ImageField(
        upload_to="collects/covers/%Y/%m/%d/",
        verbose_name="Обложка",
        null=True,
        blank=True,
    )
    end_datetime = models.DateTimeField(verbose_name="Дата и время завершения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"{self.title} (автор: {self.author.username})"

    @property
    def is_active(self):
        return timezone.now() < self.end_datetime

    @property
    def progress_percentage(self):
        if not self.target_amount:
            return 0
        try:
            return float(self.current_amount) / float(self.target_amount) * 100
        except (TypeError, ValueError, ZeroDivisionError):
            return 0

    @property
    def days_left(self):
        delta = self.end_datetime - timezone.now()
        return max(0, delta.days)

    def clean(self):
        current_amount = self.current_amount
        if hasattr(current_amount, "value"):
            return

        if self.target_amount is not None and self.target_amount <= 0:
            raise ValidationError(
                {"target_amount": "Целевая сумма должна быть положительной"}
            )

        if self.end_datetime <= timezone.now():
            raise ValidationError(
                {"end_datetime": "Дата завершения должна быть в будущем"}
            )

        if current_amount < 0:
            raise ValidationError(
                {"current_amount": "Собранная сумма не может быть отрицательной"}
            )

        if self.target_amount and current_amount > self.target_amount:
            self.current_amount = self.target_amount

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("card", "Банковская карта"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )

    collect = models.ForeignKey(
        Collect,
        on_delete=models.CASCADE,
        verbose_name="Сбор",
        related_name="payments",
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="card",
        verbose_name="Способ оплаты",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self):
        return f"{self.user.username} - {self.amount} руб. ({self.created_at.date()})"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({"amount": "Сумма должна быть положительной"})

        if not self.collect.is_active:
            raise ValidationError("Сбор завершен, нельзя внести пожертвование")

        if self.collect.target_amount:
            remaining = float(self.collect.target_amount) - float(
                self.collect.current_amount
            )
            if float(self.amount) > remaining:
                raise ValidationError(
                    {"amount": f"Сумма превышает необходимые {remaining:.2f} руб."}
                )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            self.full_clean()

        super().save(*args, **kwargs)

        if is_new:
            from django.db.models import F
            self.collect.current_amount = F("current_amount") + self.amount
            self.collect.save(update_fields=["current_amount"])
            self.collect.refresh_from_db()

    def delete(self, *args, **kwargs):
        from django.db.models import F
        self.collect.current_amount = F("current_amount") - self.amount
        self.collect.save(update_fields=["current_amount"])
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
