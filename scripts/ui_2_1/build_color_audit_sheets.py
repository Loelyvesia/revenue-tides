from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[2] / "research" / "ui-2-1-color"
PAGE = (238, 236, 229)
INK = (32, 35, 33)
COPPER = (149, 90, 59)


def continuity_sheets() -> None:
    names = [
        "desktop-hero.webp",
        "desktop-measurement.webp",
        "desktop-prism-overlap.webp",
        "desktop-f1.webp",
        "desktop-f2.webp",
        "desktop-f4.webp",
        "desktop-observatory.webp",
    ]
    labels = ["HERO", "MEASUREMENT", "QUARTER PRISM", "F1", "F2", "F4", "OBSERVATORY"]
    frames: list[Image.Image] = []
    for name, label in zip(names, labels, strict=True):
        image = Image.open(ROOT / "screenshots" / name).convert("RGB").resize((720, 450))
        strip = Image.new("RGB", (720, 28), PAGE)
        ImageDraw.Draw(strip).text((12, 7), label, fill=INK)
        frames.extend((strip, image))
    canvas = Image.new("RGB", (720, sum(frame.height for frame in frames)), PAGE)
    y = 0
    for frame in frames:
        canvas.paste(frame, (0, y))
        y += frame.height
    canvas.save(ROOT / "color-continuity-vertical.webp", "WEBP", quality=82, method=6)
    ImageOps.grayscale(canvas).save(ROOT / "color-continuity-grayscale.webp", "WEBP", quality=82, method=6)


def comparison_sheet() -> None:
    names = ["hero.webp", "prism.webp", "f2.webp", "f4.webp", "mobile-390-prism.webp"]
    canvas = Image.new("RGB", (1220, len(names) * 410 + 40), PAGE)
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 10), "BEFORE", fill=INK)
    draw.text((620, 10), "AFTER", fill=INK)
    for row, name in enumerate(names):
        for column, side in enumerate(("before", "after")):
            image = Image.open(ROOT / "before_after" / side / name).convert("RGB")
            image.thumbnail((590, 380))
            x = 10 + column * 610 + (590 - image.width) // 2
            y = 40 + row * 410 + (380 - image.height) // 2
            canvas.paste(image, (x, y))
        draw.text((10, 40 + row * 410), name, fill=COPPER)
    canvas.save(ROOT / "before-after-contact-sheet.webp", "WEBP", quality=82, method=6)


if __name__ == "__main__":
    continuity_sheets()
    comparison_sheet()
