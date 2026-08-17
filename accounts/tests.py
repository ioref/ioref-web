from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from accounts import views
from accounts.backends import TrustedHeaderBackend

User = get_user_model()

SHIB = {
    "AUTH_MODE": "shib",
    "AUTHENTICATION_BACKENDS": [
        "accounts.backends.TrustedHeaderBackend",
        "django.contrib.auth.backends.ModelBackend",
    ],
    "MIDDLEWARE": [
        *settings.MIDDLEWARE,
        "accounts.middleware.HeaderAuthenticationMiddleware",
    ],
    "REMOTE_USER_HEADER": "HTTP_EPPN",
    "REMOTE_USER_EMAIL_HEADER": "HTTP_MAIL",
    "REMOTE_USER_NAME_HEADER": "HTTP_DISPLAYNAME",
    "REMOTE_USER_SUBJECT_HEADER": "HTTP_PERSISTENT_ID",
}


def grant_admin_access(user):
    user.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="wagtailadmin", codename="access_admin"
        )
    )
    # Permissions are cached on the instance after the first check.
    return User.objects.get(pk=user.pk)


class TrustedHeaderBackendTests(TestCase):
    """Identity resolution for AUTH_MODE=shib.

    CMU releases eppn as user@andrew.cmu.edu. Where a permanent subject id is
    also released it wins, because eppn can be reassigned. Kept in step with
    ioref-inventory's copy of these tests: the two applications resolve the
    same people from the same assertions and must not disagree about who
    someone is.
    """

    def setUp(self):
        self.backend = TrustedHeaderBackend()

    def auth(self, eppn, subject_id=None, **attrs):
        return self.backend.authenticate(
            None,
            remote_user=eppn,
            attributes={"subject_id": subject_id or "", **attrs},
        )

    def test_provisions_on_first_sight_without_permissions(self):
        user = self.auth("merichar@andrew.cmu.edu", email="merichar@andrew.cmu.edu")
        self.assertEqual(user.username, "merichar@andrew.cmu.edu")
        self.assertTrue(user.is_active)
        # SSO asserts identity, never authorisation.
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.groups.count(), 0)
        self.assertFalse(user.has_perm("wagtailadmin.access_admin"))
        # Must not be able to sign in through Wagtail's form.
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.idp, "shib")

    def test_eppn_is_lowercased(self):
        user = self.auth("MeRiChaR@Andrew.CMU.edu")
        self.assertEqual(user.username, "merichar@andrew.cmu.edu")

    def test_repeat_login_reuses_account(self):
        first = self.auth("merichar@andrew.cmu.edu")
        second = self.auth("merichar@andrew.cmu.edu")
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(User.objects.count(), 1)

    def test_subject_id_survives_an_eppn_change(self):
        """A rename must follow the person, not orphan their page history."""
        before = self.auth("oldname@andrew.cmu.edu", subject_id="urn:cmu:0001")
        after = self.auth("newname@andrew.cmu.edu", subject_id="urn:cmu:0001")

        self.assertEqual(before.pk, after.pk)
        self.assertEqual(User.objects.count(), 1)
        after.refresh_from_db()
        self.assertEqual(after.username, "newname@andrew.cmu.edu")

    def test_recycled_eppn_does_not_inherit_the_old_account(self):
        """Different subject, same eppn: a new person, so a new account.

        Matching on eppn alone would get this wrong: someone leaves, their
        eppn is reissued, and the newcomer silently inherits their editor
        rights along with their history.
        """
        original = self.auth("shared@andrew.cmu.edu", subject_id="urn:cmu:0001")
        original.username = "departed@andrew.cmu.edu"
        original.save()

        newcomer = self.auth("shared@andrew.cmu.edu", subject_id="urn:cmu:0002")
        self.assertNotEqual(original.pk, newcomer.pk)
        self.assertEqual(User.objects.count(), 2)

    def test_subject_id_is_backfilled_onto_existing_accounts(self):
        """Accounts predating subject-id release adopt it on next login."""
        existing = self.auth("merichar@andrew.cmu.edu")
        self.assertIsNone(existing.subject_id)

        again = self.auth("merichar@andrew.cmu.edu", subject_id="urn:cmu:0001")
        self.assertEqual(existing.pk, again.pk)
        again.refresh_from_db()
        self.assertEqual(again.subject_id, "urn:cmu:0001")

    def test_falls_back_to_eppn_when_no_subject_released(self):
        first = self.auth("merichar@andrew.cmu.edu")
        second = self.auth("merichar@andrew.cmu.edu")
        self.assertEqual(first.pk, second.pk)

    def test_attributes_refresh_but_group_membership_does_not(self):
        user = self.auth("merichar@andrew.cmu.edu", email="old@cmu.edu")
        user = grant_admin_access(user)

        user = self.auth(
            "merichar@andrew.cmu.edu",
            email="new@cmu.edu",
            display_name="Meg Richards",
        )
        self.assertEqual(user.email, "new@cmu.edu")
        self.assertEqual(user.first_name, "Meg")
        self.assertEqual(user.last_name, "Richards")
        # Granting access is a manual act in the Wagtail user interface; a
        # login must not revoke it.
        self.assertTrue(
            User.objects.get(pk=user.pk).has_perm("wagtailadmin.access_admin")
        )

    def test_empty_header_authenticates_nobody(self):
        self.assertIsNone(self.auth(""))
        self.assertIsNone(self.backend.authenticate(None, remote_user=None))
        self.assertEqual(User.objects.count(), 0)


@override_settings(**SHIB)
class HeaderAuthenticationMiddlewareTests(TestCase):
    """The session is derived from the proxy's headers, request by request."""

    def setUp(self):
        # A plain Django view, so the test does not depend on seeded page tree.
        self.url = reverse("search")

    def test_public_pages_need_no_headers(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(User.objects.count(), 0)

    def test_headers_sign_the_user_in_and_provision_them(self):
        response = self.client.get(
            self.url,
            HTTP_EPPN="merichar@andrew.cmu.edu",
            HTTP_MAIL="merichar@andrew.cmu.edu",
            HTTP_DISPLAYNAME="Meg Richards",
            HTTP_PERSISTENT_ID="urn:cmu:0001",
        )
        user = response.wsgi_request.user
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, "merichar@andrew.cmu.edu")
        self.assertEqual(user.subject_id, "urn:cmu:0001")

    def test_session_is_dropped_when_the_headers_stop(self):
        """A Shibboleth logout must not leave a live Django session behind."""
        self.client.get(self.url, HTTP_EPPN="merichar@andrew.cmu.edu")

        response = self.client.get(self.url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_a_different_eppn_replaces_the_session(self):
        self.client.get(self.url, HTTP_EPPN="first@andrew.cmu.edu")

        response = self.client.get(self.url, HTTP_EPPN="second@andrew.cmu.edu")
        self.assertEqual(
            response.wsgi_request.user.username, "second@andrew.cmu.edu"
        )


@override_settings(**SHIB)
class SsoLoginViewTests(TestCase):
    """The stand-in for Wagtail's password form.

    Called directly rather than over a URL: the override in config/urls.py is
    registered at import time from AUTH_MODE, which override_settings cannot
    reach.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.dashboard = reverse("wagtailadmin_home")

    def get(self, user, query=""):
        request = self.factory.get(f"/admin/login/{query}")
        request.user = user
        return views.sso_login(request)

    def test_anonymous_visitor_is_handed_to_the_identity_provider(self):
        response = self.get(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.SSO_LOGIN_URL))
        self.assertIn("target=", response.url)

    def test_editor_is_sent_on_to_the_dashboard(self):
        user = grant_admin_access(User.objects.create(username="e@andrew.cmu.edu"))
        response = self.get(user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.dashboard)

    def test_signed_in_without_a_group_gets_a_page_not_a_redirect_loop(self):
        """The case that would otherwise bounce forever.

        Wagtail sends an authenticated user with no `access_admin` to the login
        URL. Their SAML session is fine, so redirecting them to the IdP would
        return them straight here again.
        """
        user = User.objects.create(username="visitor@andrew.cmu.edu")
        response = self.get(user)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "visitor@andrew.cmu.edu", status_code=403)

    def test_next_is_honoured_for_local_urls(self):
        user = grant_admin_access(User.objects.create(username="e@andrew.cmu.edu"))
        response = self.get(user, "?next=/admin/pages/")
        self.assertEqual(response.url, "/admin/pages/")

    def test_offsite_next_is_discarded(self):
        """?next= reaches the IdP as a query parameter; unchecked it is an open
        redirect wearing a CMU login page as camouflage."""
        response = self.get(AnonymousUser(), "?next=https://evil.example/")
        self.assertNotIn("evil.example", response.url)


@override_settings(**SHIB)
class SsoLogoutViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def post(self):
        request = self.factory.post("/admin/logout/")
        request.user = User.objects.create(username="e@andrew.cmu.edu")
        request.session = self.client.session
        return views.sso_logout(request)

    def test_logout_ends_the_saml_session_too(self):
        """Clearing only the Django session is a no-op: the middleware signs
        the same person back in from the headers on their next request."""
        response = self.post()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.SSO_LOGOUT_URL))
        self.assertIn("return=", response.url)

    def test_get_is_rejected(self):
        request = self.factory.get("/admin/logout/")
        request.user = AnonymousUser()
        self.assertEqual(views.sso_logout(request).status_code, 405)
