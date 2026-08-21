"""Public URLs.

Flat, and none of it is ambiguous: a guide is always /parts/<group-slug>/
regardless of category, and a category listing is always /c/<slug>/. The
previous scheme nested guides under /<category>/[<subcategory>/]<slug>/ and
needed a resolver to tell a subcategory from a part at the same depth; that
whole class of problem went away when category stopped being a fact a guide
file carries.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("part-sets/", views.part_set_index, name="part_set_index"),
    path("part-sets/<slug:slug>/", views.part_set, name="part_set"),
    path("parts/<slug:slug>/", views.part, name="part"),
    path("c/<slug:category_slug>/", views.category, name="category"),
]
