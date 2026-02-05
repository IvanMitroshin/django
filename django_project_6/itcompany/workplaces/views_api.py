from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Workplace
from .serializers import WorkplaceSerializer
from employees.permissions import WorkplacePermissions


class WorkplaceViewSet(viewsets.ModelViewSet):
    queryset = Workplace.objects.all()
    serializer_class = WorkplaceSerializer
    permission_classes = [WorkplacePermissions]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["table_number", "employee__last_name", "employee__first_name"]

    @action(detail=False, methods=["get"])
    def free(self, request):
        free_workplaces = Workplace.objects.filter(employee__isnull=True)
        page = self.paginate_queryset(free_workplaces)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(free_workplaces, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def occupied(self, request):
        occupied_workplaces = Workplace.objects.filter(employee__isnull=False)
        page = self.paginate_queryset(occupied_workplaces)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(occupied_workplaces, many=True)
        return Response(serializer.data)
