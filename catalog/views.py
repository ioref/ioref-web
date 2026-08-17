"""Legacy media paths.

Guide markdown references its diagrams and clips as /images/parts/<file> and
/videos/parts/<file>, because maker-cards resolved those against Directus at
request time (routes/file-redirect.js, mounted at both prefixes). Storing the
content as markdown means not rewriting it, so these serve the same paths from
the imported Wagtail media instead.
"""

from django.http import Http404
from django.shortcuts import redirect

from .models import MediaAlias


def legacy_media(request, filename):
    alias = (
        MediaAlias.objects.filter(filename=filename)
        .select_related("image", "document")
        .first()
    )
    if alias is None or alias.url is None:
        raise Http404(f"No media named {filename}")
    # Redirect rather than proxy, so whatever serves media -- whitenoise,
    # nginx, a CDN -- keeps doing it.
    return redirect(alias.url)
