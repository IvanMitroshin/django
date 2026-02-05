from django.contrib import admin
from django.utils.html import format_html
from .models import Collect, Payment
import os

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ["created_at"]
    fields = ["user", "amount", "payment_method", "created_at"]
    can_delete = False


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "occasion",
        "current_amount",
        "target_amount",
        "progress_bar",
        "days_left_display",
        "is_active_display",
        "created_at",
    )

    list_filter = ("occasion", "created_at", "end_datetime")
    search_fields = ("title", "description", "author__username")
    readonly_fields = ("current_amount", "created_at", "updated_at")
    inlines = [PaymentInline]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("author", "title", "occasion", "description")},
        ),
        ("Финансы", {"fields": ("target_amount", "current_amount")}),
        ("Визуальное оформление", {"fields": ("cover_image",)}),
        (
            "Временные метки",
            {
                "fields": ("end_datetime", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def progress_bar(self, obj):
        if not obj.target_amount:
            return "∞"
        percent = obj.progress_percentage
        color = "green" if percent >= 100 else "orange" if percent >= 50 else "red"
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 3px;'
            'text-align: center; color: white; font-weight: bold; line-height: 20px;">'
            "{}%</div></div>",
            min(100, percent),
            color,
            int(percent),
        )

    progress_bar.short_description = "Прогресс"

    def days_left_display(self, obj):
        days = obj.days_left
        color = "green" if days > 7 else "orange" if days > 3 else "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} д.</span>', color, days
        )

    days_left_display.short_description = "Осталось"

    def is_active_display(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            "green" if obj.is_active else "red",
            "Активен" if obj.is_active else "Завершен",
        )

    is_active_display.short_description = "Статус"

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.cover_image:
                if os.path.isfile(obj.cover_image.path):
                    os.remove(obj.cover_image.path)
        super().delete_queryset(request, queryset)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "collect",
        "amount",
        "payment_method",
        "created_at",
    )

    list_filter = ("payment_method", "created_at")
    search_fields = ("user__username", "collect__title")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Основная информация", {"fields": ("user", "collect", "amount")}),
        ("Дополнительно", {"fields": ("payment_method", "created_at")}),
    )

    def delete_model(self, request, obj):
        collect = obj.collect
        collect.current_amount -= obj.amount
        collect.save(update_fields=["current_amount"])
        super().delete_model(request, obj)
