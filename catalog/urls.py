"""Public URLs, matching what the Wagtail page tree used to produce.

Order matters. The catch-all category patterns at the bottom would happily
swallow /search/ and /part-sets/, so the named routes come first. That is the
cost of keeping category slugs at the root of the path, which is where the
legacy site had them and where the links in the guide prose point.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("part-sets/", views.part_set_index, name="part_set_index"),
    path("part-sets/<slug:slug>/", views.part_set, name="part_set"),
    path("<slug:category_slug>/", views.category, name="category"),
    # Either a subcategory or a part sitting directly under the category; the
    # view decides. See views.category_child.
    path(
        "<slug:category_slug>/<slug:slug>/", views.category_child, name="category_child"
    ),
    path(
        "<slug:category_slug>/<slug:subcategory_slug>/<slug:slug>/",
        views.part_in_subcategory,
        name="part",
    ),
]
