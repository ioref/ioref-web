"""The guide content, read from markdown files rather than a database.

The whole catalogue is 130 files and about 100 KB of prose, so it is parsed
once and held in memory. There is no database behind any of this: editing the
site means editing a file and committing it.

Rendering happens at load time, not per request. Markdown for 130 pages costs
a few hundred milliseconds once at startup, and paying it per pageview for
content that only changes on deploy would be waste.

The sanitiser allowances are the ones that were in WAGTAILMARKDOWN before, and
they are not decorative: 59 diagrams in the prose are inline <figure> HTML and
22 parts carry fenced code blocks with language hints. Narrowing the allowed
tags silently deletes them, and only on the pages that use them.
"""

import threading
from dataclasses import dataclass, field
from pathlib import Path

import markdown as markdown_lib
import nh3
import yaml
from django.conf import settings
from django.utils.safestring import mark_safe

# Matches the old WAGTAILMARKDOWN configuration exactly.
ALLOWED_TAGS = set(nh3.ALLOWED_TAGS) | {
    "figure", "figcaption", "img", "video", "source", "pre", "code",
}
ALLOWED_ATTRIBUTES = {
    **nh3.ALLOWED_ATTRIBUTES,
    "figure": {"class", "style"},
    "figcaption": {"class", "style"},
    "img": {"src", "alt", "title", "width", "height", "class", "style"},
    "video": {"src", "controls", "width", "height", "class"},
    "source": {"src", "type"},
    "code": {"class"},
    "pre": {"class"},
    "a": {"href", "title", "rel", "target"},
}

MARKDOWN_EXTENSIONS = ["fenced_code", "codehilite", "tables", "nl2br"]
MARKDOWN_CONFIGS = {"codehilite": {"use_pygments": False}}

# The seven documentation sections, in the order they render. The labels are
# also the headings in the markdown files, so this is what maps a file back
# onto a section, and what the side-menu jump links are built from.
DOC_SECTIONS = (
    ("docs_about", "About"),
    ("docs_what_it_is", "What it is"),
    ("docs_when_to_use_it", "When to use it"),
    ("docs_how_it_works", "How it works"),
    ("docs_how_to_use_it", "How to use it"),
    ("docs_getting_started", "Getting started"),
    ("docs_resources", "Resources"),
)
LABEL_TO_ANCHOR = {label: anchor for anchor, label in DOC_SECTIONS}
SECTION_ORDER = {label: i for i, (_, label) in enumerate(DOC_SECTIONS)}


def render_markdown(text):
    html = markdown_lib.markdown(
        text,
        extensions=MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWN_CONFIGS,
    )
    return mark_safe(
        nh3.clean(
            html,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            # nh3 rewrites rel on every link by default and refuses to also
            # take rel as an allowed attribute. The prose sets its own on
            # outbound links, so hand it over rather than have nh3 impose one.
            link_rel=None,
        )
    )


@dataclass
class Section:
    anchor: str
    label: str
    body: str

    @property
    def body_html(self):
        return self._html

    def render(self):
        self._html = render_markdown(self.body)


# eq=False throughout, and repr=False on every back-reference.
#
# These objects form cycles: a Part points at its Category, whose `parts` list
# points back. The generated __repr__ and __eq__ both walk fields recursively,
# so either one follows the cycle until the process dies. That is not
# theoretical -- an unrelated exception under DEBUG=True made Django render a
# traceback page, which reprs local variables, which exhausted memory and got
# the process OOM-killed with no traceback to explain it.
#
# Identity comparison is also what is wanted: there is exactly one object per
# slug in a loaded catalogue, and eq=False restores hashability with it.
@dataclass(eq=False)
class PartSet:
    slug: str
    title: str
    description: str = ""
    image: str = ""
    parts: list = field(default_factory=list, repr=False)

    @property
    def url(self):
        return f"/part-sets/{self.slug}/"

    @property
    def image_url(self):
        return f"/images/parts/{self.image}" if self.image else ""

    # Templates were written against Wagtail pages and compare identity by id.
    @property
    def id(self):
        return self.slug


@dataclass(eq=False)
class Subcategory:
    slug: str
    title: str
    category: "Category" = field(default=None, repr=False)
    parts: list = field(default_factory=list, repr=False)

    @property
    def url(self):
        return f"/{self.category.slug}/{self.slug}/"

    @property
    def id(self):
        return self.slug

    @property
    def visible_parts(self):
        return [p for p in self.parts if not p.hidden]


@dataclass(eq=False)
class Category:
    slug: str
    title: str
    subcategories: list = field(default_factory=list, repr=False)
    parts: list = field(default_factory=list, repr=False)

    @property
    def url(self):
        return f"/{self.slug}/"

    @property
    def id(self):
        return self.slug

    @property
    def loose_parts(self):
        """Parts hung straight off the category, with no subcategory.

        The legacy site rendered these in an unlabelled block above the rest.
        """
        return [p for p in self.parts if p.subcategory is None and not p.hidden]


@dataclass(eq=False)
class Part:
    slug: str
    title: str
    description: str = ""
    signal_type: str = ""
    image: str = ""
    inventory_group: str = ""
    hidden: bool = False
    category: Category = field(default=None, repr=False)
    subcategory: Subcategory = field(default=None, repr=False)
    part_sets: list = field(default_factory=list, repr=False)
    related_slugs: list = field(default_factory=list, repr=False)
    stocked: list = field(default_factory=list, repr=False)
    sections: list = field(default_factory=list, repr=False)

    @property
    def url(self):
        if self.subcategory is not None:
            return f"/{self.category.slug}/{self.subcategory.slug}/{self.slug}/"
        return f"/{self.category.slug}/{self.slug}/"

    @property
    def id(self):
        return self.slug

    @property
    def part_numbers(self):
        return [p["number"] for p in self.stocked]

    @property
    def image_url(self):
        return f"/images/parts/{self.image}" if self.image else ""

    @property
    def related_parts(self):
        return self._related


class Catalogue:
    """Everything, indexed the handful of ways the views ask for it."""

    def __init__(self, parts, categories, part_sets):
        self.parts = parts
        self.categories = categories
        self.part_sets = part_sets
        self.by_slug = {p.slug: p for p in parts}
        self.categories_by_slug = {c.slug: c for c in categories}
        self.part_sets_by_slug = {s.slug: s for s in part_sets}
        self.subcategories_by_key = {
            (c.slug, s.slug): s for c in categories for s in c.subcategories
        }

    def search(self, query):
        """Substring match over title and prose.

        130 pages fits in memory many times over, so this is a loop rather than
        an index. Wagtail's database backend was not doing anything cleverer.
        """
        needle = (query or "").strip().lower()
        if not needle:
            return []
        hits = []
        for part in self.parts:
            if part.hidden:
                continue
            haystack = " ".join(
                [part.title, part.description] + [s.body for s in part.sections]
            ).lower()
            if needle in haystack:
                # Title matches first: searching "potentiometer" should not bury
                # the potentiometer under every page that mentions one.
                hits.append((0 if needle in part.title.lower() else 1, part.title, part))
        return [p for _, _, p in sorted(hits, key=lambda h: (h[0], h[1]))]


_lock = threading.Lock()
_catalogue = None


def content_dir():
    return Path(getattr(settings, "CONTENT_DIR", Path(settings.BASE_DIR) / "content"))


def get_catalogue():
    global _catalogue
    if _catalogue is None:
        with _lock:
            if _catalogue is None:
                _catalogue = load()
    return _catalogue


def reload():
    """Drop the cache. For tests, and for a development autoreloader."""
    global _catalogue
    with _lock:
        _catalogue = None
    return get_catalogue()


def _split_frontmatter(text, path):
    if not text.startswith("---"):
        raise ValueError(f"{path}: no frontmatter")
    _, _, rest = text.partition("---\n")
    front, sep, body = rest.partition("\n---")
    if not sep:
        raise ValueError(f"{path}: frontmatter is not closed")
    return yaml.safe_load(front) or {}, body.lstrip("\n")


def _parse_sections(body, path):
    sections = []
    current_label = None
    buffer = []

    def flush():
        if current_label is None:
            return
        text = "\n".join(buffer).strip()
        if not text:
            return
        if current_label not in LABEL_TO_ANCHOR:
            raise ValueError(
                f"{path}: unknown section heading '{current_label}'. "
                f"Expected one of: {', '.join(LABEL_TO_ANCHOR)}"
            )
        sections.append(
            Section(LABEL_TO_ANCHOR[current_label], current_label, text)
        )

    for line in body.splitlines():
        # Only level two, and only at the start of a line. Deeper headings
        # inside a section are the author's own and must not split the file.
        if line.startswith("## "):
            flush()
            current_label = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    flush()

    sections.sort(key=lambda s: SECTION_ORDER[s.label])
    return sections


def load():
    root = content_dir()

    taxonomy = yaml.safe_load((root / "categories.yml").read_text(encoding="utf-8"))
    categories = []
    for entry in taxonomy["categories"]:
        category = Category(slug=entry["slug"], title=entry["title"])
        for sub in entry.get("subcategories", []):
            category.subcategories.append(
                Subcategory(slug=sub["slug"], title=sub["title"], category=category)
            )
        categories.append(category)
    by_cat = {c.slug: c for c in categories}

    set_data = yaml.safe_load((root / "part-sets.yml").read_text(encoding="utf-8"))
    part_sets = [
        PartSet(
            slug=s["slug"],
            title=s["title"],
            description=s.get("description", ""),
            image=s.get("image", ""),
        )
        for s in set_data.get("part_sets", [])
    ]
    by_set = {s.slug: s for s in part_sets}

    parts = []
    for path in sorted((root / "parts").glob("*.md")):
        front, body = _split_frontmatter(path.read_text(encoding="utf-8"), path)

        category = by_cat.get(front.get("category", ""))
        if category is None:
            raise ValueError(
                f"{path}: category '{front.get('category')}' is not in categories.yml"
            )

        subcategory = None
        if front.get("subcategory"):
            key = (category.slug, front["subcategory"])
            subcategory = {
                (c.slug, s.slug): s for c in categories for s in c.subcategories
            }.get(key)
            if subcategory is None:
                raise ValueError(
                    f"{path}: subcategory '{front['subcategory']}' is not under "
                    f"category '{category.slug}' in categories.yml"
                )

        part = Part(
            slug=path.stem,
            title=front["title"],
            description=front.get("description", ""),
            signal_type=front.get("signal_type", ""),
            image=front.get("image", ""),
            inventory_group=front.get("inventory_group", ""),
            hidden=bool(front.get("hidden", False)),
            category=category,
            subcategory=subcategory,
            related_slugs=list(front.get("related", [])),
            stocked=[dict(p) for p in front.get("parts", [])],
            sections=_parse_sections(body, path),
        )

        for slug in front.get("part_sets", []):
            part_set = by_set.get(slug)
            if part_set is None:
                raise ValueError(f"{path}: part set '{slug}' is not in part-sets.yml")
            part.part_sets.append(part_set)
            part_set.parts.append(part)

        category.parts.append(part)
        if subcategory is not None:
            subcategory.parts.append(part)
        parts.append(part)

    by_slug = {p.slug: p for p in parts}

    # Second pass: relations point at other parts, so they need every part read
    # before they can be resolved. A dangling slug is an editing mistake worth
    # dropping quietly rather than 500ing the page it appears on.
    for part in parts:
        part._related = [
            by_slug[s] for s in part.related_slugs if s in by_slug and not by_slug[s].hidden
        ]
        for section in part.sections:
            section.render()

    for category in categories:
        category.parts.sort(key=lambda p: p.title)
        for sub in category.subcategories:
            sub.parts.sort(key=lambda p: p.title)
    for part_set in part_sets:
        part_set.parts.sort(key=lambda p: p.title)
    parts.sort(key=lambda p: p.title)

    return Catalogue(parts, categories, part_sets)
