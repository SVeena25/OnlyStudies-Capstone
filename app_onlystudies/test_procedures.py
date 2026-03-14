from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from app_onlystudies.models import (
    Appointment,
    BlogPost,
    BlogPostVote,
    Category,
    Notification,
    Task,
)


class FullAppFunctionalityProcedureTest(TestCase):
    """Automated functionality procedures for critical web-app flows."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username="student_a", password="testpass123")
        self.instructor = User.objects.create_user(
            username="instructor_a", password="testpass123")
        instructor_group, _ = Group.objects.get_or_create(name="Instructor")
        self.instructor.groups.add(instructor_group)

        self.category = Category.objects.create(
            name="Procedure", slug="procedure")
        self.post = BlogPost.objects.create(
            title="Procedure Post",
            content="X" * 120,
            author=self.instructor,
            category=self.category,
            slug="procedure-post",
            is_published=True,
        )

    def test_core_public_pages_load_successfully(self):
        for url_name in ["home", "about", "login", "signup", "forum"]:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, url_name)

    def test_restricted_routes_require_authentication(self):
        restricted_urls = [
            reverse("tasks"),
            reverse("add_task"),
            reverse("appointments"),
            reverse("book_appointment"),
            reverse("notifications"),
            reverse("ask_question"),
            reverse("create_blog"),
        ]
        for path in restricted_urls:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse("login"), response.url)

    def test_role_restricted_blog_management(self):
        self.client.login(username="student_a", password="testpass123")
        denied = self.client.get(reverse("create_blog"))
        self.assertEqual(denied.status_code, 302)
        self.assertEqual(denied.url, reverse("home"))

        self.client.logout()
        self.client.login(username="instructor_a", password="testpass123")
        allowed = self.client.get(reverse("create_blog"))
        self.assertEqual(allowed.status_code, 200)


class FullAppUsabilityResponsivenessProcedureTest(TestCase):
    """Automated usability/responsiveness checks on rendered templates."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="uiuser", password="testpass123", first_name="UI")

    def test_base_template_exposes_accessibility_and_responsive_hooks(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, "Skip to main content")
        self.assertContains(response, "navbar-toggler")
        self.assertContains(response, 'aria-controls="navbarNav"')

    def test_home_contains_responsive_layout_markers(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "col-12 col-lg-8")
        self.assertContains(response, "col-12 col-lg-4")
        self.assertContains(response, "aria-live=\"polite\"")

    def test_login_state_is_visible_to_user(self):
        guest_home = self.client.get(reverse("home"))
        self.assertContains(guest_home, "Login")
        self.assertContains(guest_home, "Sign Up")

        self.client.login(username="uiuser", password="testpass123")
        user_home = self.client.get(reverse("home"))
        self.assertContains(user_home, "Welcome")
        self.assertContains(user_home, "Logout")


class FullAppDataManagementProcedureTest(TestCase):
    """Automated data-management procedures for isolation and integrity."""

    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user(
            username="data_a", password="testpass123")
        self.user_b = User.objects.create_user(
            username="data_b", password="testpass123")
        self.category = Category.objects.create(name="Data", slug="data")

        Task.objects.create(
            title="A Task", created_by=self.user_a, priority="medium")
        Task.objects.create(
            title="B Task", created_by=self.user_b, priority="medium")

        Appointment.objects.create(
            title="A Appointment",
            appointment_datetime=timezone.now() + timedelta(days=5),
            created_by=self.user_a,
        )
        Appointment.objects.create(
            title="B Appointment",
            appointment_datetime=timezone.now() + timedelta(days=6),
            created_by=self.user_b,
        )

    def test_user_data_isolation_tasks_and_appointments(self):
        self.client.login(username="data_a", password="testpass123")

        tasks_response = self.client.get(reverse("tasks"))
        self.assertContains(tasks_response, "A Task")
        self.assertNotContains(tasks_response, "B Task")

        appt_response = self.client.get(reverse("appointments"))
        self.assertContains(appt_response, "A Appointment")
        self.assertNotContains(appt_response, "B Appointment")

    def test_notifications_api_is_user_scoped(self):
        Notification.objects.create(
            user=self.user_a,
            title="A",
            message="A",
            notification_type="system")
        Notification.objects.create(
            user=self.user_b,
            title="B",
            message="B",
            notification_type="system")

        self.client.login(username="data_a", password="testpass123")
        response = self.client.get(reverse("notifications_api"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        titles = [item["title"] for item in payload["notifications"]]
        self.assertIn("A", titles)
        self.assertNotIn("B", titles)

    def test_vote_uniqueness_and_appointment_temporal_validation(self):
        post = BlogPost.objects.create(
            title="Vote Integrity",
            content="Y" * 120,
            author=self.user_a,
            category=self.category,
            slug="vote-integrity",
            is_published=True,
        )
        BlogPostVote.objects.create(blog_post=post, user=self.user_a, value=1)
        with self.assertRaises(IntegrityError):
            # Keep the expected DB error inside its own atomic block so the
            # surrounding test transaction remains usable.
            with transaction.atomic():
                BlogPostVote.objects.create(
                    blog_post=post, user=self.user_a, value=1)

        past_appt = Appointment(
            title="Past Invalid",
            appointment_datetime=timezone.now() - timedelta(hours=2),
            created_by=self.user_a,
        )
        with self.assertRaises(ValidationError):
            past_appt.full_clean()
