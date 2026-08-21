"""Native inventory browsing.

maker-cards linked out to a separate application with target="_blank". Here
the listing is rendered in the site's own chrome from the ioref-inventory API,
so "what's in stock" is part of the site rather than a hand-off to another one.

Read-only and public: the API key is read-scoped, and nothing here can write.
"""

from django.core.paginator import Paginator
from django.shortcuts import render

from catalog.content import get_catalogue

from .client import InventoryUnavailable, get_part, list_parts

PAGE_SIZE = 60


def _guide_for(part, catalogue, by_number):
    """The guide that documents one part dict from the inventory API.

    Group first: most guides are group-driven now, and the part dict already
    carries its group (list_parts() and get_part() both embed it), so this
    costs nothing extra -- no second API call to find out. Falls back to a
    guide that lists the number by hand, for the couple of parts inventory
    has not grouped yet.
    """
    group = part.get("group")
    if group and group["slug"] in catalogue.by_group:
        return catalogue.by_group[group["slug"]]
    return by_number.get(part["part_number"])


def _attach_guides(parts):
    """Annotate API dicts with their guide URL, in place.

    Done here rather than in the template because Django templates cannot
    subscript a dict by a variable key without a custom filter, and one view
    line is cheaper to maintain than a templatetags module.
    """
    catalogue = get_catalogue()
    by_number = {n: p for p in catalogue.parts for n in p.part_numbers}
    for part in parts:
        guide = _guide_for(part, catalogue, by_number)
        part["guide_url"] = guide.url if guide else None
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

    catalogue = get_catalogue()
    by_number = {n: p for p in catalogue.parts for n in p.part_numbers}
    guide = _guide_for(part, catalogue, by_number)

    context["part"] = part
    context["page_title"] = part.get("short_name") or part_number
    context["guide_url"] = guide.url if guide else None
    return render(request, "stock/inventory_detail.html", context)
