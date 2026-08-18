"""Guide pages, rendered from the markdown files in content/.

These replace Wagtail's page serving. The URLs are unchanged from what the
page tree produced, because they are the public URLs of a live site and the
templates are the same ones, so a reader should not be able to tell.

There is no /images/parts/ view any more. Those files sit at that path under
static/, so whitenoise answers them directly and the MediaAlias table that
used to translate them is gone.
"""

from django.http import Http404
from django.shortcuts import render

from .content import get_catalogue


def _sidebar(catalogue, active_category):
    """The category rail shared by category, subcategory and part pages."""
    return {
        "all_categories": catalogue.categories,
        "active_category": active_category,
    }


def home(request):
    catalogue = get_catalogue()
    by_slug = catalogue.categories_by_slug

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
    catalogue = get_catalogue()
    page = catalogue.categories_by_slug.get(category_slug)
    if page is None:
        raise Http404(f"No category {category_slug}")

    return render(
        request,
        "catalog/category_page.html",
        {
            "page": page,
            "subcategories": page.subcategories,
            "loose_parts": page.loose_parts,
            **_sidebar(catalogue, page),
        },
    )


def category_child(request, category_slug, slug):
    """Two path segments below the root, which is ambiguous.

    /input/light/ is a subcategory and /connector/2096-female-female-jumper-wire/
    is a part hung straight off its category. Wagtail told them apart by walking
    the page tree; without one, the subcategory names are what decide, so they
    are checked first and a part is the fallback.
    """
    catalogue = get_catalogue()
    sub = catalogue.subcategories_by_key.get((category_slug, slug))
    if sub is not None:
        return _render_subcategory(request, catalogue, sub)
    return _render_part(request, catalogue, slug, category_slug, None)


def part_in_subcategory(request, category_slug, subcategory_slug, slug):
    return _render_part(
        request, get_catalogue(), slug, category_slug, subcategory_slug
    )


def _render_subcategory(request, catalogue, page):
    return render(
        request,
        "catalog/subcategory_page.html",
        {
            "page": page,
            "parts": page.visible_parts,
            **_sidebar(catalogue, page.category),
        },
    )


def _render_part(request, catalogue, slug, category_slug, subcategory_slug):
    page = catalogue.by_slug.get(slug)
    if page is None:
        raise Http404(f"No part {slug}")

    # The part is reached at exactly one path. Serving it under any category
    # would mean the same page answering to several URLs, which the page tree
    # did not allow and search engines should not be offered.
    expected = (
        page.category.slug,
        page.subcategory.slug if page.subcategory else None,
    )
    if (category_slug, subcategory_slug) != expected:
        raise Http404(f"{slug} does not live at this path")

    return render(
        request,
        "catalog/component_page.html",
        {
            "page": page,
            "variants": _variants(page),
            "related_parts": page.related_parts,
            **_sidebar(catalogue, page.category),
        },
    )


def _variants(page):
    """What the lab stocks under this component heading.

    Two sources, and they are additive: a page can read a whole inventory group
    and still name a stray part that inventory files elsewhere.
    """
    from stock.client import get_stock_many, list_by_group

    variants = []
    if page.inventory_group:
        for entry in list_by_group(page.inventory_group):
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
        # One request for the lot, not one each: the ceramic capacitor page
        # covers 33 part numbers.
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
