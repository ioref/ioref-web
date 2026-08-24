from django.conf import settings
from django.urls import include, path

urlpatterns = [
    # Compatibility only. Inventory browsing now belongs to ioref-inventory.
    path("inventory/", include("stock.urls")),
    # Must come last: catalog puts category slugs at the root of the path, so
    # its patterns would otherwise swallow everything above.
    path("", include("catalog.urls")),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
