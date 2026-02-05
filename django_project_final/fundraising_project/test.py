from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from fundraising.models import Collect, Payment


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_collect_creation(self):
        collect = Collect.objects.create(
            author=self.user,
            title="День рождения",
            occasion="birthday",
            description="Сбор на подарок",
            target_amount=5000,
            end_datetime=timezone.now() + timedelta(days=30),
        )

        self.assertEqual(collect.title, "День рождения")
        self.assertEqual(collect.occasion, "birthday")
        self.assertEqual(collect.current_amount, 0)
        self.assertTrue(collect.is_active)
        self.assertGreater(collect.days_left, 0)

    def test_collect_without_target(self):
        collect = Collect.objects.create(
            author=self.user,
            title="Благотворительность",
            occasion="charity",
            description="Помощь",
            target_amount=None,
            end_datetime=timezone.now() + timedelta(days=60),
        )

        self.assertIsNone(collect.target_amount)
        self.assertEqual(collect.progress_percentage, 0)

    def test_payment_creation_simple(self):
        collect = Collect.objects.create(
            author=self.user,
            title="На лечение",
            occasion="medical",
            description="Сбор на лечение",
            target_amount=100000,
            end_datetime=timezone.now() + timedelta(days=90),
        )

        collect.current_amount = 5000
        collect.save()

        payment = Payment(
            user=self.user, collect=collect, amount=5000, payment_method="card"
        )

        self.assertEqual(payment.amount, 5000)
        self.assertEqual(payment.payment_method, "card")
        self.assertEqual(collect.current_amount, 5000)


class APITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="apipass123")

    def test_swagger_accessible(self):
        from django.test import Client
        client = Client()
        response = client.get("/swagger/")
        self.assertEqual(response.status_code, 200)

    def test_admin_accessible(self):
        from django.test import Client
        client = Client()
        response = client.get("/admin/")
        self.assertIn(response.status_code, [200, 302])

    def test_api_endpoints_exist(self):
        from django.test import Client
        client = Client()
        endpoints = ["/api/collects/", "/api/payments/", "/api/token/"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            self.assertNotEqual(response.status_code, 404)


class SettingsTests(TestCase):

    def test_cors_enabled(self):
        from django.conf import settings
        self.assertTrue(hasattr(settings, "CORS_ALLOW_ALL_ORIGINS"))

    def test_swagger_configured(self):
        from django.conf import settings
        self.assertIn("drf_yasg", settings.INSTALLED_APPS)
        self.assertIn("SWAGGER_SETTINGS", dir(settings))

    def test_jwt_configured(self):
        from django.conf import settings
        self.assertIn("rest_framework_simplejwt", settings.INSTALLED_APPS)
        self.assertIn("SIMPLE_JWT", dir(settings))


class BasicValidationTests(TestCase):
  
    def setUp(self):
        self.user = User.objects.create_user(
            username="validator", password="testpass123"
        )

    def test_collect_future_date(self):
        collect = Collect.objects.create(
            author=self.user,
            title="Валидный сбор",
            occasion="birthday",
            description="Тест",
            target_amount=1000,
            end_datetime=timezone.now() + timedelta(days=1),
        )

        self.assertGreater(collect.end_datetime, timezone.now())

    def test_positive_target_amount(self):
        collect = Collect.objects.create(
            author=self.user,
            title="Сбор с положительной суммой",
            occasion="charity",
            description="Тест",
            target_amount=1000,  
            end_datetime=timezone.now() + timedelta(days=10),
        )

        self.assertGreater(collect.target_amount, 0)
