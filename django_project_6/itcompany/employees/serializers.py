from rest_framework import serializers
from .models import Employee, Skill
from workplaces.models import Workplace


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ["id", "user"]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    work_experience_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "gender",
            "description",
            "hire_date",
            "work_experience_days",
        ]
        read_only_fields = ["id", "work_experience_days"]


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "gender",
            "description",
            "hire_date",
        ]


class WorkplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workplace
        fields = "__all__"
        read_only_fields = ["id"]
