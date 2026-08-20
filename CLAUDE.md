# ioref-web

Django with no CMS and no database. The public ioref.org site, replacing
maker-cards. Initial implementation August 2026.

The guides are 49 markdown files in `content/`, read once at startup. Editing
the site means editing a file and committing it. Stock arrives over
ioref-inventory's API. There is nothing else.

`README.md` covers usage. This document covers rationale, constraints, and
outstanding work.

## System context

ioref.org currently runs as three applications and is being rebuilt as two.

| Current | Replacement | Status |
|---|---|---|
| **Directus** (`admin.ioref.org`, MySQL `phys_comp_prod`) — CMS and identity provider | retired | in production |
| **maker-cards** (`guides.ioref.org`, Express + Handlebars) | **ioref-web** — this repository | scaffolded |
| **IDeATe-Inventory** (Express, port 3000) | **ioref-inventory** — separate repository | scaffolded |

The applications being replaced are the authoritative reference. Check them out
alongside this repository:

- **maker-cards** — what this replaces. `public/css/main.scss` is the source of
  truth for visual design; `views/` are the templates these were ported from.
- **ioref-inventory** — the stock application. Read its `CLAUDE.md` too; the API
  contract is defined there.
- **cms** — the Directus installation.
- `ioref-schema.yaml` — Directus schema snapshot; the migration reference.
- **physcomp-drawio-library** — Python; generates drawio shape libraries. Shares
  the five-category taxonomy and is a candidate for the LTI work.

## Design decisions

**Guide content and stock are separate applications.** The Directus `parts`
collection was a 42-column table combining maker-card documentation with stock
keeping. Splitting it is what allows ioref-inventory to be deployed by another
organisation with its own parts and no interest in CMU's write-ups. Do not add
stock fields to models here, and do not add guide content to inventory.

**There is no database.** `DATABASES = {}`, and no `django.contrib.auth`,
`sessions`, `messages` or `admin`. Guide content is files, stock lives in
ioref-inventory, and there are no accounts because there is nothing to log in
to. Wagtail was here first and was carrying a page tree, a revision history, an
image library and a user system for a site whose entire content is 100 KB of
markdown edited by one person who would rather use git.

The empty `DATABASES` is the load-bearing part: it means anything that wants a
model has to argue for reintroducing a database, rather than adding one field
and quietly bringing back migrations.

**Components are separate from the parts stocked under them.** One file answers
"what is a ceramic capacitor"; its `parts:` list is the 10pF, 22pF and 47pF the
lab actually holds, each with its own bin and count in inventory. The Directus
schema had no such distinction, so `data.csv` repeats the same capacitor
explanation across 33 rows, the same bulb explanation across 12, and editing one
meant editing all of them.

The import defaulted to 1:1, one file per part number, which produced 31
resistor pages that differed only by value. Those are merged: `resistor`,
`potentiometer` and `electrolytic-capacitor` each cover a whole family now.
Further merging is done as staff next edit a card.

**`part_number` is the join key.** It lives in the `parts:` list in frontmatter.
The two applications have separate stores, so it is not a foreign key;
referential integrity is a convention, and `catalog/tests.py` at least checks
the numbers are unique across the catalogue.

**Part sets are many-to-many.** Directus modelled this as a single FK on
`parts`, restricting a part to one set. A resistor belongs in many kits.

**The seven documentation sections are markdown.** maker-cards ran every one of
them through `marked()` (`routes/parts.js:91`), and the content is written
accordingly: 22 parts carry fenced code blocks with language hints (`cpp` x14),
and 59 diagrams are inline `<figure>` HTML.

They are `##` headings in the file, and the heading text is what maps a section
back onto its anchor. The set is fixed, not free-form: the side-menu jump links
are built from it by name, so an unrecognised heading raises at load rather than
vanishing from the page. See `catalog/content.py:DOC_SECTIONS`.

The nh3 allowances in `catalog/content.py` are what let `<figure>`,
`<figcaption>` and `<pre>` through. Narrowing them silently deletes the
diagrams, and only on the pages that use them.

`nh3.clean` is called with `link_rel=None`. It rewrites `rel` on every link by
default and refuses to also accept `rel` as an allowed attribute, so the two
settings are mutually exclusive; the prose sets its own on outbound links.

**`/images/parts/<file>` is a real path, served from `public/`.** The guide
markdown references its diagrams that way because maker-cards resolved them
against Directus at request time (`routes/file-redirect.js`). Exporting the
media under the names the prose already uses means a file server answers
directly, and the alias table that used to translate them is gone along with
the view that read it. Not rewriting the markdown was the point of storing it.

`public/` is served at the root of the URL space by `WHITENOISE_ROOT`, and is
deliberately **not** in `STATICFILES_DIRS`. Under `STATIC_URL` these would be
`/static/images/parts/<file>`, which is not what the prose asks for, and
`collectstatic` would copy 58 MB into `staticfiles/` as a second set whose
names the manifest storage then hashes. Files existing on disk is not the same
as files answering on a URL; `catalog/tests.py` checks the paths and the smoke
test in the Commands section checks the URLs.

**`main.css` is carried over verbatim.** The site must look unchanged. It is a
straight copy of maker-cards' compiled stylesheet; additions go in `site.css`
so the copy can be resynced without merging.

**There is no sign-in, because there is nothing to sign in to.** An earlier
revision put the Wagtail admin behind CMU Shibboleth, with a custom user model,
a trusted-header backend and a vhost that cleared the identity headers. All of
it went when the CMS did; recover it from git history if a web editor ever comes
back. ioref-inventory still uses that arrangement for staff count entry, and is
unaffected.

**Media is committed to the repository.** 110 files, 58 MB in `public/`,
unoptimised straight out of Directus. Only files the prose actually references
are kept; the export copied Wagtail's whole alias table, 75 files of which
nothing pointed at. Deliberate, on the grounds that the
alternative is running something to serve them. Note that git keeps every
future revision forever, so replacing an image is not free.

## Implementation constraints

**Never give the content objects a generated `__repr__` or `__eq__`.** `Part`
points at its `Category`, whose `parts` list points back. Both generated methods
walk fields recursively, so either one follows that cycle until the process
dies. This is not hypothetical: an unrelated exception under `DEBUG=True` made
Django render a traceback page, which reprs the view's local variables, which
exhausted memory and got the process OOM-killed with no traceback to say why.
Hence `@dataclass(eq=False)` and `repr=False` on every back-reference in
`catalog/content.py`, and a test that asserts `repr()` terminates.

**`inventory_group` means "this page documents the whole group".** It does not
mean "this part happens to be in that group", which is what the Directus import
wrote and what made three switch pages each render a byte-identical table of
every switch in the lab. A page with its own `parts:` entry must not carry a
group; only `resistor` and `potentiometer` do, and neither has an inline part
of its own. Getting this wrong is invisible in tests and obvious on the page.

**An unknown group is silent.** Inventory answers a group it has never heard
of with HTTP 200 and an empty result set, which is byte-identical to a group
whose parts were all retired. When inventory re-derived its groups from part
names, `resistors` became `resistor`, and the resistor page rendered an empty
stock table for two days without logging anything. `list_by_group` now warns on
an empty result, and `manage.py check_groups` is the deliberate version to run
after any rename; `--strict` exits non-zero for a deploy gate. It is a command
rather than a test because it needs a running inventory, and a suite that fails
when a service is down is a suite people learn to ignore.

**URL ordering in `catalog/urls.py` is load-bearing.** Category slugs sit at the
root of the path, because that is where the legacy site had them and where the
links inside the guide prose point. `/search/` and `/part-sets/` are therefore
one reordering away from being interpreted as categories. Tested.

**`/<category>/<something>/` is ambiguous and resolved in the view.** It is
either a subcategory or a part hung straight off its category. Wagtail told
them apart by walking the page tree; `views.category_child` checks the
subcategory names first and falls back to a part.

**A part is served at exactly one URL.** `_render_part` 404s if the path does
not match the part's own category and subcategory, so the same page cannot be
reached under all five categories. The page tree enforced this for free.

**Category slugs are load-bearing.** `main.css` colours boxes with
`category-<slug>`, so the five slugs must remain `input`, `output`, `power`,
`connector`, `controller`. The home page rows are driven from slugs in
`views.home` rather than file order, so that reordering `categories.yml` cannot
break the layout.

**The client functions fail differently on purpose.** `get_stock()` and
`get_stock_many()` return `None` / `{}`; `list_parts()` raises
`InventoryUnavailable`. A component page without stock is still a useful page —
it is mostly documentation — but a browse view that renders an outage as an
empty catalogue is actively misleading. Preserve the distinction.

**Component pages fetch stock in one request, not one per part.** The ceramic
capacitor page covers 33 part numbers; `get_stock_many()` uses the API's
`part_number__in` filter so rendering it costs a single call. Reverting to a
loop over `get_stock()` would be 33 round trips per pageview.

**404s are cached, 500s are not.** A part with a guide but no stock record is a
permanent condition and should not be re-requested every pageview; a 500 is
transient and caching it would extend the outage.

**Images are served full size.** Wagtail generated a 200x200 rendition for
every tile; there is no rendition machinery now, so `.img_part_tile` scales the
original in CSS and the browser downloads all 403 KB of it. The tiles look
right and the bytes are wrong. A build-time resize step is the fix if it ever
matters.

**Never write a multi-line `{# … #}` comment.** Django's `{# #}` syntax is
single-line only. Spanning one across lines does not produce a comment — the
text is emitted into the page as literal content. It raises no error and no
warning, so it is caught only by looking at the rendered output. Use
`{% comment %} … {% endcomment %}` for anything longer than one line. Every
comment in this repository longer than a line uses the tag form for this
reason.

## Design language

`maker-cards/public/css/main.scss` is authoritative.

- Typeface Nunito Sans. Info pages: 24px bold titles, 22px bold section
  headings, bold labels.
- Neutral greys, no blue cast: `#f2f2f2`, `#c4c4c4`, `#4f4f4f`, off-black
  `#1d1d1d`, off-white `#fdfdfd`.
- Category colours: input `#14B04D`, output `#00A0C4`, controller `#4C265B`,
  connector `#636466`, power `#DD1B50`.
- The `stock_low` crimson matches the badge in the inventory admin, so both
  interfaces agree on what "low" looks like.

## Commits

Conventional Commits, e.g. `feat(api): add part_number__in filter`.

Types in use: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`,
`build`, `ci`. Scope is the app or area (`catalog`, `stock`, `content`,
`deploy`). Breaking changes take a `!` before the colon and a
`BREAKING CHANGE:` footer.

List items in commit bodies use `*`, not `-`. No `Co-Authored-By` trailer.

The subject is imperative and lower-case, under about 72 characters. Where a
change encodes a decision, put the reasoning in the body -- this project has
several constraints that look arbitrary without it.

## Commands

```bash
uv sync
uv run python manage.py runserver
uv run python manage.py test
uv run python manage.py check_groups     # after inventory renames a group
```

No `migrate`, no `createsuperuser`, no seed command. There is no database and
no login, and the content is checked in, so a fresh clone runs.

Run both applications for the cross-application join: inventory on 8765, this
on 8766, with `INVENTORY_API_URL` pointing at the former. The part numbers in
`content/` are the real ones, which ioref-inventory's `seed_demo` covers a
subset of, so most parts will show stock as unavailable against a demo
inventory. That is the honest rendering of a part inventory has not heard of.

Content is read once at startup. `runserver` reloads on `.py` changes but not
on edits under `content/`, so restart it after editing a card, or call
`catalog.content.reload()`.

Media is the thing the test suite can only half check, because a file existing
on disk and a file answering on a URL are different claims. Against a running
server:

```bash
python - <<'EOF'
import re, pathlib, urllib.parse, urllib.request
pat = re.compile(r'/(images|videos)/parts/([^"\'<>)\]]+)')
for f in sorted(pathlib.Path("content/parts").glob("*.md")):
    for kind, name in pat.findall(f.read_text()):
        url = urllib.parse.quote(f"/{kind}/parts/{name.strip()}")
        try:
            code = urllib.request.urlopen(f"http://127.0.0.1:8000{url}").status
        except Exception as e:
            print(getattr(e, "code", e), url, f.name)
EOF
```

## Outstanding work

**The category sidebar no longer lists loose parts.** The Wagtail template
rendered `category.get_children`, which returns subcategories *and* the parts
hung directly off a category, so the rail on `/connector/` listed all 24 of its
parts as though they were subcategories. `side_category_menu.html` now iterates
`category.subcategories`. This is the only visible difference between the CMS
site and this one, and whether it was a bug or a feature is a judgement call
that has not been made. Restoring the old behaviour is a one-line change.

**Search has no autocomplete.** `Catalogue.search` is a substring scan over the
catalogue, ranking title matches first. It returns a superset of what Wagtail's
database backend did. The legacy site had live autocomplete against Directus; if
that is wanted, it is a JSON index and a little JavaScript, not a search
backend.

**Image bytes.** See the note under implementation constraints. A build step
that writes resized copies alongside the originals would fix both the tile
bandwidth and some of the repository weight.

**LTI.** Under consideration for the drawio library or part sets, launched from
Canvas. It lands here, not on inventory. LTI 1.3 is OIDC-based and launches in
an iframe, so it needs `SameSite=None` cookies — maker-cards already established
that pattern for its Directus session cookie.

**`.env` currently holds a development API key** generated against the local
inventory instance. Production needs its own read-scoped key.
