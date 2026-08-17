# ioref-web

The public ioref.org site: maker cards, categories, part sets, and a native
inventory browser. Wagtail 7 on Django.

Replaces **maker-cards** (`guides.ioref.org`, Express + Handlebars + Directus).
Visually it is the same site — `static/css/main.css` is carried over verbatim
and the templates are ports of the original Handlebars ones.

Stock lives in **ioref-inventory**, a separate repository with its own database.
This site reads it over HTTP with a read-scoped API key and joins on
`part_number`.

## Quick start

```bash
uv sync
cp .env.example .env          # set INVENTORY_API_KEY
uv run python manage.py migrate
uv run python manage.py seed_site
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Wagtail admin at `/admin/`.

For the inventory integration to do anything, ioref-inventory must be running
and `INVENTORY_API_KEY` must hold a **read**-scoped key generated in its admin.
Without one the site still works — stock blocks are simply omitted.

## Page tree

```
HomePage
├── CategoryPage             input · output · power · connector · controller
│   ├── SubcategoryPage
│   │   └── ComponentPage
│   │         └── StockedPart (inline, not a page)
│   └── ComponentPage        components hung straight off a category
└── PartSetIndexPage
    └── PartSetPage
```

**A component is not a part.** `ComponentPage` answers "what is a ceramic
capacitor"; its `StockedPart` rows are the 10pF, 22pF and 47pF the lab actually
holds, each with its own bin, count and price in ioref-inventory.

This is the fix for a real problem in the old data: `data.csv` repeats the same
capacitor explanation across 33 rows, the same incandescent-bulb explanation
across 12, and soldering-tip instructions across 4. Editing one meant editing
all of them. Most components have exactly one stocked part, and the migration
defaults to that.

Category slugs are load-bearing: `main.css` colours boxes by
`category-<slug>`, and the same five categories key the drawio shape library.

## The split with ioref-inventory

| Here | ioref-inventory |
|---|---|
| Component names, descriptions, images, signal type | Counts, backstock |
| Seven `docs_*` sections | Prices, suppliers, purchase links |
| Categories, subcategories, part sets | Locations, min/max, status |
| Related components | Stock and price history |
| Which part numbers a component covers | The parts themselves |

They join on `part_number`, which is not a foreign key — separate databases by
design, so integrity is a convention enforced at import.

Three fixes over the Directus schema:

- **Part sets are many-to-many.** Directus had a single FK on `parts`, so a part
  could belong to one set only — wrong, since a resistor appears in many kits.
- **Guide content is separated from stock.** The old `parts` collection was one
  42-column table doing both jobs, which is why inventory could not be deployed
  independently.
- **Components are separated from stocked parts**, so one explanation can cover
  many part numbers.

## Inventory integration

`stock/client.py` is the only channel. Everything fails soft, but two different
ways, deliberately:

- `get_stock()` / `get_stock_many()` return `None` / `{}` when inventory is
  unreachable. A component page is mostly documentation and reads fine without
  stock counts.
- `list_parts()` raises `InventoryUnavailable`. The browse view must be able to
  distinguish "nothing matched your filter" from "inventory is down" — rendering
  an outage as an empty catalogue would be worse than an error.

`get_stock_many()` fetches every part under a component in a single request via
the API's `part_number__in` filter — the capacitor page covers 33 of them.

Results are cached for `INVENTORY_CACHE_SECONDS` (default 120). 404s are cached
too, so a part with a guide but no stock record is not re-requested on every
pageview; 500s are not, since they are transient.

## Native inventory browser

`/inventory/` — the listing maker-cards did not have. It linked out to a
separate application with `target="_blank"`; this renders the same data in the
site's own chrome, with search, status filtering, and links across to the maker
card where one exists. Read-only: the API key is read-scoped.

## Styling

`static/css/main.css` is an unmodified copy from
`maker-cards/public/css/main.scss`. Do not edit it — put changes in
`static/css/site.css`, which holds only the inventory-view styles. To resync:

```bash
npx sass static/css/main.scss static/css/main.css
```

The header search is a plain GET to Wagtail's search view. The original ran a
live autocomplete against Directus via jQuery, bootstrap-autocomplete and a
Handlebars template; that machinery went with Directus.

## Importing from Directus

```bash
# once, from ioref-inventory -- writes the JSONL bundle both apps read
./tools/directus_to_json.sh physcomp.sql ../directus-export

uv run python manage.py import_directus ../directus-export
uv run python manage.py import_directus ../directus-export --uploads /path/to/uploads
```

Idempotent; pages are matched on slug within their parent. Of 1,511 source rows
about 130 carry guide content and become components -- the rest are stock only
and belong to ioref-inventory.

The `docs_*` fields are copied verbatim, because they are markdown already.

Images need the Directus uploads directory, which the SQL dump does not contain.
Run without `--uploads` first and re-run later to backfill.

## Tests

```bash
uv run python manage.py test
```
