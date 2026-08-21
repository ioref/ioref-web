"""Verify the five hardcoded categories match what inventory actually has.

content/categories.yml is deliberately not fetched from inventory (the home
page must render when inventory is down), but that means nothing catches it
drifting from what /api/v1/categories/ actually returns -- a category
inventory renamed or removed would leave this file naming something that
matches no group, silently.
"""

from django.core.management.base import BaseCommand, CommandError

from catalog.content import load_categories


class Command(BaseCommand):
    help = "Check the five hardcoded categories against a running inventory."

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit non-zero on any mismatch. For CI or a deploy gate.",
        )

    def handle(self, *args, **options):
        from stock.client import InventoryUnavailable, list_categories

        try:
            live = list_categories()
        except InventoryUnavailable as exc:
            raise CommandError(f"Inventory is unreachable, so nothing can be checked: {exc}")

        live_slugs = {c["slug"] for c in live}
        local_slugs = {c.slug for c in load_categories()}

        missing = local_slugs - live_slugs
        extra = live_slugs - local_slugs

        for slug in sorted(local_slugs & live_slugs):
            self.stdout.write(f"  ok       {slug}")
        for slug in sorted(missing):
            self.stdout.write(self.style.ERROR(f"  MISSING  {slug} (in categories.yml, not in inventory)"))
        for slug in sorted(extra):
            self.stdout.write(f"  unused   {slug} (in inventory, no home-page tile)")

        self.stdout.write("")
        if not missing:
            self.stdout.write(self.style.SUCCESS("All hardcoded categories exist in inventory."))
            if extra:
                self.stdout.write(
                    f"{len(extra)} more exist in inventory with no tile here -- "
                    "that is fine, but worth a look if it grows."
                )
            return

        self.stdout.write(
            self.style.WARNING(
                f"{len(missing)} of {len(local_slugs)} hardcoded categories do not exist in "
                "inventory. Groups filed under them will never show up in /c/<slug>/."
            )
        )
        if options["strict"]:
            raise CommandError("categories.yml is out of sync with inventory.")
