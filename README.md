# ioref-web

The public ioref.org site: maker cards, categories, part sets, and a native
inventory browser. Django, with no CMS and no database.

The guides are markdown files in `content/`. Editing the site means editing a
file and committing it.

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
uv run python manage.py runserver
```

No migrate, no superuser, no seed step: there is no database and no login, and
the content is checked in, so a fresh clone runs.

For the inventory integration to do anything, ioref-inventory must be running
and `INVENTORY_API_KEY` must hold a **read**-scoped key generated in its admin.
Without one the site still works — stock blocks are simply omitted.

## Editing a card

Every card is one file, `content/parts/<slug>.md`:

```markdown
---
title: Infrared Receiver
description: Interprets infrared remote control signals.
category: input
subcategory: light
image: 0251.jpg
parts:
- number: '0251'
---

## What it is

The infrared receiver interprets infrared light commands.
```

The `##` headings are a fixed set of seven, in a fixed display order: About,
What it is, When to use it, How it works, How to use it, Getting started,
Resources. A heading outside that set is an error at startup rather than a
section that silently disappears from the page. Omit any you do not need.

Images referenced as `/images/parts/<file>` are files under
`public/images/parts/`, which is served at the root of the URL space rather
than under `/static/`. Restart the server after editing; content is read once
at startup.

`content/categories.yml` holds the five categories and their subcategories,
`content/part-sets.yml` the part sets.

## Structure

```
content/parts/*.md          one file per component
content/categories.yml      input · output · power · connector · controller
content/part-sets.yml
public/images/parts/        media the prose references by path
public/videos/parts/
```

**A component is not a part.** One file answers "what is a ceramic capacitor";
its `parts:` list is the 10pF, 22pF and 47pF the lab actually holds, each with
its own bin, count and price in ioref-inventory.

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

The header search is a plain GET, matched as a substring across titles and
prose with title hits ranked first. 130 parts fit in memory, so there is no
index. The original ran a live autocomplete against Directus via jQuery,
bootstrap-autocomplete and a Handlebars template; that machinery went with
Directus.

## Where the content came from

Directus → Wagtail → files. The middle step is gone: `content/` is the source
of truth now and is edited directly.

Of 1,511 source rows in Directus about 130 carried guide content and became
the files in `content/parts/`; the rest are stock only and belong to
ioref-inventory. The seven `docs_*` fields were markdown in Directus and are
markdown here, byte for byte.

The Wagtail-era importer and the exporter that produced `content/` are in git
history rather than the tree, since neither can run without the models they
were written against.

## Tests

```bash
uv run python manage.py test
```
