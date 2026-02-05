from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import CollectViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r"api/collects", CollectViewSet, basename="collect")
router.register(r"api/payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
]
