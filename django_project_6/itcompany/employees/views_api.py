from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from datetime import date, timedelta
from django.contrib.auth.models import User
from .models import Employee, Skill
from .serializers import (
    EmployeeSerializer,
    EmployeeDetailSerializer,
    EmployeeCreateUpdateSerializer,
    SkillSerializer,
    WorkplaceSerializer,
)
from workplaces.models import Workplace
from .permissions import EmployeePermissions, WorkplacePermissions


class SimplePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    pagination_class = SimplePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["first_name", "last_name", "description"]
    permission_classes = [EmployeePermissions]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EmployeeDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return EmployeeCreateUpdateSerializer
        return EmployeeSerializer

    def get_queryset(self):
        queryset = Employee.objects.all()

        skill = self.request.query_params.get("skill")
        if skill:
            queryset = queryset.filter(skills__skill__name=skill)

        min_exp = self.request.query_params.get("min_experience")
        if min_exp:
            min_date = date.today() - timedelta(days=int(min_exp))
            queryset = queryset.filter(hire_date__lte=min_date)

        max_exp = self.request.query_params.get("max_experience")
        if max_exp:
            max_date = date.today() - timedelta(days=int(max_exp))
            queryset = queryset.filter(hire_date__gte=max_date)

        return queryset.distinct()

    @action(
        detail=True,
        methods=["get", "put", "patch"],
        permission_classes=[EmployeePermissions],
    )
    def workplace(self, request, pk=None):
        employee = self.get_object()

        if request.method == "GET":
            workplace = getattr(employee, "workplace", None)
            if workplace:
                serializer = WorkplaceSerializer(workplace)
                return Response(serializer.data)
            return Response(
                {"detail": "Рабочее место не назначено"},
                status=status.HTTP_404_NOT_FOUND,
            )

        elif request.method in ["PUT", "PATCH"]:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Требуется авторизация"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            table_number = request.data.get("table_number")
            floor = request.data.get("floor")

            if not table_number:
                return Response(
                    {"error": "Требуется номер стола"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                current_workplace = getattr(employee, "workplace", None)
                workplace, created = Workplace.objects.get_or_create(
                    table_number=table_number, defaults={"floor": floor}
                )

                if current_workplace:
                    current_workplace.employee = None
                    current_workplace.save()

                workplace.employee = employee
                if floor is not None:
                    workplace.floor = floor
                workplace.full_clean()
                workplace.save()

                serializer = WorkplaceSerializer(workplace)
                return Response(serializer.data)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        data = serializer.validated_data
        username = f"{data['last_name']}_{data['first_name']}".lower()
        if User.objects.filter(username=username).exists():
            username = f"{username}_{Employee.objects.count() + 1}"

        user = User.objects.create_user(
            username=username,
            password="default_password_123",  
        )

        serializer.save(user=user)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [EmployeePermissions]
    pagination_class = None
