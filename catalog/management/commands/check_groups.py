"""Verify that every group named in front matter still exists in inventory.

Run this after inventory renames or re-derives its groups. Nothing else will
tell you: the API answers an unknown group with HTTP 200 and an empty result
set, which is indistinguishable from a group whose parts have all been
retired, so a stale slug renders an empty stock table and logs nothing at
build time.

This is deliberately a command and not a test. It needs a running inventory,
and a test suite that fails when a service is down is a test suite people
learn to ignore.
"""

from django.core.management.base import BaseCommand, CommandError

from catalog.content import get_catalogue


class Command(BaseCommand):
    help = "Check every group in content/ against a running inventory."

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit non-zero if any group is missing. For CI or a deploy gate.",
        )

    def handle(self, *args, **options):
        from stock.client import InventoryUnavailable, list_by_group, list_parts

        # Fail loudly rather than reporting every group as broken because the
        # service is down. That mistake would be worse than the one this
        # command exists to catch.
        try:
            list_parts(limit=1)
        except InventoryUnavailable as exc:
            raise CommandError(f"Inventory is unreachable, so nothing can be checked: {exc}")

        pages = [p for p in get_catalogue().parts if p.group]
        if not pages:
            self.stdout.write("No page declares a group.")
            return

        missing = []
        for page in sorted(pages, key=lambda p: p.slug):
            parts = list_by_group(page.group)
            if parts:
                self.stdout.write(
                    f"  ok       {page.slug:28} {page.group:24} {len(parts)} parts"
                )
            else:
                missing.append(page)
                self.stdout.write(
                    self.style.ERROR(
                        f"  EMPTY    {page.slug:28} {page.group:24} 0 parts"
                    )
                )

        self.stdout.write("")
        if not missing:
            self.stdout.write(self.style.SUCCESS(f"{len(pages)} groups, all resolve."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"{len(missing)} of {len(pages)} groups matched nothing. Either the slug "
                "was renamed in inventory, or the group is genuinely empty. "
                "Check against /api/v1/groups/ before editing front matter."
            )
        )
        if options["strict"]:
            raise CommandError("Stale groups found.")
