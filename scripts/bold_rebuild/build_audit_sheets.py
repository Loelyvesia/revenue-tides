from pathlib import Path
from shutil import copy2

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / "bold-rebuild"
SHOTS = RESEARCH / "screenshots"
BEFORE = RESEARCH / "before_after" / "before"
AFTER = RESEARCH / "before_after" / "after"
AFTER.mkdir(parents=True, exist_ok=True)

copies = {
    "hero.webp": "desktop-hero.webp",
    "measurement.webp": "desktop-measurement.webp",
    "prism.webp": "desktop-prism-overlap.webp",
    "f1.webp": "desktop-f1.webp",
    "f2.webp": "desktop-f2.webp",
    "f4.webp": "desktop-f4.webp",
    "observatory.webp": "desktop-observatory.webp",
    "mobile-hero.webp": "mobile-390-hero.webp",
    "mobile-prism.webp": "mobile-390-overlap.webp",
    "mobile-f2.webp": "mobile-390-f2.webp",
    "mobile-f4.webp": "mobile-390-f4.webp",
    "mobile-observatory.webp": "mobile-390-observatory.webp",
}
for target, source in copies.items():
    copy2(SHOTS / source, AFTER / target)

font = ImageFont.load_default(size=24)
small = ImageFont.load_default(size=18)
paper = "#eeeae0"
ink = "#0b3740"


def fit(path: Path, width: int, height: int) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), paper)
    canvas.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
    return canvas


sections = ["hero", "measurement", "prism", "f1", "f2", "f4", "observatory"]
cell_w, cell_h, label_h = 720, 450, 42
sheet = Image.new("RGB", (cell_w * 2, (cell_h + label_h) * len(sections) + 56), paper)
draw = ImageDraw.Draw(sheet)
draw.text((24, 16), "REVENUE TIDES — BEFORE / AFTER", fill=ink, font=font)
for index, name in enumerate(sections):
    y = 56 + index * (cell_h + label_h)
    draw.text((18, y + 10), f"BEFORE · {name.upper()}", fill=ink, font=small)
    draw.text((cell_w + 18, y + 10), f"AFTER · {name.upper()}", fill=ink, font=small)
    sheet.paste(fit(BEFORE / f"{name}.webp", cell_w, cell_h), (0, y + label_h))
    sheet.paste(fit(AFTER / f"{name}.webp", cell_w, cell_h), (cell_w, y + label_h))
sheet.save(RESEARCH / "before-after-desktop.webp", "WEBP", quality=86, method=6)

mobile_names = ["mobile-hero", "mobile-prism", "mobile-f2", "mobile-f4", "mobile-observatory"]
m_w, m_h = 360, 650
mobile = Image.new("RGB", (m_w * len(mobile_names), m_h + 58), paper)
mobile_draw = ImageDraw.Draw(mobile)
for index, name in enumerate(mobile_names):
    mobile_draw.text((index * m_w + 14, 16), name.replace("mobile-", "").upper(), fill=ink, font=small)
    mobile.paste(fit(AFTER / f"{name}.webp", m_w, m_h), (index * m_w, 58))
mobile.save(RESEARCH / "mobile-after-contact-sheet.webp", "WEBP", quality=86, method=6)

promo = Image.new("RGB", (1600, 1200), "#e9eee8")
promo.paste(fit(SHOTS / "desktop-hero.webp", 1600, 700), (0, 0))
promo.paste(fit(SHOTS / "desktop-prism-overlap.webp", 800, 500), (0, 700))
promo.paste(fit(SHOTS / "desktop-f2.webp", 800, 500), (800, 700))
promo.save(RESEARCH / "promotional-screens.webp", "WEBP", quality=88, method=6)

print(f"AFTER COPIES: {len(copies)}")
print("CONTACT SHEETS: 3")
