# ioref-web

Wagtail 7 on Django. The public ioref.org site, replacing maker-cards.
Initial implementation August 2026.

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

**Components are separate from the parts stocked under them.** `ComponentPage`
answers "what is a ceramic capacitor"; its `StockedPart` children are the 10pF,
22pF and 47pF the lab actually holds, each with its own bin and count. The old
schema had no such distinction, so `data.csv` repeats the same capacitor
explanation across 33 rows, the same bulb explanation across 12, and editing one
meant editing all of them.

The migration defaults to **1:1** — one component, one stocked part — and merges
only where duplication is obvious. Nobody has to reclassify 1,628 parts up
front, and staff can merge others as they next edit a card.

**`part_number` is the join key, and lives on `StockedPart`, not the page.** The
two applications have separate databases, so it is not a foreign key;
referential integrity is a convention enforced at import.

**Part sets are many-to-many.** Directus modelled this as a single FK on
`parts`, restricting a part to one set. A resistor belongs in many kits.

**The seven `docs_*` fields are markdown, not rich text.** maker-cards ran every
one of them through `marked()` (`routes/parts.js:91`), and the content is
written accordingly: 22 parts carry fenced code blocks with language hints
(`cpp` x14), and 59 diagrams are inline `<figure>` HTML. Wagtail's rich text
editor has no fenced code block and sanitises against a whitelist, so it would
strip both -- and only on an editor's first save, weeks after the migration.
`wagtail-markdown` keeps the content byte-identical to the source.

The nh3 allowances in `WAGTAILMARKDOWN` are what let `<figure>`, `<figcaption>`
and `<pre>` through. Narrowing them silently deletes the diagrams.

**They are fixed named fields, not a StreamField.** Directus modelled them that
way, the side-menu jump links are built from them by name, and authors fill in
the same set every time. See `ComponentPage.DOC_SECTIONS`.

**`/images/parts/<file>` is served by `catalog/views.py`, not rewritten.** The
guide markdown references its diagrams by that path because maker-cards resolved
them against Directus at request time (`routes/file-redirect.js`). Keeping the
markdown untouched is the point of storing markdown, so `MediaAlias` maps the
filenames onto imported Wagtail images instead. Matching on `Image.title` would
have been simpler and would break the moment an editor renamed one.

**`main.css` is carried over verbatim.** The site must look unchanged. It is a
straight copy of maker-cards' compiled stylesheet; additions go in `site.css`
so the copy can be resynced without merging.

**Editors sign in with CMU Shibboleth; the guides stay public.** `AUTH_MODE`
takes `local`, `shib` or `oidc`, mirroring ioref-inventory rather than inventing
a second pattern (same env names, same header names, same user model shape),
because both applications sit behind one service provider and a change to CMU's
attribute release has to be answerable in both places at once. Nothing imports a
SAML or OIDC library at module scope, so Shibboleth to Entra is a configuration
and proxy change.

The two applications do *not* share a session or a user table. They share a
convention about what identifies a person: `username` is the eppn
(`user@andrew.cmu.edu`), and `subject_id` holds the IdP's permanent identifier
where one is released, taking precedence when resolving an account so that a
rename follows the person and a reissued eppn does not inherit the previous
holder's page history.

**A custom user model was defined before the first deployment.** Django cannot
swap `AUTH_USER_MODEL` once production data exists without a manual migration.
`accounts.User` adds only `subject_id` and `idp`.

**Shibboleth asserts identity, never authorisation.** Accounts are provisioned
on first sight with no groups, which in Wagtail means no
`wagtailadmin.access_admin` and so no editor at all. Adding someone to Editors
or Moderators stays a manual act in Wagtail's own user interface, which is the
point of provisioning: an administrator can only grant rights to an account that
exists, and this is what makes it exist without anyone typing an eppn by hand.
`_sync_attributes` refreshes name and email on every login and touches group
membership never, so signing in cannot revoke what was granted.

## Implementation constraints

**`AUTH_MODE=shib` trusts its request headers unconditionally.**
`accounts/backends.py` accepts whatever `REMOTE_USER_HEADER` contains. That is
safe only because the vhost overwrites those headers on every inbound request;
see the `RequestHeader unset` block in `deploy/apache/web.conf`. The block must
name every header the application reads. Adding a `REMOTE_USER_*_HEADER`
setting without adding it there is a complete authentication bypass. If gunicorn
is reachable other than through that vhost, the block buys nothing.

**The site root must stay `requireSession 0`.** The guides are public and are
most of the traffic. `requireSession 1` at `<Location />` puts the entire public
site behind a CMU login, which also breaks it for anyone outside the university.

**Wagtail's login view is replaced, and the replacement must not redirect an
authenticated user.** `require_admin_access` sends a signed-in user who lacks
`access_admin` to the login URL (`reject_request`, `wagtail/admin/auth.py`).
Under SSO their SAML session is valid, so handing them back to the IdP returns
them here immediately and loops until the browser gives up. `accounts/views.py`
renders a 403 explaining that a group is missing. Covered in `accounts/tests.py`.

**Logging out must end the SAML session, not just the Django one.**
`HeaderAuthenticationMiddleware` rebuilds the session from headers on every
request, so `auth.logout()` alone is invisible: the user is signed back in on
their next click. `wagtailadmin_logout` is overridden to redirect to
`/Shibboleth.sso/Logout`.

**Wagtail's password screens are switched off outside `local` mode.**
Provisioned accounts have unusable passwords, so a change-password form would
write to a field nothing checks and a reset email would arrive for an account
that cannot use it. `WAGTAIL_PASSWORD_MANAGEMENT_ENABLED`,
`WAGTAIL_PASSWORD_RESET_ENABLED` and `WAGTAILUSERS_PASSWORD_ENABLED`.

**The SSO URL overrides are registered from `AUTH_MODE` at import time.**
`override_settings(AUTH_MODE=...)` cannot reach them, which is why
`accounts/tests.py` calls those two views directly rather than over a URL.

**Category slugs are load-bearing.** `main.css` colours boxes with
`category-<slug>`, so the five slugs must remain `input`, `output`, `power`,
`connector`, `controller`. The home page rows are driven from slugs in
`HomePage.get_context` rather than tree order, so that an editor reordering
pages in the admin cannot break the layout.

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

**Templates that use `{% pageurl %}` must load `wagtailcore_tags`.** Easy to
miss in an include that mainly deals with images.

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
`build`, `ci`. Scope is the app or area (`api`, `inventory`, `accounts`,
`catalog`, `stock`, `deploy`). Breaking changes take a `!` before the colon and
a `BREAKING CHANGE:` footer.

The subject is imperative and lower-case, under about 72 characters. Where a
change encodes a decision, put the reasoning in the body -- this project has
several constraints that look arbitrary without it.

## Commands

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_site
uv run python manage.py createsuperuser
uv run python manage.py runserver
uv run python manage.py test
```

`seed_site` is idempotent and uses the same part numbers as ioref-inventory's
`seed_demo`, so with both running the cross-application join is live. Run both:
inventory on 8765, this on 8766, with `INVENTORY_API_URL` pointing at the former.

## Outstanding work

**Directus content migration.** Not written. Needs the collection export plus
`directus_files` metadata and the uploads directory for images.
`directus-dump.sh` in ioref-inventory exports an instance over HTTP. Categories,
subcategories, part sets and the seven `docs_*` fields all land here; stock
fields go to inventory. Two shape changes to apply on the way in:
`parts.part_set` is a single FK in the source and must widen to many-to-many,
and each source row becomes a `ComponentPage` with one `StockedPart` unless it
is one of the known duplicate-prose groups.

**Multi-line code in guide content.** Live cards carry Arduino listings — see
part 0260's "Getting started" section. Wagtail rich text has no block-level code
element by default, so a naive import will flatten them. Configure a code
feature, or move those sections to a StreamField, before importing.

**Search.** Currently Wagtail's default database backend. The legacy site had
live autocomplete against Directus. If that is wanted back, the right answer is
Wagtail's own autocomplete over a proper backend, not a reimplementation of the
jQuery machinery.

**Shibboleth under Docker.** `mod_shib` is an Apache module needing `shibd`
alongside it, and cannot run in the Python image. It wants a second service with
a persistent volume, because the service provider keypair must survive container
rebuilds or the metadata registered with the identity provider goes stale. The
same problem stands open in ioref-inventory; solve it once for both. Until then
`deploy/apache/web.conf` describes a host-Apache deployment.

**Registering this host with the identity provider.** ioref-inventory's service
provider is registered; `guides.ioref.org` is a second entityID and needs its
own registration and its own attribute release (eppn, mail, displayName, and a
persistent identifier if CMU will release one). Nothing in `AUTH_MODE=shib`
works until that is done.

**Bootstrapping the first editor.** Provisioned accounts have no groups, so on a
fresh deployment nobody can reach `/admin` and there is no password login to
fall back on. Sign in once to provision the account, then
`manage.py shell` to set `is_superuser`, or run `createsuperuser` with the eppn
as the username before first sign-in.

**LTI.** Under consideration for the drawio library or part sets, launched from
Canvas. It lands here, not on inventory. LTI 1.3 is OIDC-based and launches in
an iframe, so it needs `SameSite=None` cookies — maker-cards already established
that pattern for its Directus session cookie.

**`.env` currently holds a development API key** generated against the local
inventory instance. Production needs its own read-scoped key.
