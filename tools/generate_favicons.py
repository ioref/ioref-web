#!/usr/bin/env python3
"""Regenerate every raster favicon from static/icon.svg.

static/icon.svg is the only favicon file meant to be edited by hand: the
canonical ioRef glyph, shared with .github/branding and ioref-inventory under
that same name. Everything else this writes (favicon.ico, favicon-16x16.png,
favicon-32x32.png, apple-touch-icon.png) is a derived artifact, committed
anyway because whitenoise serves static/ as-is with no build step; there is
nowhere else for a browser to fetch them from at request time. Those names
stay browser-convention rather than following the icon.svg rename, since
that is what HTML favicon discovery actually expects.

Run this after editing the SVG, and commit the results alongside it:

    uv run python tools/generate_favicons.py

Requires Inkscape on PATH for rasterising the SVG; Pillow does the resizing,
compositing and .ico packing from there. Pillow is a dev dependency only:
`uv sync --no-dev`, what the Dockerfile runs, does not install it, because
this script runs by hand, occasionally, not at request time or in CI.
Inkscape is not a Python package at all and has no dependency entry; install
it separately (`apt install inkscape` or equivalent).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

STATIC = Path(__file__).resolve().parent.parent / "static"
SVG = STATIC / "icon.svg"

# The apple-touch-icon composites onto this rather than staying transparent:
# a transparent PNG there can render as a solid black square on an iOS home
# screen. It is the site's own off-white, not plain white.
TOUCH_ICON_BACKGROUND = (253, 253, 253, 255)

# Matches what the original hand-supplied favicon.ico already carried.
ICO_SIZES = [16, 32, 48, 64, 128, 256]

RASTER_SIZE = 1024  # Rendered once at this size; everything else downsamples from it.


def rasterize(svg_path: Path, size: int, out_path: Path) -> None:
    subprocess.run(
        [
            "inkscape", str(svg_path),
            "--export-type=png",
            f"--export-filename={out_path}",
            f"--export-width={size}",
            f"--export-height={size}",
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    if shutil.which("inkscape") is None:
        sys.exit(
            "inkscape not found on PATH. It is the SVG rasteriser this script "
            "uses; install it (or run this on a machine that has it) and try "
            "again. Nothing was written."
        )

    with tempfile.TemporaryDirectory() as tmp:
        master_path = Path(tmp) / "master.png"
        rasterize(SVG, RASTER_SIZE, master_path)
        master = Image.open(master_path).convert("RGBA")

        for size in (16, 32):
            master.resize((size, size), Image.LANCZOS).save(
                STATIC / f"favicon-{size}x{size}.png"
            )

        touch = Image.new("RGBA", master.size, TOUCH_ICON_BACKGROUND)
        touch.alpha_composite(master)
        touch.convert("RGB").resize((180, 180), Image.LANCZOS).save(
            STATIC / "apple-touch-icon.png"
        )

        # Pillow's ICO writer resizes internally from `sizes`; it does not
        # take append_images the way multi-frame TIFF/JPEG saves do. Passing
        # pre-resized frames there silently produces a single-size .ico with
        # no error, found only by checking the frame count after the fact,
        # not by anything Pillow raised.
        master.save(STATIC / "favicon.ico", sizes=[(s, s) for s in ICO_SIZES])

    print(f"Regenerated favicon.ico, favicon-16x16.png, favicon-32x32.png and "
          f"apple-touch-icon.png in {STATIC}/ from {SVG.name}.")


if __name__ == "__main__":
    main()
