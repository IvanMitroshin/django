from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Collect, Payment


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "full_name"]
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()


class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "user", "collect", "amount", "payment_method", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, data):
        request = self.context.get("request")
        collect = self.instance.collect if self.instance else data.get("collect")

        if not collect or not collect.is_active:
            raise serializers.ValidationError(
                "Сбор завершен, нельзя внести пожертвование"
            )

        if collect.target_amount:
            remaining = collect.target_amount - collect.current_amount
            amount = data.get("amount", self.instance.amount if self.instance else 0)
            if amount > remaining:
                raise serializers.ValidationError(
                    {"amount": f"Сумма превышает необходимые {remaining} руб."}
                )

        return data


class CollectSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    days_left = serializers.IntegerField(read_only=True)
    payments_count = serializers.IntegerField(read_only=True, source="payments.count")

    class Meta:
        model = Collect
        fields = [
            "id",
            "author",
            "title",
            "occasion",
            "description",
            "target_amount",
            "current_amount",
            "cover_image",
            "end_datetime",
            "created_at",
            "updated_at",
            "is_active",
            "progress_percentage",
            "days_left",
            "payments_count",
        ]
        read_only_fields = [
            "id",
            "author",
            "current_amount",
            "created_at",
            "updated_at",
            "is_active",
            "progress_percentage",
            "days_left",
            "payments_count",
        ]

    def validate(self, data):
        from django.utils import timezone

        end_datetime = data.get(
            "end_datetime", getattr(self.instance, "end_datetime", None)
        )
        if end_datetime and end_datetime <= timezone.now():
            raise serializers.ValidationError(
                {"end_datetime": "Дата завершения должна быть в будущем"}
            )

        target_amount = data.get(
            "target_amount", getattr(self.instance, "target_amount", None)
        )
        if target_amount is not None and target_amount <= 0:
            raise serializers.ValidationError(
                {"target_amount": "Целевая сумма должна быть положительной"}
            )

        return data


class CollectDetailSerializer(CollectSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    recent_payments = serializers.SerializerMethodField()

    class Meta(CollectSerializer.Meta):
        fields = CollectSerializer.Meta.fields + ["payments", "recent_payments"]

    def get_recent_payments(self, obj):
        payments = obj.payments.all().order_by("-created_at")[:10]
        return PaymentSerializer(payments, many=True).data


class CollectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = [
            "title",
            "occasion",
            "description",
            "target_amount",
            "cover_image",
            "end_datetime",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user
        return super().create(validated_data)
