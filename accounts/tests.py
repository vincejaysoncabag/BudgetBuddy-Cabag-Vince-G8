from django.test import TestCase
from django.urls import reverse

from .models import User

GOOD = {"first_name": "Ana", "last_name": "Cruz", "email": "Ana@X.com",
        "password1": "Budget123", "password2": "Budget123"}


def make_user(email="u@x.com", role=User.Role.USER):
    return User.objects.create_user(email=email, password="Budget123", first_name="U", last_name="Ser", role=role)


class AccountTests(TestCase):
    def test_register_hashes_password_and_blocks_duplicate_email(self):
        resp = self.client.post(reverse("register"), GOOD)
        self.assertRedirects(resp, reverse("login"))
        user = User.objects.get(email="ana@x.com")
        self.assertNotEqual(user.password, "Budget123")
        resp = self.client.post(reverse("register"), {**GOOD, "email": "ANA@x.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_register_rejects_weak_or_mismatched_password(self):
        for p1, p2 in [("abcdefgh", "abcdefgh"), ("Budget123", "Budget124"), ("a1", "a1")]:
            resp = self.client.post(reverse("register"), {**GOOD, "password1": p1, "password2": p2})
            self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_invalid_login_shows_error(self):
        make_user()
        resp = self.client.post(reverse("login"), {"username": "u@x.com", "password": "wrong"})
        self.assertContains(resp, "Incorrect email or password")

    def test_login_routes_by_role(self):
        make_user("u@x.com")
        make_user("a@x.com", User.Role.ADMIN)
        self.client.post(reverse("login"), {"username": "U@x.com", "password": "Budget123"})
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("user_dashboard"))
        self.client.post(reverse("logout"))
        self.client.post(reverse("login"), {"username": "a@x.com", "password": "Budget123"})
        self.assertRedirects(self.client.get(reverse("dashboard")), reverse("admin_dashboard"))

    def test_protected_pages_redirect_to_login(self):
        for name in ["dashboard", "user_dashboard", "admin_dashboard", "profile"]:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 302)
            self.assertTrue(resp.url.startswith(reverse("login")))

    def test_roles_cannot_open_each_others_dashboard(self):
        self.client.force_login(make_user("u@x.com"))
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 403)
        self.client.force_login(make_user("a@x.com", User.Role.ADMIN))
        self.assertEqual(self.client.get(reverse("user_dashboard")).status_code, 403)

    def test_profile_update_and_email_uniqueness(self):
        make_user("taken@x.com")
        self.client.force_login(make_user("me@x.com"))
        self.client.post(reverse("profile"), {"first_name": "New", "last_name": "Name", "email": "me@x.com"})
        self.assertEqual(User.objects.get(email="me@x.com").first_name, "New")
        resp = self.client.post(reverse("profile"), {"first_name": "N", "last_name": "N", "email": "TAKEN@x.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(User.objects.get(email="me@x.com").email, "me@x.com")
