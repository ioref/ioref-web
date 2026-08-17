from django.urls import path

from . import views

urlpatterns = [
    path("", views.inventory_index, name="inventory_index"),
    path("<str:part_number>/", views.inventory_detail, name="inventory_detail"),
]
