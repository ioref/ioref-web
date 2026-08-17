from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from accounts import views as accounts_views
from search import views as search_views

# Under SSO, Wagtail's password form cannot authenticate anybody, because
# provisioned accounts have unusable passwords, so it is replaced by a handoff
# to the identity provider. Registered under Wagtail's own URL names and
# paths, so reverse("wagtailadmin_login") and a typed /admin/login/ both reach
# the override; these must come before the wagtailadmin include, which
# resolves first-match-wins.
#
# In local mode they are left alone, which is what keeps runserver usable
# without a Shibboleth service provider in front of it.
sso_urls = [] if settings.AUTH_MODE == "local" else [
    path("admin/login/", accounts_views.sso_login, name="wagtailadmin_login"),
    path("admin/logout/", accounts_views.sso_logout, name="wagtailadmin_logout"),
]

urlpatterns = sso_urls + [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    # Native inventory browsing. maker-cards linked out to a separate app;
    # this renders the same data in the site's own chrome.
    path("inventory/", include("stock.urls")),
    # Image paths the guide markdown refers to; see catalog/views.py.
    path("", include("catalog.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
