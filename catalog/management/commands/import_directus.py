"""Import guide content from a Directus export.

Consumes the JSONL bundle written by ioref-inventory's tools/directus_to_json.sh.

Takes the maker-card half of the old `parts` collection: names, the seven
docs_* fields, images, categories, subcategories, part sets and related parts.
Stock is ignored here -- it belongs to ioref-inventory and arrives over the API.

The docs_* fields are copied verbatim. They are markdown (maker-cards rendered
them with marked(), routes/parts.js:91) and stay markdown, so nothing is
transformed and nothing can be lost in translation.

Of 1,511 source rows only ~130 carry any guide content, and those have 130
distinct names -- the cards were already curated one per component. Each becomes
a ComponentPage whose stocked parts come from its inventory group, so the
potentiometer card lists all 23 pots rather than only the one it was written on.

Idempotent: pages are matched on slug within their parent.
"""

import json
from collections import Counter
from pathlib import Path

from django.core.files import File
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify
from wagtail.documents.models import Document
from wagtail.images.models import Image

from catalog.models import (
    CategoryPage,
    ComponentPage,
    MediaAlias,
    PartRelation,
    PartSetIndexPage,
    PartSetPage,
    StockedPart,
    SubcategoryPage,
)
from home.models import HomePage

DOC_FIELDS = [
    "docs_about",
    "docs_what_it_is",
    "docs_when_to_use_it",
    "docs_how_it_works",
    "docs_how_to_use_it",
    "docs_getting_started",
    "docs_resources",
]

# Mirrors ioref-inventory's derivation, so a component page's inventory_group
# matches the group the same location string produced there. Kept as a copy
# rather than shared code: the two applications are separate repositories on
# separate release cycles, and a shared helper would be a hidden coupling.
USE_AS_TAG = {"touch", "lending", "tool box"}
GROUP_ALIASES = {"potentiometer": "Potentiometers", "capacitor": "Capacitors"}


def group_slug_for(location_name):
    if not location_name or ":" not in location_name:
        return ""
    _, _, fine = location_name.partition(":")
    fine = fine.strip()
    if not fine or fine.lower() in USE_AS_TAG:
        return ""
    return slugify(GROUP_ALIASES.get(fine.lower(), fine))


def load(export, name):
    path = export / f"{name}.jsonl"
    if not path.exists():
        raise CommandError(f"No {name}.jsonl in {export}")
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def child_page(parent, model, slug, title, **fields):
    """Idempotent get-or-create of a page beneath `parent`."""
    existing = model.objects.child_of(parent).filter(slug=slug).first()
    if existing:
        existing.title = title
        for key, value in fields.items():
            setattr(existing, key, value)
        existing.save()
        return existing, False
    page = model(slug=slug, title=title, **fields)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page, True


class Command(BaseCommand):
    help = "Import guide content from a Directus JSONL export."

    def add_arguments(self, parser):
        parser.add_argument("export_dir", type=Path)
        parser.add_argument(
            "--uploads",
            type=Path,
            help=(
                "Directus uploads directory. Images are skipped without it, and "
                "the command can be re-run later to backfill them."
            ),
        )

    @transaction.atomic
    def handle(self, *args, **options):
        export = options["export_dir"]
        self.uploads = options["uploads"]
        self.stats = Counter()

        home = HomePage.objects.first()
        if home is None:
            raise CommandError("No HomePage; run migrate first.")

        files = {f["id"]: f for f in load(export, "files")}
        self.images = self._import_images(files)

        categories = self._import_categories(home, load(export, "categories"))
        subcategories = self._import_subcategories(
            categories, load(export, "subcategories")
        )
        sets = self._import_part_sets(home, load(export, "part_sets"))

        parts = load(export, "parts")
        components = self._import_components(parts, categories, subcategories, sets)
        self._import_relations(load(export, "parts_parts"), parts, components)

        self._report()

    # -- images ------------------------------------------------------------

    def _import_images(self, files):
        """Load the Directus files that are actually referenced.

        Also records a MediaAlias per file, so the /images/parts/<filename>
        paths embedded in the guide markdown keep resolving without rewriting
        the content.
        """
        images = {}
        if not self.uploads:
            self.stats["images_skipped_no_uploads"] = len(files)
            return images

        for file_id, meta in files.items():
            disk = meta.get("filename_disk")
            if not disk:
                continue
            path = self.uploads / disk
            if not path.exists():
                self.stats["images_missing_on_disk"] += 1
                continue

            title = (meta.get("title") or meta.get("filename_download") or disk)[:255]
            mime = (meta.get("type") or "").lower()
            download = meta.get("filename_download")

            # Idempotency keys on filename_disk, which is UUID-named and unique.
            # Titles are not: 9 collide, including three distinct "Medium Bread"
            # photographs, and deduping on them silently merged 12 files into
            # one another on the first run.
            if mime.startswith("image/"):
                media = Image.objects.filter(file__endswith=f"/{disk}").first()
                if media is None:
                    with path.open("rb") as handle:
                        media = Image.objects.create(
                            title=title, file=ImageFile(handle, name=disk)
                        )
                    self.stats["images_created"] += 1
                images[file_id] = media
                alias_field = "image"
            else:
                # Two of 185 are video. Wagtail images cannot hold them, and
                # they are only ever referenced from prose, never as a part
                # photo, so they do not belong in the `images` map.
                media = Document.objects.filter(file__endswith=f"/{disk}").first()
                if media is None:
                    with path.open("rb") as handle:
                        media = Document.objects.create(
                            title=title, file=File(handle, name=disk)
                        )
                    self.stats["documents_created"] += 1
                alias_field = "document"

            # 5 filename_download values are shared by two files each. The
            # legacy resolver required exactly one match and 404s on those, so
            # nothing is lost by last-write-wins here -- but none of the five
            # are referenced in the prose anyway.
            if download:
                MediaAlias.objects.update_or_create(
                    filename=download,
                    defaults={alias_field: media, "image" if alias_field == "document" else "document": None},
                )
                self.stats["media_aliases"] += 1
        return images

    # -- taxonomy ----------------------------------------------------------

    def _import_categories(self, home, rows):
        out = {}
        for row in rows:
            page, created = child_page(
                home, CategoryPage, row["slug"] or slugify(row["name"]), row["name"]
            )
            out[row["id"]] = page
            self.stats["categories_created"] += int(created)
        return out

    def _import_subcategories(self, categories, rows):
        out = {}
        for row in rows:
            parent = categories.get(row["category"])
            if parent is None:
                self.stats["subcategories_orphaned"] += 1
                continue
            # Slugs are only unique within a category -- "Movement" exists under
            # both Input and Output, and "Light" under both -- so they are
            # created beneath their own parent rather than globally.
            page, created = child_page(
                parent, SubcategoryPage, row["slug"] or slugify(row["name"]), row["name"]
            )
            out[row["id"]] = page
            self.stats["subcategories_created"] += int(created)
        return out

    def _import_part_sets(self, home, rows):
        index, _ = child_page(home, PartSetIndexPage, "part-sets", "Part Sets")
        out = {}
        for row in rows:
            page, created = child_page(
                index,
                PartSetPage,
                row["slug"] or slugify(row["name"]),
                row["name"],
                description=row.get("description") or "",
                image=self.images.get(row.get("image")),
            )
            out[row["id"]] = page
            self.stats["part_sets_created"] += int(created)
        return out

    # -- components --------------------------------------------------------

    def _import_components(self, parts, categories, subcategories, sets):
        components = {}
        for row in parts:
            docs = {f: (row.get(f) or "").strip() for f in DOC_FIELDS}
            has_docs = any(docs.values())
            if not (row.get("category") or row.get("image") or has_docs):
                self.stats["parts_stock_only"] += 1
                continue

            parent = subcategories.get(row.get("subcategory")) or categories.get(
                row.get("category")
            )
            if parent is None:
                # Guide content with nowhere to hang it. Reported rather than
                # invented a home for.
                self.stats["components_uncategorised"] += 1
                continue

            number = (row.get("part_number") or "").strip()
            name = (row.get("name") or number).strip()
            slug = slugify(f"{number}-{name}")[:80] or slugify(number)

            page, created = child_page(
                parent, ComponentPage, slug, name,
                signal_type=(row.get("signal_type") or "")[:100],
                description=row.get("description") or "",
                image=self.images.get(row.get("image")),
                hidden=bool(row.get("hidden")),
                # Set so the page lists every part inventory files under the
                # same group -- all 23 potentiometers, not just this one.
                inventory_group=group_slug_for(row.get("location")),
                **docs,
            )
            self.stats["components_created" if created else "components_updated"] += 1
            self.stats["components_with_docs"] += int(has_docs)

            # Its own part number, in case it has no inventory group. Additive,
            # and deduped against the group at render time.
            StockedPart.objects.update_or_create(
                part_number=number, defaults={"page": page, "sort_order": 0}
            )

            if row.get("part_set") and row["part_set"] in sets:
                page.part_sets.set([sets[row["part_set"]]])
                page.save()

            components[row["id"]] = page
        return components

    def _import_relations(self, rows, parts, components):
        by_id = {r["id"]: r for r in parts}
        PartRelation.objects.all().delete()
        for row in rows:
            source = components.get(row["parts_id"])
            target = components.get(row["related_parts_id"])
            if source is None or target is None:
                # One side has no guide page -- a related part that is stock only.
                self.stats["relations_skipped"] += 1
                continue
            PartRelation.objects.create(page=source, related_part=target)
            self.stats["relations_created"] += 1

    def _report(self):
        self.stdout.write("")
        for key, value in sorted(self.stats.items()):
            self.stdout.write(f"  {key.replace('_', ' '):<30} {value:>6}")
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{ComponentPage.objects.count()} components, "
                f"{CategoryPage.objects.count()} categories, "
                f"{SubcategoryPage.objects.count()} subcategories, "
                f"{PartSetPage.objects.count()} part sets, "
                f"{Image.objects.count()} images."
            )
        )
