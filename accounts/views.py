from urllib.parse import urlencode

from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

# Both views are only routed when AUTH_MODE is not "local"; see config/urls.py.
# In local mode Wagtail's own login and logout views stay in place, which is
# what makes `runserver` usable without a Shibboleth service provider.


def _safe_next(request, fallback):
    """Read ?next=, refusing anything that would leave this site.

    The value ends up as a query parameter on the identity provider's URL, so an
    unchecked one is an open redirect with an SSO round trip attached to lend it
    credibility.
    """
    candidate = request.GET.get("next") or request.POST.get("next")
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return fallback


def sso_login(request):
    """Stand in for Wagtail's password form when the IdP owns credentials.

    Wired over `wagtailadmin_login`, so it catches both a direct visit to
    /admin/login/ and Wagtail's own redirects into it.

    The authenticated-but-unauthorised branch is the one that matters. Wagtail's
    `require_admin_access` sends a signed-in user who lacks
    `wagtailadmin.access_admin` to the login URL (`reject_request` in
    wagtail/admin/auth.py). Under Shibboleth that user already has a valid SAML
    session, so bouncing them to the IdP would return them here immediately and
    loop until the browser gives up. What they are missing is a Wagtail group,
    not a login, and the page below tells them so.
    """
    dashboard = reverse("wagtailadmin_home")

    if request.user.is_authenticated:
        if request.user.has_perm("wagtailadmin.access_admin"):
            return redirect(_safe_next(request, dashboard))
        return render(request, "accounts/no_access.html", status=403)

    target = request.build_absolute_uri(_safe_next(request, dashboard))
    return redirect(f"{settings.SSO_LOGIN_URL}?{urlencode({'target': target})}")


@require_POST
def sso_logout(request):
    """End the SAML session, not just the Django one.

    HeaderAuthenticationMiddleware re-establishes the session from headers on
    every request, so `auth.logout()` alone is invisible: the user is signed
    back in on their next click. The Django session is cleared here anyway, in
    case the browser does not follow the redirect.

    POST only, matching Django's own LogoutView. Wagtail's sidebar submits a
    form, and a GET-triggered logout can be fired by any third-party page.
    """
    auth.logout(request)
    return_to = request.build_absolute_uri("/")
    return redirect(f"{settings.SSO_LOGOUT_URL}?{urlencode({'return': return_to})}")
