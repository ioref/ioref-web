"""Component pages: the generic explanation, and the parts stocked under it."""

from unittest.mock import patch

from django.test import RequestFactory, TestCase

from catalog.models import CategoryPage, ComponentPage, StockedPart, SubcategoryPage
from home.models import HomePage

FENCED = """Wire it up, then:

```cpp
void setup() {
  Serial.begin(9600);
}
```
"""


class SectionTests(TestCase):
    def test_empty_sections_are_omitted(self):
        """Live card 0390 has no 'About' section; the jump menu must skip it."""
        page = ComponentPage(
            title="Potentiometer",
            slug="pot",
            docs_what_it_is="<p>A variable resistor.</p>",
            docs_how_it_works="<p>A wiper slides along a track.</p>",
        )
        self.assertEqual(
            [s["label"] for s in page.sections], ["What it is", "How it works"]
        )

    def test_fenced_code_is_kept_verbatim_in_the_section(self):
        """Code needs no special field: it is fenced markdown in the body.

        22 parts in the production data carry fenced blocks with language
        hints. Wagtail rich text would have stripped them on first save.
        """
        page = ComponentPage(title="P", slug="p", docs_getting_started=FENCED)
        self.assertEqual(page.sections[0]["body"], FENCED)
        self.assertIn("```cpp", page.sections[0]["body"])

    def test_whitespace_only_sections_are_omitted(self):
        page = ComponentPage(title="P", slug="p", docs_about="   \n  ")
        self.assertEqual(page.sections, [])


class StockedPartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        category = CategoryPage(title="Input", slug="input")
        home.add_child(instance=category)
        sub = SubcategoryPage(title="Movement", slug="movement")
        category.add_child(instance=sub)

        cls.component = ComponentPage(title="Potentiometer", slug="potentiometer")
        sub.add_child(instance=cls.component)

        for order, (number, label) in enumerate(
            [("0390", "10kΩ, panel mount"), ("0388", "1kΩ, panel mount")]
        ):
            StockedPart.objects.create(
                page=cls.component, part_number=number, label=label, sort_order=order
            )

    def test_one_component_covers_several_part_numbers(self):
        """The point of the split: 25 pots, one explanation."""
        self.assertEqual(self.component.part_numbers, ["0390", "0388"])

    def test_stocked_parts_keep_their_order(self):
        labels = [p.label for p in self.component.stocked_parts.all()]
        self.assertEqual(labels, ["10kΩ, panel mount", "1kΩ, panel mount"])

    def test_a_part_number_belongs_to_one_component(self):
        from django.db import IntegrityError

        other = ComponentPage(title="Other", slug="other")
        self.component.get_parent().add_child(instance=other)
        with self.assertRaises(IntegrityError):
            StockedPart.objects.create(page=other, part_number="0390")

    def test_page_renders_without_inventory(self):
        """Inventory being unreachable must not fail a documentation page."""
        response = self.client.get(self.component.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Potentiometer")


class GroupDerivedPartsTests(TestCase):
    """A component page can read its parts from an inventory group.

    This is what replaced hand-listing 25 potentiometer part numbers: the
    membership question is answered where the parts are maintained, so adding,
    retiring or reclassifying one needs no edit here.
    """

    @classmethod
    def setUpTestData(cls):
        home = HomePage.objects.get()
        category = CategoryPage(title="Input", slug="input")
        home.add_child(instance=category)
        cls.category = category

    def _component(self, slug, **kwargs):
        page = ComponentPage(title="Potentiometer", slug=slug, **kwargs)
        self.category.add_child(instance=page)
        return page

    @patch("stock.client.list_by_group")
    def test_variants_come_from_the_group(self, mock_group):
        mock_group.return_value = [
            {"part_number": "0390", "short_name": "potentiometer",
             "description": "potentiometer, 10kΩ, panel mount", "on_floor": 30},
            {"part_number": "0308", "short_name": "potentiometer",
             "description": "potentiometer, trimmer, 500Ω", "on_floor": 20},
        ]
        page = self._component("pot-a", inventory_group="potentiometers")
        variants = page.get_context(RequestFactory().get("/"))["variants"]
        self.assertEqual([v["number"] for v in variants], ["0390", "0308"])
        # short_name is the same word for every part in the group, so the
        # description is what actually distinguishes them.
        self.assertEqual(variants[0]["label"], "potentiometer, 10kΩ, panel mount")

    @patch("stock.client.list_by_group")
    def test_hand_listed_parts_are_additive(self, mock_group):
        """A page can use a group and still name a stray part filed elsewhere."""
        mock_group.return_value = [
            {"part_number": "0390", "short_name": "pot", "description": "d", "on_floor": 1}
        ]
        page = self._component("pot-b", inventory_group="potentiometers")
        StockedPart.objects.create(page=page, part_number="9999", label="oddity")

        with patch("stock.client.get_stock_many", return_value={}):
            variants = page.get_context(RequestFactory().get("/"))["variants"]
        self.assertEqual([v["number"] for v in variants], ["0390", "9999"])

    @patch("stock.client.list_by_group")
    def test_a_part_in_both_is_not_duplicated(self, mock_group):
        mock_group.return_value = [
            {"part_number": "0390", "short_name": "pot", "description": "d", "on_floor": 1}
        ]
        page = self._component("pot-c", inventory_group="potentiometers")
        StockedPart.objects.create(page=page, part_number="0390", label="dupe")

        with patch("stock.client.get_stock_many", return_value={}):
            variants = page.get_context(RequestFactory().get("/"))["variants"]
        self.assertEqual([v["number"] for v in variants], ["0390"])

    @patch("stock.client.list_by_group")
    def test_page_still_renders_when_inventory_is_down(self, mock_group):
        """The documentation is the point of the page; stock is a bonus."""
        mock_group.return_value = []
        page = self._component(
            "pot-d", inventory_group="potentiometers",
            docs_what_it_is="<p>A variable resistor.</p>",
        )
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A variable resistor")

    def test_without_a_group_it_falls_back_to_the_inline_list(self):
        page = self._component("pot-e")
        StockedPart.objects.create(page=page, part_number="0390", label="10kΩ")
        with patch("stock.client.get_stock_many", return_value={}):
            variants = page.get_context(RequestFactory().get("/"))["variants"]
        self.assertEqual([v["number"] for v in variants], ["0390"])


class MarkdownRenderingTests(TestCase):
    """The content is markdown, and the pieces that matter must survive nh3."""

    def render(self, text):
        from wagtailmarkdown.utils import render_markdown

        return str(render_markdown(text))

    def test_fenced_code_keeps_its_language_hint(self):
        html = self.render("```cpp\nint x = A0;\n```")
        self.assertIn("<pre>", html)
        self.assertIn("language-cpp", html)
        self.assertIn("int x = A0;", html)

    def test_include_directives_are_not_eaten_as_html(self):
        """6 parts have #include <Servo.h> in their code."""
        html = self.render("```cpp\n#include <Servo.h>\n```")
        self.assertIn("Servo.h", html)

    def test_inline_figure_and_caption_survive(self):
        """59 diagrams are inline <figure> HTML inside the markdown."""
        html = self.render(
            '<figure class="image"><img src="/images/parts/x.gif" alt="X">'
            "<figcaption>A caption</figcaption></figure>"
        )
        for fragment in ("<figure", "<img", "/images/parts/x.gif", "<figcaption", "A caption"):
            self.assertIn(fragment, html)

    def test_scripts_are_still_stripped(self):
        html = self.render("<script>alert(1)</script>\n\nSafe text")
        self.assertNotIn("<script", html)
        self.assertIn("Safe text", html)


class LegacyImagePathTests(TestCase):
    """/images/parts/<file> keeps resolving, so the markdown needs no rewriting."""

    def test_unknown_filename_404s(self):
        self.assertEqual(self.client.get("/images/parts/nope.gif").status_code, 404)

    def test_known_filename_redirects_to_the_image(self):
        import io

        from django.core.files.base import ContentFile
        from PIL import Image as PILImage
        from wagtail.images.models import Image

        from catalog.models import MediaAlias

        buffer = io.BytesIO()
        PILImage.new("RGB", (1, 1)).save(buffer, format="PNG")
        image = Image.objects.create(
            title="diagram",
            file=ContentFile(buffer.getvalue(), name="diagram.png"),
            width=1,
            height=1,
        )
        MediaAlias.objects.create(filename="potentiometer_interior.gif", image=image)
        response = self.client.get("/images/parts/potentiometer_interior.gif")
        self.assertEqual(response.status_code, 302)
        self.assertIn("diagram", response["Location"])
