"""Native inventory browsing.

maker-cards linked out to a separate application with target="_blank". Here
the listing is rendered in the site's own chrome from the ioref-inventory API,
so "what's in stock" is part of the site rather than a hand-off to another one.

Read-only and public: the API key is read-scoped, and nothing here can write.
"""

from django.core.paginator import Paginator
from django.shortcuts import render

from catalog.models import StockedPart

from .client import InventoryUnavailable, get_part, list_parts

PAGE_SIZE = 60


def _guide_links(part_numbers):
    """Map part numbers to their maker card URL, where one exists.

    Inventory holds many parts with no guide -- consumables, fasteners -- so
    this is a left join, not an assumption.
    """
    stocked = (
        StockedPart.objects.filter(part_number__in=part_numbers)
        .select_related("page")
    )
    # A stocked part points at the component that documents it, so several
    # part numbers can share one guide -- 33 capacitors, one explanation.
    return {
        s.part_number: s.page.url
        for s in stocked
        if s.page.live
    }


def _attach_guides(parts):
    """Annotate API dicts with their guide URL.

    Done here rather than in the template because Django templates cannot
    subscript a dict by a variable key without a custom filter, and one view
    line is cheaper to maintain than a templatetags module.
    """
    guides = _guide_links([p["part_number"] for p in parts])
    for part in parts:
        part["guide_url"] = guides.get(part["part_number"])
    return parts


def inventory_index(request):
    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    page_number = request.GET.get("page", "1")

    try:
        page_number = max(1, int(page_number))
    except ValueError:
        page_number = 1

    context = {
        "search_query": search,
        "status": status,
        "page_title": "Current Inventory",
    }

    try:
        data = list_parts(
            search=search,
            status=status,
            limit=PAGE_SIZE,
            offset=(page_number - 1) * PAGE_SIZE,
        )
    except InventoryUnavailable:
        # Explicitly distinguished from "no results" so an outage does not
        # render as an empty catalogue.
        context["unavailable"] = True
        return render(request, "stock/inventory_index.html", context, status=503)

    results = _attach_guides(data.get("results", []))
    total = data.get("count", len(results))

    # Paginator over a placeholder range: the API has already sliced the page,
    # and this exists only to render the page links consistently with the rest
    # of the site.
    paginator = Paginator(range(total), PAGE_SIZE)
    context.update(
        {
            "parts": results,
            "total": total,
            "page_obj": paginator.get_page(page_number),
        }
    )
    return render(request, "stock/inventory_index.html", context)


def inventory_detail(request, part_number):
    context = {"part_number": part_number}

    try:
        part = get_part(part_number)
    except InventoryUnavailable:
        context["unavailable"] = True
        return render(request, "stock/inventory_detail.html", context, status=503)

    if part is None:
        return render(request, "stock/inventory_detail.html", context, status=404)

    context["part"] = part
    context["page_title"] = part.get("short_name") or part_number
    context["guide_url"] = _guide_links([part_number]).get(part_number)
    return render(request, "stock/inventory_detail.html", context)
