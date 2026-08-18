"""The file-backed catalogue: parsing, rendering, and the URLs it serves.

SimpleTestCase throughout, because there is no database. The parsing tests
build a content directory in a temporary folder so they can assert on exact
inputs; the view tests run against the real content/, because the real files
are the thing most likely to contain a case nobody thought to write a fixture
for.
"""

import re
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from catalog import content

FENCED = """Wire it up, then:

```cpp
void setup() {
  Serial.begin(9600);
}
```
"""

FIGURE = (
    '<figure class="image" style="text-align:center">'
    '<img src="/images/parts/pot.gif" alt="A potentiometer">'
    "<figcaption><em>Image from Sparkfun</em></figcaption></figure>"
)


def write_content(root, parts, categories=None, part_sets=None):
    root = Path(root)
    (root / "parts").mkdir(parents=True, exist_ok=True)
    (root / "categories.yml").write_text(
        categories
        or "categories:\n- slug: input\n  title: Input\n  subcategories:\n"
        "  - slug: light\n    title: Light\n",
        encoding="utf-8",
    )
    (root / "part-sets.yml").write_text(
        part_sets or "part_sets:\n- slug: starter\n  title: Starter\n", encoding="utf-8"
    )
    for name, text in parts.items():
        (root / "parts" / f"{name}.md").write_text(text, encoding="utf-8")
    return root


class ParsingTests(SimpleTestCase):
    def load(self, parts, **kwargs):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = write_content(self.tmp.name, parts, **kwargs)
        with override_settings(CONTENT_DIR=root):
            return content.load()

    def test_sections_come_back_in_display_order_not_file_order(self):
        """The jump menu is built from this order, so it cannot follow the file.

        An author who appends a section to the end of a file should not thereby
        move it to the end of the page.
        """
        cat = self.load(
            {
                "p": "---\ntitle: P\ncategory: input\n---\n\n"
                "## Resources\n\nLinks.\n\n## About\n\nA thing.\n"
            }
        )
        self.assertEqual(
            [s.label for s in cat.by_slug["p"].sections], ["About", "Resources"]
        )

    def test_empty_sections_are_omitted(self):
        """Live card 0390 has no About section; the jump menu must skip it."""
        cat = self.load(
            {
                "p": "---\ntitle: P\ncategory: input\n---\n\n"
                "## About\n\n## What it is\n\nA variable resistor.\n"
            }
        )
        self.assertEqual([s.label for s in cat.by_slug["p"].sections], ["What it is"])

    def test_fenced_code_survives_rendering(self):
        """22 parts carry fenced blocks with language hints.

        This is why the content is markdown and why the sanitiser has to allow
        <pre> and <code>: rich text would have eaten them on first save.
        """
        cat = self.load(
            {
                "p": f"---\ntitle: P\ncategory: input\n---\n\n## Getting started\n\n{FENCED}"
            }
        )
        html = str(cat.by_slug["p"].sections[0].body_html)
        self.assertIn("<code", html)
        self.assertIn("Serial.begin(9600)", html)

    def test_figure_markup_survives_rendering(self):
        """59 diagrams are inline <figure> HTML. Narrowing the allowed tags
        deletes them silently, and only on the pages that use them."""
        cat = self.load(
            {
                "p": f"---\ntitle: P\ncategory: input\n---\n\n## How it works\n\n{FIGURE}\n"
            }
        )
        html = str(cat.by_slug["p"].sections[0].body_html)
        self.assertIn("<figure", html)
        self.assertIn("<figcaption", html)
        self.assertIn("/images/parts/pot.gif", html)

    def test_script_tags_are_stripped(self):
        cat = self.load(
            {
                "p": "---\ntitle: P\ncategory: input\n---\n\n"
                "## About\n\n<script>alert(1)</script>Safe.\n"
            }
        )
        self.assertNotIn("<script", str(cat.by_slug["p"].sections[0].body_html))

    def test_part_numbers_stay_strings(self):
        """0386 is an identifier, not the integer 386."""
        cat = self.load(
            {
                "p": "---\ntitle: P\ncategory: input\nparts:\n- number: '0386'\n---\n\n"
                "## About\n\nx\n"
            }
        )
        self.assertEqual(cat.by_slug["p"].part_numbers, ["0386"])

    def test_url_reflects_whether_a_subcategory_is_set(self):
        cat = self.load(
            {
                "loose": "---\ntitle: L\ncategory: input\n---\n\n## About\n\nx\n",
                "nested": "---\ntitle: N\ncategory: input\nsubcategory: light\n---\n\n## About\n\nx\n",
            }
        )
        self.assertEqual(cat.by_slug["loose"].url, "/input/loose/")
        self.assertEqual(cat.by_slug["nested"].url, "/input/light/nested/")

    def test_unknown_section_heading_is_an_error_not_a_silent_drop(self):
        """A typo in a heading would otherwise delete the section from the page
        with nothing to show for it."""
        with self.assertRaises(ValueError) as caught:
            self.load(
                {"p": "---\ntitle: P\ncategory: input\n---\n\n## Waht it is\n\nx\n"}
            )
        self.assertIn("Waht it is", str(caught.exception))

    def test_unknown_category_is_an_error(self):
        with self.assertRaises(ValueError):
            self.load(
                {"p": "---\ntitle: P\ncategory: nonsense\n---\n\n## About\n\nx\n"}
            )

    def test_subcategory_must_belong_to_the_category(self):
        with self.assertRaises(ValueError):
            self.load(
                {
                    "p": "---\ntitle: P\ncategory: input\nsubcategory: nope\n---\n\n## About\n\nx\n"
                }
            )

    def test_dangling_related_slug_is_dropped_not_fatal(self):
        """A rename elsewhere should not 500 an unrelated page."""
        cat = self.load(
            {
                "p": "---\ntitle: P\ncategory: input\nrelated:\n- gone\n---\n\n## About\n\nx\n"
            }
        )
        self.assertEqual(cat.by_slug["p"].related_parts, [])

    def test_deeper_headings_do_not_split_the_file(self):
        """### inside a section belongs to the author, not to the parser."""
        cat = self.load(
            {
                "p": "---\ntitle: P\ncategory: input\n---\n\n"
                "## About\n\nIntro.\n\n### A detail\n\nMore.\n"
            }
        )
        sections = cat.by_slug["p"].sections
        self.assertEqual(len(sections), 1)
        self.assertIn("A detail", sections[0].body)

    def test_repr_terminates(self):
        """Part and Category reference each other. A generated repr that walks
        both directions runs until the process is killed, which is how this was
        found: an unrelated error page tried to repr a view's locals."""
        cat = self.load({"p": "---\ntitle: P\ncategory: input\n---\n\n## About\n\nx\n"})
        self.assertIn("slug='p'", repr(cat.by_slug["p"]))
        self.assertIn("slug='input'", repr(cat.categories[0]))


class RealContentTests(SimpleTestCase):
    """Against the real content/, not a fixture."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.catalogue = content.reload()

    def test_every_part_loads(self):
        self.assertEqual(
            len(self.catalogue.parts),
            len(list((Path(settings.CONTENT_DIR) / "parts").glob("*.md"))),
        )

    def test_every_part_has_a_category(self):
        self.assertEqual(
            [p.slug for p in self.catalogue.parts if p.category is None], []
        )

    def test_every_section_heading_is_recognised(self):
        # Guaranteed by the loader raising, but assert it for the real files so
        # a bad edit fails here rather than at the first pageview.
        labels = {s.label for p in self.catalogue.parts for s in p.sections}
        self.assertTrue(labels <= set(content.LABEL_TO_ANCHOR))

    def test_no_slug_carries_a_part_number_prefix(self):
        """A component page documents a kind of thing, not one stocked item.

        The Directus slugs led with the part number, so /input/movement/
        0390-potentiometer/ was the URL of the general potentiometer
        explanation. Values belong to the parts in inventory, not to the
        document. The three families that only differed by value were merged;
        a new file must not reintroduce the pattern.
        """
        offenders = [
            p.slug for p in self.catalogue.parts if re.match(r"^\d{4}-", p.slug)
        ]
        self.assertEqual(offenders, [])

    def test_part_numbers_are_unique_across_the_catalogue(self):
        seen = [n for p in self.catalogue.parts for n in p.part_numbers]
        self.assertEqual(len(seen), len(set(seen)))

    def test_search_ranks_title_matches_first(self):
        results = self.catalogue.search("potentiometer")
        self.assertTrue(results)
        self.assertIn("potentiometer", results[0].title.lower())

    def test_every_media_path_in_the_prose_exists_on_disk(self):
        """The diagrams are referenced by path, not by a database row.

        Nothing resolves these at runtime any more, so a missing or mis-cased
        file is a broken image on a live page and nothing else notices. The
        filenames contain spaces and mixed case, hence the wide character class
        and the exact-case check.
        """
        pattern = re.compile(r'/(images|videos)/parts/([^"\'<>)\]]+)')
        root = Path(settings.WHITENOISE_ROOT)
        missing = []
        for path in sorted((Path(settings.CONTENT_DIR) / "parts").glob("*.md")):
            for kind, name in pattern.findall(path.read_text(encoding="utf-8")):
                target = root / kind / "parts" / name.strip()
                if not target.exists():
                    missing.append(f"{path.name}: /{kind}/parts/{name.strip()}")
        self.assertEqual(missing, [])

    def test_frontmatter_images_exist_on_disk(self):
        for part in self.catalogue.parts:
            if part.image:
                target = (
                    Path(settings.WHITENOISE_ROOT) / "images" / "parts" / part.image
                )
                self.assertTrue(target.exists(), f"{part.slug}: {part.image}")


class ViewTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.catalogue = content.reload()

    def test_home(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_every_part_url_resolves(self):
        bad = []
        for part in self.catalogue.parts:
            if self.client.get(part.url).status_code != 200:
                bad.append(part.url)
        self.assertEqual(bad, [])

    def test_every_category_and_subcategory_url_resolves(self):
        for category in self.catalogue.categories:
            self.assertEqual(
                self.client.get(category.url).status_code, 200, category.url
            )
            for sub in category.subcategories:
                self.assertEqual(self.client.get(sub.url).status_code, 200, sub.url)

    def test_part_is_404_under_the_wrong_category(self):
        """One page, one URL. Serving it under every category would hand search
        engines a pile of duplicates."""
        part = next(p for p in self.catalogue.parts if p.subcategory is None)
        wrong = next(c for c in self.catalogue.categories if c is not part.category)
        self.assertEqual(
            self.client.get(f"/{wrong.slug}/{part.slug}/").status_code, 404
        )

    def test_unknown_paths_404(self):
        for url in ["/nonsense/", "/input/nonsense/", "/input/light/nonsense/"]:
            self.assertEqual(self.client.get(url).status_code, 404, url)

    def test_part_sets(self):
        self.assertEqual(self.client.get("/part-sets/").status_code, 200)
        for part_set in self.catalogue.part_sets:
            self.assertEqual(self.client.get(part_set.url).status_code, 200)

    def test_search_page(self):
        response = self.client.get("/search/", {"query": "potentiometer"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "otentiometer")

    def test_named_routes_are_not_swallowed_by_the_category_pattern(self):
        """Category slugs sit at the root of the path, so /search/ and
        /part-sets/ are one ordering mistake away from becoming categories."""
        self.assertEqual(self.client.get("/search/").status_code, 200)
        self.assertEqual(self.client.get("/part-sets/").status_code, 200)
