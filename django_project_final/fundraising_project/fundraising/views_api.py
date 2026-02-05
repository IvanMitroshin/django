from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Collect, Payment
from .serializers import (
    CollectSerializer,
    CollectDetailSerializer,
    CollectCreateUpdateSerializer,
    PaymentSerializer,
)
from .permissions import IsAuthorOrReadOnly


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.select_related("author").prefetch_related("payments")
    pagination_class = StandardPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "description"]
    filterset_fields = ["occasion", "author"]
    ordering_fields = ["created_at", "end_datetime", "current_amount"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthorOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CollectDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CollectCreateUpdateSerializer
        return CollectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        status_filter = self.request.query_params.get("status")
        if status_filter == "active":
            queryset = queryset.filter(end_datetime__gt=timezone.now())
        elif status_filter == "completed":
            queryset = queryset.filter(end_datetime__lte=timezone.now())

        return queryset


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    pagination_class = StandardPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["collect", "payment_method"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related(
            "user", "collect"
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
