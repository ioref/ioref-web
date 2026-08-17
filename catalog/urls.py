from django.urls import path

from . import views

# Both prefixes resolve the same alias table; maker-cards mounted its
# file-redirect route at /images and /videos alike.
urlpatterns = [
    path("images/parts/<str:filename>", views.legacy_media, name="legacy_image"),
    path("videos/parts/<str:filename>", views.legacy_media, name="legacy_video"),
]
