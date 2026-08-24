"""Compatibility redirects for ioref-web's former inventory browser."""

from urllib.parse import quote

from django.http import HttpResponsePermanentRedirect


INVENTORY_URL = "https://inventory.ioref.org"


def inventory_index(request):
    query = request.GET.urlencode()
    url = f"{INVENTORY_URL}/"
    if query:
        url = f"{url}?{query}"
    return HttpResponsePermanentRedirect(url)


def inventory_detail(request, part_number):
    number = quote(part_number, safe="")
    return HttpResponsePermanentRedirect(f"{INVENTORY_URL}/parts/{number}/")
