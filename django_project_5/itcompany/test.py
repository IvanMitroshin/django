from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date

from employees.models import Employee, Skill, EmployeeSkill
from workplaces.models import Workplace


class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.employee = Employee.objects.create(
            user=self.user,
            gender="M",
            first_name="Иван",
            last_name="Иванов",
            middle_name="Иванович",
            description="Тестовый сотрудник",
            hire_date=date(2020, 1, 1),
        )

        self.skill_dev = Skill.objects.create(name="backend")
        self.skill_tester = Skill.objects.create(name="testing")

        self.employee_skill_dev = EmployeeSkill.objects.create(
            employee=self.employee, skill=self.skill_dev, level=8
        )

        self.client = Client()


class UrlTests(BaseTestCase):

    def test_home_url(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_employee_list_url(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employees/employee_list.html")

    def test_employee_detail_url_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("employee_detail", args=[self.employee.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employees/employee_detail.html")

    def test_employee_detail_url_unauthenticated(self):
        response = self.client.get(reverse("employee_detail", args=[self.employee.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("?next=/employees/", response.url)

    def test_admin_url(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        admin_user = User.objects.create_superuser(
            username="admin", password="admin123", email="admin@test.com"
        )
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)


class ContextTests(BaseTestCase):

    def setUp(self):
        super().setUp()

        for i in range(5):
            Employee.objects.create(
                user=User.objects.create_user(
                    username=f"testuser{i}", password="testpass123"
                ),
                gender="F" if i % 2 == 0 else "M",
                first_name=f"Тест{i}",
                last_name=f"Тестов{i}",
                description=f"Описание {i}",
                hire_date=date(2020 + i, 1, 1),
            )

    def test_home_context(self):
        response = self.client.get(reverse("home"))

        self.assertIn("employees", response.context)
        self.assertIn("total_employees", response.context)

        self.assertEqual(
            response.context["total_employees"], 6
        ) 

        self.assertLessEqual(len(response.context["employees"]), 4)

        employee = response.context["employees"][0]
        self.assertTrue(hasattr(employee, "work_days"))
        self.assertTrue(hasattr(employee, "first_image"))

    def test_employee_list_context(self):
        response = self.client.get(reverse("employee_list"))

        self.assertIn("employees", response.context)

        self.assertEqual(response.context["employees"].paginator.per_page, 10)

        for employee in response.context["employees"]:
            self.assertTrue(hasattr(employee, "work_days"))
            self.assertTrue(hasattr(employee, "first_image"))

    def test_employee_detail_context_authenticated(self):
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("employee_detail", args=[self.employee.pk]))

        self.assertIn("employee", response.context)
        self.assertIn("first_image", response.context)
        self.assertIn("gallery_images", response.context)
        self.assertIn("work_days", response.context)
        self.assertIn("table_number", response.context)

        self.assertEqual(response.context["employee"], self.employee)
        self.assertEqual(
            response.context["work_days"], (date.today() - date(2020, 1, 1)).days
        )
        self.assertEqual(response.context["table_number"], "Не назначен")

    def test_employee_work_experience(self):

        test_date = date(2022, 6, 15)
        days_expected = (date.today() - test_date).days

        employee = Employee.objects.create(
            user=User.objects.create_user(
                username="experience_test", password="testpass123"
            ),
            gender="M",
            first_name="Тест",
            last_name="Стаж",
            description="Тест стажа",
            hire_date=test_date,
        )

        self.assertEqual(employee.work_experience_days(), days_expected)


class ValidatorTests(BaseTestCase):

    def setUp(self):
        super().setUp()

        self.user2 = User.objects.create_user(
            username="testuser2", password="testpass123"
        )

        self.employee2 = Employee.objects.create(
            user=self.user2,
            gender="Ж",
            first_name="Мария",
            last_name="Петрова",
            description="Второй сотрудник",
            hire_date=date(2021, 1, 1),
        )

        self.workplace1 = Workplace.objects.create(table_number="101", floor=1)
        self.workplace2 = Workplace.objects.create(table_number="102", floor=1)

    def test_validator_allows_same_role_neighbors(self):
        EmployeeSkill.objects.filter(employee=self.employee).delete()
        EmployeeSkill.objects.create(
            employee=self.employee, skill=self.skill_dev, level=8
        )

        EmployeeSkill.objects.create(
            employee=self.employee2, skill=self.skill_dev, level=9
        )

        self.workplace1.employee = self.employee
        self.workplace2.employee = self.employee2

        try:
            self.workplace1.save()
            self.workplace2.save()
            success = True
        except Exception as e:
            print(f"Ошибка: {e}")
            success = False

        self.assertTrue(success, "Разработчики должны иметь возможность сидеть рядом")

    def test_validator_blocks_developer_tester_neighbors(self):
        skill_tester = Skill.objects.create(name="testing")

        EmployeeSkill.objects.filter(employee=self.employee).delete()
        EmployeeSkill.objects.create(
            employee=self.employee, skill=self.skill_dev, level=8
        )

        EmployeeSkill.objects.create(
            employee=self.employee2, skill=skill_tester, level=7
        )

        self.workplace1.employee = self.employee
        self.workplace1.save()

        self.workplace2.employee = self.employee2

        with self.assertRaises(Exception) as context:
            self.workplace2.save()

        self.assertIn(
            "Тестировщики и разработчики не могут сидеть за соседними столами",
            str(context.exception),
        )

    def test_validator_allows_non_adjacent_tables(self):
        workplace3 = Workplace.objects.create(table_number="103", floor=1)

        skill_tester = Skill.objects.create(name="testing")

        EmployeeSkill.objects.filter(employee=self.employee).delete()
        EmployeeSkill.objects.create(
            employee=self.employee, skill=self.skill_dev, level=8
        )

        EmployeeSkill.objects.create(
            employee=self.employee2, skill=skill_tester, level=7
        )

        self.workplace1.employee = self.employee
        workplace3.employee = self.employee2

        try:
            self.workplace1.save()
            workplace3.save()
            success = True
        except Exception as e:
            print(f"Ошибка: {e}")
            success = False

        self.assertTrue(
            success, "Разработчики и тестировщики могут сидеть за несоседними столами"
        )
