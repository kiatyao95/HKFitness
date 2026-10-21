"""
HK FITNESS — asset pipeline.

Builds every derivative image the site needs from the raw material in
`My Picture/` and `HK_FITNESS_Signboard.pdf`: brand artwork, the coach
portrait, client comparisons, the studio carousel and the social card.

Run from the project root:
    python tools/build-images.py

Requires: pillow, pymupdf
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "My Picture"
OUT = ROOT / "assets" / "img"
TMP = ROOT / "_tmp"

GOLD = (248, 192, 8)
GOLD_WARM = (240, 160, 32)

FONT_DISPLAY = Path("C:/Windows/Fonts/ariblk.ttf")
FONT_CONDENSED = Path("C:/Windows/Fonts/impact.ttf")
FONT_MONO = Path("C:/Windows/Fonts/consola.ttf")

# Square crop of the mascot plate, used for the header mark and the app icons.
MARK_CROP = (170, 0, 510, 340)


def ensure_dirs() -> None:
    for folder in (
        OUT,
        OUT / "brand",
        OUT / "results",
        OUT / "studio",
        OUT / "icons",
    ):
        folder.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(exist_ok=True)


def save_jpeg(img: Image.Image, relative: str, quality: int = 82) -> None:
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    print(f"  {relative:<38} {img.size[0]}x{img.size[1]}  {path.stat().st_size // 1024} KB")


def save_png(img: Image.Image, relative: str) -> None:
    path = OUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)
    print(f"  {relative:<38} {img.size[0]}x{img.size[1]}  {path.stat().st_size // 1024} KB")


def resize_to_width(img: Image.Image, width: int) -> Image.Image:
    if img.width <= width:
        return img
    height = round(img.height * width / img.width)
    return img.resize((width, height), Image.LANCZOS)


# --------------------------------------------------------------------------- #
# Brand artwork
# --------------------------------------------------------------------------- #


def extract_signboard() -> Image.Image:
    """Pull the artwork back out of the supplied signage PDF."""
    doc = pymupdf.open(ROOT / "HK_FITNESS_Signboard.pdf")
    xref = doc[0].get_images(full=True)[0][0]
    info = doc.extract_image(xref)
    raw = TMP / f"signboard-raw.{info['ext']}"
    raw.write_bytes(info["image"])
    return Image.open(raw).convert("RGB")


def build_brand(signboard: Image.Image) -> None:
    print("brand")

    # The full lockup, trimmed of its outer border, used in the footer.
    width, height = signboard.size
    strip = signboard.crop((6, 6, width - 6, height - 6))
    save_jpeg(resize_to_width(strip, 1800), "brand/signboard.jpg", quality=88)

    # The bear mascot, cropped clear of the Malay signboard line above it and
    # wide enough to keep both dumbbells whole.
    emblem = signboard.crop((17, 44, 368, 292))
    save_png(emblem, "brand/bear.png")

    # The mascot artwork carries its own black backdrop, so it is shipped as a
    # plate for use inside a bordered tile. Cutting it out would leave the
    # brush streaks visibly clipped at the crop edge. Flat art quantises well,
    # which keeps the file a fraction of the full-colour PNG.
    plate = emblem.resize((640, round(emblem.height * 640 / emblem.width)), Image.LANCZOS)
    save_png(plate.quantize(colors=256, method=Image.MEDIANCUT), "brand/bear-plate.png")

    # Compact square mark for the header. The head, ears and the tops of the
    # dumbbells are what still read at 38px, so the wide plate is cropped down
    # to that. 256px covers a 40px slot on any current display.
    mark = plate.crop(MARK_CROP).resize((256, 256), Image.LANCZOS)
    save_png(mark.quantize(colors=256, method=Image.MEDIANCUT), "brand/bear-mark.png")


# --------------------------------------------------------------------------- #
# Portrait
# --------------------------------------------------------------------------- #


def build_portrait() -> None:
    print("portrait")
    src = Image.open(RAW / "My Photo" / "WhatsApp Image 2026-10-20 at 20.09.38 (1).jpeg").convert("RGB")
    width, height = src.size

    # The source carries a magazine watermark across the top-left wall. That
    # area is a flat grey backdrop, so a clean patch from just below it can be
    # cloned over the mark instead of cropping into the subject.
    patch = src.crop((0, 92, 270, 182))
    mask = Image.new("L", patch.size, 255)
    mask = mask.filter(ImageFilter.GaussianBlur(6))
    src.paste(patch, (0, 0), mask)

    portrait = resize_to_width(src, 1100)
    portrait = portrait.filter(ImageFilter.UnsharpMask(radius=1.3, percent=45, threshold=3))
    save_jpeg(portrait, "coach-portrait.jpg", quality=86)

    # Tight square crop for small circular/rounded usages.
    square_side = portrait.width
    top = round(portrait.height * 0.10)
    square = portrait.crop((0, top, square_side, min(top + square_side, portrait.height)))
    save_jpeg(square.resize((640, 640), Image.LANCZOS), "coach-portrait-square.jpg", quality=85)


# --------------------------------------------------------------------------- #
# Client transformations
# --------------------------------------------------------------------------- #


def split_pair(img: Image.Image, box: tuple[int, int, int, int], name: str) -> None:
    """Crop the photo area out of a composite and split it into before/after."""
    photo = img.crop(box)
    midpoint = photo.width // 2
    before = photo.crop((0, 0, midpoint, photo.height))
    after = photo.crop((midpoint, 0, photo.width, photo.height))

    # Both halves must be identical in size for the comparison slider.
    after = after.resize(before.size, Image.LANCZOS)
    save_jpeg(before, f"results/{name}-before.jpg", quality=85)
    save_jpeg(after, f"results/{name}-after.jpg", quality=85)


def build_results() -> None:
    print("results")

    # Feature set — highest resolution source, portrait halves for the slider.
    feature = Image.open(RAW / "Client Before After" / "WhatsApp Image 2026-10-20 at 20.09.40.jpeg").convert("RGB")
    split_pair(feature, (0, 0, feature.width, feature.height), "feature")

    front = Image.open(RAW / "Client Before After" / "WhatsApp Image 2026-10-20 at 20.09.39.jpeg").convert("RGB")
    split_pair(front, (0, 0, front.width, front.height), "front")

    back = Image.open(RAW / "Client Before After" / "WhatsApp Image 2026-10-20 at 20.09.39 (1).jpeg").convert("RGB")
    split_pair(back, (0, 0, back.width, back.height), "back")

    # Phone screenshots — trim the status bar, promotional bands and labels.
    female = Image.open(RAW / "Client Before After" / "WhatsApp Image 2026-10-20 at 20.09.39 (2).jpeg").convert("RGB")
    split_pair(female, (0, 288, female.width, 846), "waist")

    profile = Image.open(RAW / "Client Before After" / "WhatsApp Image 2026-10-20 at 20.09.39 (3).jpeg").convert("RGB")
    split_pair(profile, (0, 292, profile.width, 846), "profile")


# --------------------------------------------------------------------------- #
# Studio carousel
# --------------------------------------------------------------------------- #

# Shown whole in the carousel — no crop, no resample. The order matches the
# slides in `index.html`.
STUDIO_PHOTOS = [
    "WhatsApp Image 2026-10-21 at 11.07.46 (1).jpeg",
    "WhatsApp Image 2026-10-21 at 11.07.42 (1).jpeg",
    "WhatsApp Image 2026-10-21 at 11.07.42.jpeg",
    "WhatsApp Image 2026-10-21 at 11.07.44.jpeg",
    "WhatsApp Image 2026-10-21 at 11.07.47.jpeg",
    "WhatsApp Image 2026-10-21 at 11.07.46.jpeg",
]


def build_studio() -> None:
    print("studio")
    for index, photo in enumerate(STUDIO_PHOTOS, start=1):
        relative = f"studio/gym-{index:02d}.jpg"
        target = OUT / relative
        # The carousel shows each frame whole, so the files are copied rather
        # than cropped or resampled.
        shutil.copyfile(RAW / "Gym Room" / photo, target)
        width, height = Image.open(target).size
        print(f"  {relative:<38} {width}x{height}  {target.stat().st_size // 1024} KB")


# --------------------------------------------------------------------------- #
# Icons
# --------------------------------------------------------------------------- #


def build_icons(plate: Image.Image) -> None:
    """The mascot inside a gold frame — the frame keeps the tile visible in a
    browser tab, where a black square would disappear."""
    print("icons")
    size = 512
    frame = 46

    mark = plate.crop(MARK_CROP).resize((size - frame * 2, size - frame * 2), Image.LANCZOS)
    tile = Image.new("RGB", (size, size), GOLD)
    tile.paste(mark, (frame, frame))

    for px, name in ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")):
        tile.resize((px, px), Image.LANCZOS).save(OUT / "icons" / name, "PNG", optimize=True)

    tile.resize((32, 32), Image.LANCZOS).save(OUT / "icons" / "favicon-32.png", "PNG", optimize=True)
    tile.resize((16, 16), Image.LANCZOS).save(OUT / "icons" / "favicon-16.png", "PNG", optimize=True)
    tile.resize((180, 180), Image.LANCZOS).save(
        OUT / "icons" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print("  icons/*")

    # Maskable icon keeps the mark inside the 80% safe zone.
    base = Image.new("RGB", (size, size), GOLD)
    base.paste(tile.resize((410, 410), Image.LANCZOS), (51, 51))
    base.save(OUT / "icons" / "maskable-512.png", "PNG", optimize=True)


# --------------------------------------------------------------------------- #
# Social card
# --------------------------------------------------------------------------- #


def fitted_font(path: Path, text: str, max_width: int, start_size: int) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > 8:
        font = ImageFont.truetype(str(path), size)
        if ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(str(path), size)


def build_og(bear: Image.Image) -> None:
    print("social")
    width, height = 1200, 630
    card = Image.new("RGB", (width, height), (8, 8, 8))
    draw = ImageDraw.Draw(card, "RGBA")

    # Angular tonal panels, echoing the signboard's brush sweeps.
    draw.polygon([(600, 0), (1200, 0), (1200, 630), (420, 630)], fill=(22, 21, 18))
    draw.polygon([(830, 0), (1200, 0), (1200, 630), (650, 630)], fill=(34, 31, 24))
    draw.polygon([(1090, 0), (1200, 0), (1200, 210)], fill=(48, 42, 24))

    mono = ImageFont.truetype(str(FONT_MONO), 24)
    condensed = ImageFont.truetype(str(FONT_CONDENSED), 38)
    display = fitted_font(FONT_DISPLAY, "BUILD STRENGTH.", 690, 74)

    draw.rectangle([0, 0, width - 1, height - 1], outline=(255, 255, 255, 24), width=2)
    draw.text((76, 70), "HK FITNESS  /  PERSONAL TRAINING", font=mono, fill=GOLD)
    draw.text((74, 132), "MOVE WELL.", font=display, fill=(255, 255, 255))
    draw.text((74, 214), "BUILD STRENGTH.", font=display, fill=(255, 255, 255))
    draw.text((74, 296), "LIVE BETTER.", font=display, fill=GOLD)

    draw.line([(76, 424), (196, 424)], fill=GOLD, width=8)
    draw.text((76, 460), "10+ YEARS  ·  100+ CLIENTS  ·  MOVE PAIN-FREE", font=condensed, fill=(255, 255, 255, 214))
    draw.text((76, 520), "HK FITNESS  ·  PERSONAL COACHING STUDIO", font=mono, fill=(255, 255, 255, 110))

    # The mascot keeps its black backdrop, so blend it in screen like the site
    # does rather than pasting a visible rectangle.
    mascot = bear.resize((400, round(bear.height * 400 / bear.width)), Image.LANCZOS)
    box = (width - mascot.width - 24, height - mascot.height - 24)
    region = card.crop((box[0], box[1], box[0] + mascot.width, box[1] + mascot.height))
    card.paste(ImageChops.screen(region, mascot), box)

    save_jpeg(card, "og-image.jpg", quality=90)


def main() -> None:
    ensure_dirs()
    signboard = extract_signboard()
    build_brand(signboard)
    build_portrait()
    build_results()
    build_studio()
    build_icons(Image.open(OUT / "brand" / "bear-plate.png").convert("RGB"))
    build_og(Image.open(OUT / "brand" / "bear.png").convert("RGB"))
    print("done")


if __name__ == "__main__":
    main()
