"""
URL configuration for itcompany project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from employees import views
from employees.views_api import EmployeeViewSet, SkillViewSet
from workplaces.views_api import WorkplaceViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet)
router.register(r"skills", SkillViewSet)
router.register(r"workplaces", WorkplaceViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
