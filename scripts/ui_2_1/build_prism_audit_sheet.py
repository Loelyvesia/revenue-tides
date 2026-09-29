from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2] / "research" / "ui-2-1-prism"
PAGE = (238, 236, 229)
INK = (32, 35, 33)
TEAL = (31, 113, 109)


def fit(path: Path, box: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(box)
    frame = Image.new("RGB", box, PAGE)
    frame.paste(image, ((box[0] - image.width) // 2, (box[1] - image.height) // 2))
    return frame


def main() -> None:
    rows = [
        ("quarter-prism-overlap.webp", "LINEAGE OVERLAP"),
        ("quarter-prism-direct.webp", "DIRECT READING"),
        ("quarter-prism-mobile-390.webp", "MOBILE 390"),
    ]
    width, row_height, header = 1220, 430, 54
    canvas = Image.new("RGB", (width, header + row_height * len(rows)), PAGE)
    draw = ImageDraw.Draw(canvas)
    draw.text((10, 14), "CURRENT", fill=INK)
    draw.text((620, 14), "REDESIGNED", fill=INK)
    draw.line((0, header - 1, width, header - 1), fill=TEAL, width=2)
    for row, (name, label) in enumerate(rows):
        y = header + row * row_height
        draw.text((10, y + 8), label, fill=TEAL)
        for column, side in enumerate(("before", "after")):
            frame = fit(ROOT / "before_after" / side / name, (590, 390))
            canvas.paste(frame, (10 + column * 610, y + 30))
    canvas.save(ROOT / "quarter-prism-before-after.webp", "WEBP", quality=84, method=6)


if __name__ == "__main__":
    main()
