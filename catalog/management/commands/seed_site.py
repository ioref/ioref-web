"""Build a representative page tree for development.

Part numbers match those loaded by ioref-inventory's `seed_demo`, so the two
applications join up and stock actually appears on part pages.

Not a migration. The real Directus import is a separate, unwritten job.
"""

from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.images.models import Image
from wagtail.models import Page

from catalog.models import (
    CategoryPage,
    ComponentPage,
    PartSetIndexPage,
    PartSetPage,
    StockedPart,
    SubcategoryPage,
)
from home.models import HomePage

# slug -> title. Order matters: main.css colours by `category-<slug>` and the
# home page lays these out two-then-three.
CATEGORIES = [
    ("input", "Input"),
    ("output", "Output"),
    ("power", "Power"),
    ("connector", "Connector"),
    ("controller", "Controller"),
]

SUBCATEGORIES = {
    "connector": [("board-mount", "Board Mount"), ("wire-to-wire", "Wire to Wire"), ("misc", "Misc.")],
    "power": [("passives", "Passives")],
    "input": [("movement", "Movement"), ("light", "Light")],
}

# (part_number, title, category, subcategory or None, signal_type, about)
PARTS = [
    ("0020", "Flexible protoboard", "connector", "board-mount", "",
     "A flexible half-size breadboard you can solder onto to make a bendable assembly."),
    ("0097", "Small protoboard", "connector", "board-mount", "",
     "17 rows tall, no power rails. For soldering a circuit down semi-permanently."),
    ("0026", "2 x 8cm protoboard", "connector", "board-mount", "",
     "A narrow protoboard for small solder assemblies."),
    ("0107", "2-circuit lever connector", "connector", "wire-to-wire", "",
     "Wago lever nut. Lift the lever, insert the wire, push the lever back down."),
    ("0044", "Butt connector", "connector", "wire-to-wire", "",
     "3M Scotchlok insulation-displacement butt connector for joining two wires."),
    ("2409", "Brass wool", "connector", "misc", "",
     "For cleaning a soldering tip without the thermal shock of a wet sponge."),
    ("0010", "Soldering flux pen", "connector", "misc", "",
     "Refillable flux pen. Useful when preparing a joint, especially surface-mount."),
    ("0028", "Rigid base for Arduino Uno", "controller", None, "Digital",
     "A rigid mounting base matching the Arduino Uno footprint."),
]

# Components stocking several parts. This is the case the old schema could not
# express: data.csv repeats the same capacitor explanation across 33 rows, and
# it collapses to one page with 33 stocked parts.
# (slug, title, category, subcategory, signal_type, about, [(part_number, label)])
MULTI = [
    (
        "ceramic-capacitor", "Ceramic capacitor", "power", "passives", "Analog",
        "Capacitors store electrical energy for later release, filter unwanted "
        "electrical noise, and set timing in oscillators. Ceramic capacitors are "
        "small, cheap and non-polarised, so they can go in either way round.",
        [("0054", "10pF"), ("0056", "22pF"), ("0058", "47pF"), ("0060", "100pF")],
    ),
]

# Content transcribed from https://ioref.org/parts/0390, which the legacy site
# attached to one specific 10kΩ panel-mount pot. None of it is about that part
# in particular, so here it is the component page and every stocked pot hangs
# off it -- 25 rows in data.csv, one explanation.
POTENTIOMETER = {
    "slug": "potentiometer",
    "title": "Potentiometer",
    "category": "input",
    "subcategory": "movement",
    "signal_type": "Continuous",
    "docs": {
        "docs_what_it_is": "<p>The potentiometer is a variable resistor that is "
            "adjusted with rotation (a knob).</p>",
        "docs_when_to_use_it": "<p>When you need an adjustable knob with a finite "
            "range or when you need to measure rotation within a finite range. The "
            "potentiometer has a finite range because it may turn all the way to the "
            "left and stop and turn all the way to the right and stop.</p>",
        "docs_how_it_works": "{interior}"
            "<p>A potentiometer is a variable resistor. The "
            "potentiometer works by sliding a wiper around a resistive track. The "
            "wiper is connected to the center pin, and the outer pins are connected "
            "to either end of the track. The closer the wiper is to either end of the "
            "track, the smaller the resistance is from the wiper to that end of the "
            "track. So, turning the potentiometer all the way to the left would mean "
            "there is no resistance between the wiper and the left pin but a lot of "
            "resistance between the wiper and the right pin. Moving the potentiometer "
            "to the center would cause there to be equal resistances between the "
            "wiper and the two pins.</p>",
        "docs_how_to_use_it": "<p>The rotation of the potentiometer can be measured "
            "with an analog pin on an Arduino. If the left pin is connected to ground "
            "and the right pin is connected to 5V, then the middle pin (the wiper) "
            "will have a voltage that ranges from 0V to 5V.</p>",
        "docs_getting_started": "{schematic}"
            "<p>Wire the outer pins to ground and 5V, and the wiper to an analog "
            "input. This sketch reads it and prints the value.</p>",
        "docs_resources": (
            "<p>Panel-mount hole pattern, from BI Technologies P160 series "
            "datasheet (all values are millimeters):</p>"
            "{panel}"
            "<p>Note that the circle on the left is a clearance hole for the "
            "side-nubbin on the face of the potentiometer, which helps it not "
            "spin freely once installed.</p>"
            "<ul>"
            "<li><a href=\"https://learn.adafruit.com/make-it-change-potentiometers\">"
            "Adafruit Learning System: Make It Change: Potentiometers</a></li>"
            "<li><a href=\"https://learn.sparkfun.com/tutorials/sparkfun-inventors-kit-experiment-guide---v40/circuit-1b-potentiometer\">"
            "Sparkfun Tutorial: Potentiometer</a></li>"
            "<li><a href=\"https://www.arduino.cc/en/tutorial/potentiometer\">"
            "Arduino: Potentiometer Tutorial</a></li>"
            "<li><a href=\"https://www.arduino.cc/en/Tutorial/BuiltInExamples/AnalogReadSerial\">"
            "Arduino: AnalogReadSerial Example</a></li>"
            "</ul>"
        ),
    },
    "code_caption": "Reading a potentiometer on an analog pin",
    # No hand-listed part numbers. Membership is answered in inventory, so
    # adding, retiring or reclassifying a pot needs no edit here.
    "inventory_group": "potentiometers",
    # Diagrams embedded in the prose. On the live site these are served by
    # maker-cards itself from /images/parts/, not by Directus -- so they are
    # absent from the Directus dump and need migrating separately.
    "figures": {
        "interior": (
            "potentiometer_interior.gif",
            "Potentiometer interior",
            "The interior of a potentiometer, with a resistive track, a wiper "
            "that slides along it, and two pins bracketing the track.",
            "Image from Jeff Feddersen at NYU Physical Computing",
        ),
        "schematic": (
            "0390_schematic1.svg",
            "Potentiometer schematic",
            "For this example, the potentiometer is connected to pin A0.",
            "",
        ),
        "panel": (
            "potentiometer_panel_mount_pattern.png",
            "Panel mount drilling pattern",
            "Circle on the right with diameter of 7.5mm; circle on the left "
            "with diameter 3mm; the center to center distance is 7.8mm.",
            "",
        ),
    },
    "code_example": """/*
 * This reads a potentiometer on analog pin POTENTIOMETER_PIN
 * and sends the data back to the computer via serial.
 *
 * Created 2021-04-02 by Perry Naseck
 */

// Set which analog pin on the Arduino that the middle pin of
// the potentiometer is connected to
const int POTENTIOMETER_PIN = A0;

// A place to store the data when received
int potentiometerVal = 0;

void setup() {
  // Setup serial port to send the data back to the computer
  Serial.begin(9600);

  // Setup the potentiometer pin as an input
  pinMode(POTENTIOMETER_PIN, INPUT);
}

void loop() {
  // Get the current potentiometer state (saves a value
  // from 0 to 1023)
  potentiometerVal = analogRead(POTENTIOMETER_PIN);

  // Send the data over serial
  Serial.print("potentiometer: ");
  Serial.println(potentiometerVal);

  // Delay to not send messages too fast
  delay(100);
}""",
    "parts": [
            ('0308', 'trimmer, 500Ω, 3/8"'),
            ('0310', 'trimmer, 1kΩ, 19/32"'),
            ('0312', 'trimmer, 1kΩ, breadboard compatible'),
            ('0314', 'trimmer, 10kΩ, breadboard compatible'),
            ('0316', 'trimmer, 10kΩ, 3/8"'),
            ('0318', 'trimmer, 10kΩ, 19/32"'),
            ('0320', 'trimmer, 100kΩ, 3/8" square'),
            ('0322', 'trimmer, 100kΩ, 19/32"'),
            ('0324', 'trimmer, 1MΩ, breadboard compatible'),
            ('0326', 'trimmer, 1MΩ, 3/8" square'),
            ('0328', '5kΩ 20%, single turn, 6.35mm pin'),
            ('0332', 'trimmer, 10kΩ 20%, single turn'),
            ('0333', 'multi-turn, 10-turn with built-in dial, 10kΩ resistance'),
            ('0334', 'slide, 5kΩ, 90º mount'),
            ('0351', '250kΩ, panel mount, breadboard compatible'),
            ('0376', 'miscellaneous'),
            ('0380', 'slide, 5kΩ, 20mm travel'),
            ('0382', 'slide, 10kΩ, 37mm travel'),
            ('0384', 'slide, 10kΩ, 67mm travel'),
            ('0386', 'soft, linear ribbon sensor, 10kΩ'),
            ('0388', '1kΩ, panel mount, breadboard compatible'),
            ('0390', '10kΩ, panel mount, breadboard compatible'),
            ('0392', '100kΩ, panel mount, breadboard compatible'),
            ('0394', 'soft, circular, 10kΩ'),
            ('1088', '10kΩ'),
    ],
}

PART_SETS = [
    ("intro-kit", "Intro Kit", ["0020", "0107", "0054"]),
    ("soldering-kit", "Soldering Kit", ["2409", "0010"]),
]


def seed_image(filename, title):
    """Load a development fixture image from seed_assets/.

    These were pulled from the live site to make the seeded pages look right.
    They are dev fixtures, not the migration: the real import takes Directus's
    uploads directory plus its directus_files metadata.

    Note there are two sources on the live site. The part photograph comes from
    Directus (admin.ioref.org/assets/<uuid>); the diagrams inside the docs are
    served by maker-cards itself from /images/parts/ via its file-redirect
    route. Both have to be migrated, and only the first is in the Directus dump.
    """
    path = settings.BASE_DIR / "seed_assets" / filename
    if not path.exists():
        return None
    existing = Image.objects.filter(title=title).first()
    if existing:
        return existing
    with path.open("rb") as handle:
        return Image.objects.create(title=title, file=ImageFile(handle, name=filename))


def child(parent, model, slug, title, **kwargs):
    """Idempotent get-or-create for a page, so the command can be re-run."""
    existing = model.objects.child_of(parent).filter(slug=slug).first()
    if existing:
        for key, value in kwargs.items():
            setattr(existing, key, value)
        existing.title = title
        existing.save()
        return existing
    page = model(slug=slug, title=title, **kwargs)
    parent.add_child(instance=page)
    page.save_revision().publish()
    return page


class Command(BaseCommand):
    help = "Create a representative page tree for development."

    @transaction.atomic
    def handle(self, *args, **options):
        home = HomePage.objects.first()
        if home is None:
            self.stderr.write("No HomePage found; run migrate first.")
            return

        # wagtail start ships a placeholder title.
        if home.title != "IOref":
            home.title = "IOref"
            home.save()

        categories = {}
        for slug, title in CATEGORIES:
            categories[slug] = child(home, CategoryPage, slug, title)

        subcategories = {}
        for cat_slug, subs in SUBCATEGORIES.items():
            for slug, title in subs:
                subcategories[(cat_slug, slug)] = child(
                    categories[cat_slug], SubcategoryPage, slug, title
                )

        set_index = child(home, PartSetIndexPage, "part-sets", "Part Sets")
        sets = {
            slug: child(set_index, PartSetPage, slug, title)
            for slug, title, _ in PART_SETS
        }

        parts = {}
        for number, title, cat_slug, sub_slug, signal, about in PARTS:
            parent = (
                subcategories[(cat_slug, sub_slug)] if sub_slug else categories[cat_slug]
            )
            slug = f"{number}-{title.lower().replace(' ', '-').replace('/', '-')}"[:80]
            component = child(
                parent,
                ComponentPage,
                slug,
                title,
                signal_type=signal,
                docs_about=f"<p>{about}</p>",
            )
            StockedPart.objects.update_or_create(
                part_number=number, defaults={"page": component, "sort_order": 0}
            )
            parts[number] = component

        pot = POTENTIOMETER
        pot_image = seed_image("potentiometer.jpg", "Potentiometer")

        # Build the embeds now that the images exist and have ids. Wagtail
        # stores rich-text images as <embed embedtype="image" id="N">; the alt
        # text is carried on the embed, and the caption follows as its own
        # paragraph because Wagtail's embed has nowhere to put one.
        figures = {}
        for slot, (filename, title, alt, credit) in pot["figures"].items():
            image = seed_image(filename, title)
            if image is None:
                figures[slot] = ""
                continue
            caption = alt
            if credit:
                caption += f' <span class="credit">{credit}</span>'
            figures[slot] = (
                f'<embed embedtype="image" id="{image.pk}" format="fullwidth" '
                f'alt="{alt}"/>'
                f'<p class="figure_caption">{caption}</p>'
            )

        docs = {k: v.format(**figures) for k, v in pot["docs"].items()}

        component = child(
            subcategories[(pot["category"], pot["subcategory"])],
            ComponentPage, pot["slug"], pot["title"],
            signal_type=pot["signal_type"],
            code_example=pot["code_example"],
            code_caption=pot["code_caption"],
            inventory_group=pot["inventory_group"],
            image=pot_image,
            **docs,
        )
        # The explicit list is gone: `inventory_group` above supplies it.
        StockedPart.objects.filter(page=component).delete()
        for number, _ in pot["parts"]:
            parts[number] = component

        for slug, title, cat_slug, sub_slug, signal, about, members in MULTI:
            parent = (
                subcategories[(cat_slug, sub_slug)] if sub_slug else categories[cat_slug]
            )
            component = child(
                parent, ComponentPage, slug, title,
                signal_type=signal, docs_what_it_is=f"<p>{about}</p>",
            )
            for order, (number, label) in enumerate(members):
                StockedPart.objects.update_or_create(
                    part_number=number,
                    defaults={"page": component, "label": label, "sort_order": order},
                )
                parts[number] = component

        for slug, _, members in PART_SETS:
            for number in members:
                if number in parts:
                    parts[number].part_sets.add(sets[slug])
                    parts[number].save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(categories)} categories, {len(subcategories)} "
                f"subcategories, {ComponentPage.objects.count()} components "
                f"({StockedPart.objects.count()} stocked parts), {len(sets)} part sets."
            )
        )
