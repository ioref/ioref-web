from wagtail.models import Page


class HomePage(Page):
    subpage_types = ["catalog.CategoryPage", "catalog.PartSetIndexPage"]

    def get_context(self, request):
        from catalog.models import CategoryPage

        context = super().get_context(request)
        categories = {
            page.slug: page
            for page in CategoryPage.objects.child_of(self).live()
        }

        # maker-cards laid these out two-then-three, and the widths in main.css
        # assume that split. Driven from slugs rather than tree order so an
        # editor reordering pages in the admin cannot break the layout.
        def row(*slugs):
            return [categories[slug] for slug in slugs if slug in categories]

        context["categories_top"] = row("input", "output")
        context["categories_bottom"] = row("power", "connector", "controller")
        return context
