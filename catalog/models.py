"""Guide content: the maker-card side of the old Directus `parts` collection.

Stock, prices, suppliers and locations are *not* here -- they belong to
ioref-inventory and arrive over its API, joined on `part_number`. See
stock/client.py.
"""

from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtailmarkdown.fields import MarkdownField
from wagtail.models import Orderable, Page
from wagtail.search import index

# The five categories are a fixed taxonomy shared with the drawio shape library
# and maker-cards' CSS, which colours by `category-<slug>`. Slugs must match.
CATEGORY_SLUGS = ("input", "output", "power", "connector", "controller")


class CategorySidebarMixin:
    """Supplies the category rail shared by category, subcategory and part pages.

    Kept in one place because all three render the same sidebar and it needs to
    know which category is currently active.
    """

    def sidebar_context(self, active_category):
        return {
            "all_categories": CategoryPage.objects.live().order_by("path").specific(),
            "active_category": active_category,
        }


class CategoryPage(CategorySidebarMixin, Page):
    """One of the five top-level categories. Lives directly under the home page."""

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["catalog.SubcategoryPage", "catalog.ComponentPage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["subcategories"] = (
            SubcategoryPage.objects.child_of(self).live().order_by("title")
        )
        # Parts hung directly off the category rather than a subcategory. The
        # legacy site rendered these in an unlabelled block above the rest.
        context["loose_parts"] = (
            ComponentPage.objects.child_of(self).live().filter(hidden=False).order_by("title")
        )
        context.update(self.sidebar_context(self))
        return context


class SubcategoryPage(CategorySidebarMixin, Page):
    parent_page_types = ["catalog.CategoryPage"]
    subpage_types = ["catalog.ComponentPage"]

    @property
    def visible_parts(self):
        return ComponentPage.objects.child_of(self).live().filter(hidden=False).order_by("title")

    def get_context(self, request):
        context = super().get_context(request)
        context["parts"] = self.visible_parts
        context.update(self.sidebar_context(self.get_parent().specific))
        return context


class PartRelation(Orderable):
    """Self-referential 'related parts', mirroring Directus's parts_parts table."""

    page = ParentalKey("catalog.ComponentPage", related_name="related_part_links")
    related_part = models.ForeignKey(
        "catalog.ComponentPage", on_delete=models.CASCADE, related_name="+"
    )

    panels = [FieldPanel("related_part")]


class StockedPart(Orderable):
    """One specific thing the lab stocks under a component heading.

    "Ceramic capacitor" is a component; 10pF, 22pF and 47pF are stocked parts,
    each with its own bin, count and price. The legacy schema had no such
    distinction, so the capacitor explanation was copy-pasted across 33 rows of
    data.csv and had to be edited 33 times.

    Most components have exactly one of these -- the migration defaults to 1:1
    and merges only where the duplication is obvious, so nobody has to
    reclassify 1,628 parts up front.

    `part_number` is the join key to ioref-inventory and must match the part
    number there exactly. Not a foreign key: the two applications have separate
    databases by design, so integrity is a convention enforced at import.
    """

    page = ParentalKey("catalog.ComponentPage", related_name="stocked_parts")
    part_number = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        help_text="Must match the part number in ioref-inventory.",
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text='What distinguishes this one, e.g. "10pF". Leave blank if the component has only one.',
    )
    note = models.CharField(max_length=200, blank=True)

    panels = [FieldPanel("part_number"), FieldPanel("label"), FieldPanel("note")]

    class Meta(Orderable.Meta):
        verbose_name = "stocked part"

    def __str__(self):
        return f"{self.part_number} {self.label}".strip()


class ComponentPage(CategorySidebarMixin, Page):
    """A maker card: what this component is, generally.

    Holds no stock data. What the lab actually has sits in ioref-inventory,
    reached through the StockedPart rows below.
    """

    description = RichTextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    signal_type = models.CharField(max_length=100, blank=True)

    # Markdown, not rich text. maker-cards ran every one of these through
    # marked() (routes/parts.js:91), and the content is written accordingly:
    # 22 parts carry fenced code blocks with language hints, and 59 diagrams
    # are inline <figure> HTML. Wagtail's rich text editor has no fenced code
    # block and sanitises against a whitelist, so it would strip both -- and
    # only on the first save by an editor, weeks after the migration.
    #
    # Fixed named fields rather than a StreamField: Directus modelled them this
    # way, the side-menu jump links are built from them by name, and authors
    # fill in the same set every time.
    docs_about = MarkdownField(blank=True, verbose_name="About")
    docs_what_it_is = MarkdownField(blank=True, verbose_name="What it is")
    docs_when_to_use_it = MarkdownField(blank=True, verbose_name="When to use it")
    docs_how_it_works = MarkdownField(blank=True, verbose_name="How it works")
    docs_how_to_use_it = MarkdownField(blank=True, verbose_name="How to use it")
    docs_getting_started = MarkdownField(blank=True, verbose_name="Getting started")
    docs_resources = MarkdownField(blank=True, verbose_name="Resources")


    part_sets = ParentalManyToManyField(
        "catalog.PartSetPage",
        blank=True,
        related_name="parts",
        help_text="A part may belong to several sets.",
    )

    inventory_group = models.SlugField(
        max_length=100,
        blank=True,
        help_text=(
            "Slug of an ioref-inventory group, e.g. 'potentiometers'. When set, "
            "the stocked parts below are read from inventory instead of being "
            "listed by hand."
        ),
    )

    hidden = models.BooleanField(
        default=False,
        help_text="Keep published but omit from category and set listings.",
    )

    parent_page_types = ["catalog.CategoryPage", "catalog.SubcategoryPage"]
    subpage_types = []

    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("docs_about"),
        index.SearchField("docs_what_it_is"),
        index.AutocompleteField("title"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("signal_type"),
                FieldPanel("image"),
                FieldPanel("description"),
            ],
            heading="Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("docs_about"),
                FieldPanel("docs_what_it_is"),
                FieldPanel("docs_when_to_use_it"),
                FieldPanel("docs_how_it_works"),
                FieldPanel("docs_how_to_use_it"),
                FieldPanel("docs_getting_started"),
                FieldPanel("docs_resources"),
            ],
            heading="Documentation",
            classname="collapsed",
        ),
        MultiFieldPanel(
            [FieldPanel("inventory_group")],
            heading="Stocked parts from inventory",
        ),
        InlinePanel(
            "stocked_parts",
            heading="Stocked parts listed by hand",
            help_text=(
                "Only needed when there is no inventory group, or to cover parts "
                "outside it."
            ),
        ),
        MultiFieldPanel(
            [FieldPanel("part_sets"), FieldPanel("hidden")],
            heading="Placement",
        ),
    ]

    # Ordered so the side-menu jump links render in the sequence authors expect.
    DOC_SECTIONS = (
        ("docs_about", "About"),
        ("docs_what_it_is", "What it is"),
        ("docs_when_to_use_it", "When to use it"),
        ("docs_how_it_works", "How it works"),
        ("docs_how_to_use_it", "How to use it"),
        ("docs_getting_started", "Getting started"),
        ("docs_resources", "Resources"),
    )

    @property
    def sections(self):
        """Populated documentation sections, in display order.

        Code blocks need no special handling now: they are fenced markdown
        inside the section body, which is how the content was already written.
        """
        return [
            {"anchor": field, "label": label, "body": getattr(self, field)}
            for field, label in self.DOC_SECTIONS
            if (getattr(self, field) or "").strip()
        ]

    @property
    def category(self):
        """The CategoryPage above this part, whether or not a subcategory sits between."""
        for ancestor in self.get_ancestors().specific():
            if isinstance(ancestor, CategoryPage):
                return ancestor
        return None

    @property
    def subcategory(self):
        parent = self.get_parent().specific
        return parent if isinstance(parent, SubcategoryPage) else None

    @property
    def part_numbers(self):
        return [p.part_number for p in self.stocked_parts.all()]

    def _variants_from_group(self):
        """Stocked parts read from inventory, by group.

        Membership is answered where the part lives. Nothing here has to be
        kept in step when a part is added, retired or reclassified.
        """
        from stock.client import list_by_group

        variants = []
        for part in list_by_group(self.inventory_group):
            # The distinguishing detail is in the description; short_name is the
            # same word for every part in the group ("potentiometer" x25).
            description = (part.get("description") or "").strip()
            label = description or part.get("short_name", "")
            variants.append(
                {"number": part["part_number"], "label": label, "stock": part}
            )
        return variants

    def _variants_from_inlines(self):
        from stock.client import get_stock_many

        # One request for the lot, not one each: the ceramic capacitor page
        # covers 33 part numbers.
        stock = get_stock_many(self.part_numbers)
        return [
            {
                "number": part.part_number,
                "label": part.label,
                "note": part.note,
                "stock": stock.get(part.part_number),
            }
            for part in self.stocked_parts.all()
        ]

    def get_context(self, request):
        context = super().get_context(request)

        # Hand-listed parts are additive, so a page can use a group and still
        # name a stray part that inventory files elsewhere.
        variants = self._variants_from_group() if self.inventory_group else []
        seen = {v["number"] for v in variants}
        variants += [v for v in self._variants_from_inlines() if v["number"] not in seen]

        context["variants"] = variants
        context["has_stock_data"] = any(v["stock"] for v in variants)
        context["related_parts"] = [
            link.related_part for link in self.related_part_links.all()
        ]
        context.update(self.sidebar_context(self.category))
        return context


class MediaAlias(models.Model):
    """Maps a legacy image filename to the imported Wagtail image.

    The guide markdown references diagrams by path -- <img
    src="/images/parts/potentiometer_interior.gif"> -- because maker-cards
    resolved those against Directus at request time (routes/file-redirect.js).
    Keeping the markdown untouched is the point of storing it as markdown, so
    rather than rewriting 59 image paths on import, this table lets the same
    URLs keep working.

    An explicit table rather than matching on Image.title, which editors can
    rename at any time and would silently break every reference.
    """

    filename = models.CharField(max_length=255, unique=True, db_index=True)
    # Two targets because the legacy library is not all images: 183 of 185
    # files are, but two are video (an assembly clip and an operation clip),
    # referenced from the prose as /videos/parts/<file>. Wagtail images cannot
    # hold those, so they become documents.
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="legacy_aliases",
    )
    document = models.ForeignKey(
        "wagtaildocs.Document",
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="legacy_aliases",
    )

    class Meta:
        verbose_name_plural = "media aliases"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(image__isnull=False, document__isnull=True)
                    | models.Q(image__isnull=True, document__isnull=False)
                ),
                name="alias_points_at_exactly_one_target",
            )
        ]

    def __str__(self):
        return self.filename

    @property
    def url(self):
        target = self.image or self.document
        return target.file.url if target else None


class PartSetIndexPage(Page):
    parent_page_types = ["home.HomePage"]
    subpage_types = ["catalog.PartSetPage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["part_sets"] = PartSetPage.objects.child_of(self).live().order_by("title")
        return context


class PartSetPage(Page):
    """A set of components for a project.

    Directus modelled this as a single foreign key on `parts`, so a part could
    belong to exactly one set -- wrong, since a resistor appears in many kits.
    The relationship is many-to-many here; see ComponentPage.part_sets.
    """

    description = RichTextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("image"),
    ]

    parent_page_types = ["catalog.PartSetIndexPage"]
    subpage_types = []

    def get_context(self, request):
        context = super().get_context(request)
        context["set_parts"] = self.parts.live().filter(hidden=False).order_by("title")
        return context
