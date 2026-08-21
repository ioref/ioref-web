"""Guide pages, rendered from the markdown files in content/.

Guides live at /parts/<group-slug>/ regardless of category, because parsing
one never talks to inventory (see content.py). Category only exists as a
live, request-time concept, fetched by the /category/<slug>/ browse view
below -- the site's shape does not depend on inventory being reachable at
startup, only that one page does.
"""

from django.http import Http404
from django.shortcuts import redirect, render

from stock.client import InventoryUnavailable, get_part, list_groups_by_category

from .content import get_catalogue, load_categories


def home(request):
    categories = load_categories()
    by_slug = {c.slug: c for c in categories}

    # maker-cards laid these out two-then-three, and the widths in main.css
    # assume that split. Driven from slugs rather than file order so that
    # reordering categories.yml cannot break the layout.
    def row(*slugs):
        return [by_slug[slug] for slug in slugs if slug in by_slug]

    return render(
        request,
        "catalog/home_page.html",
        {
            "categories_top": row("input", "output"),
            "categories_bottom": row("power", "connector", "controller"),
        },
    )


def category(request, category_slug):
    """Every group inventory files under this category, live.

    Not built from content/: a group with no guide still belongs here, so a
    purchasing question ("what's under Power") is answerable without anyone
    having written a word about half of it. Guided groups link to their guide;
    the rest link to /inventory/?group=<slug>, which already knows how to list
    a group's stock.
    """
    categories = load_categories()
    page = next((c for c in categories if c.slug == category_slug), None)
    if page is None:
        raise Http404(f"No category {category_slug}")

    context = {
        "page": page,
        "all_categories": categories,
        "active_category_slug": category_slug,
    }

    catalogue = get_catalogue()
    try:
        groups = list_groups_by_category(category_slug)
    except InventoryUnavailable:
        context["unavailable"] = True
        return render(request, "catalog/category_page.html", context, status=503)

    context["unavailable"] = False
    context["groups"] = [
        {
            "slug": g["slug"],
            "name": g["name"],
            "part_count": g.get("part_count", 0),
            "guide": catalogue.by_group.get(g["slug"]),
            "url": (catalogue.by_group[g["slug"]].url
                    if g["slug"] in catalogue.by_group
                    else f"/inventory/?group={g['slug']}"),
        }
        for g in sorted(groups, key=lambda g: g["name"])
    ]
    return render(request, "catalog/category_page.html", context)


def category_alias(request, category_slug):
    """/c/<slug>/ -> /category/<slug>/. A short alias, not a second page --
    it never renders anything itself, so category_page.html has exactly one
    caller. Permanent redirect: the alias is a deliberate, stable shorthand,
    not a typo to leave open for search engines to index twice."""
    return redirect("category", category_slug=category_slug, permanent=True)


def resolve_legacy(request, token):
    """The printed cards' bare URLs: ioref.org/resistor, ioref.org/0496.

    They predate this site and cannot be reprinted, so whatever they name has
    to resolve from here, at the root, with no prefix to hint which case it
    is. Tried in order:

    1. `token` is a guide's own slug (a group name, "resistor") -- resolved
       locally, no inventory involved.
    2. `token` is a part number inventory knows about, and that part's group
       has a guide -- redirect to the guide, since it documents the whole
       group this part belongs to.
    3. `token` is a part number with no guide behind it (ungrouped, or a
       group nobody has written up) -- redirect to its inventory page, the
       same "just show the inventory" fallback /inventory/ itself uses for
       stock with no guide.
    4. None of the above: 404. Inventory being unreachable is folded into
       this case rather than a 503 of its own -- the inventory detail page
       one line down already renders the right outage message for a part
       number, and a token that is not a part number was never going to
       resolve regardless of whether inventory answers.
    """
    catalogue = get_catalogue()

    guide = catalogue.by_slug.get(token)
    if guide is not None:
        return redirect(guide.url)

    try:
        part = get_part(token)
    except InventoryUnavailable:
        part = None

    if part is None:
        raise Http404(f"No guide, group, or part named {token}")

    group = part.get("group")
    if group:
        guide = catalogue.by_group.get(group["slug"])
        if guide is not None:
            return redirect(guide.url)

    return redirect("inventory_detail", part_number=token)


def part(request, slug):
    catalogue = get_catalogue()
    page = catalogue.by_slug.get(slug)
    if page is None:
        raise Http404(f"No part {slug}")

    return render(
        request,
        "catalog/component_page.html",
        {
            "page": page,
            "variants": _variants(page),
            "related_parts": page.related_parts,
        },
    )


def _variants(page):
    """What the lab stocks under this component heading.

    Two sources, and they are additive: a page can read a whole inventory group
    and still name a stray part that inventory files elsewhere.
    """
    from stock.client import get_stock_many, list_by_group

    variants = []
    if page.group:
        for entry in list_by_group(page.group):
            # The distinguishing detail is in the description; short_name is
            # the same word for every part in the group ("potentiometer" x25).
            description = (entry.get("description") or "").strip()
            variants.append(
                {
                    "number": entry["part_number"],
                    "label": description or entry.get("short_name", ""),
                    "note": "",
                    "stock": entry,
                }
            )

    seen = {v["number"] for v in variants}
    inline = [p for p in page.stocked if p["number"] not in seen]
    if inline:
        # One request for the lot, not one each: a group can run to 30+ parts.
        stock = get_stock_many([p["number"] for p in inline])
        variants += [
            {
                "number": p["number"],
                "label": p.get("label", ""),
                "note": p.get("note", ""),
                "stock": stock.get(p["number"]),
            }
            for p in inline
        ]

    return variants


def part_set_index(request):
    catalogue = get_catalogue()
    return render(
        request,
        "catalog/part_set_index_page.html",
        {"page": {"title": "Part Sets"}, "part_sets": catalogue.part_sets},
    )


def part_set(request, slug):
    catalogue = get_catalogue()
    page = catalogue.part_sets_by_slug.get(slug)
    if page is None:
        raise Http404(f"No part set {slug}")

    return render(
        request,
        "catalog/part_set_page.html",
        {
            "page": page,
            "set_parts": [p for p in page.parts if not p.hidden],
        },
    )


def search(request):
    catalogue = get_catalogue()
    query = request.GET.get("query", "")
    return render(
        request,
        "catalog/search.html",
        {"search_query": query, "search_results": catalogue.search(query)},
    )
