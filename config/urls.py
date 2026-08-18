from django.conf import settings
from django.urls import include, path

urlpatterns = [
    # Native inventory browsing. maker-cards linked out to a separate app;
    # this renders the same data in the site's own chrome.
    path("inventory/", include("stock.urls")),
    # Must come last: catalog puts category slugs at the root of the path, so
    # its patterns would otherwise swallow everything above.
    path("", include("catalog.urls")),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
