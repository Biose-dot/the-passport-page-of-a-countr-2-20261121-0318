#!/usr/bin/env python3
"""Kestrelia passport spread — draws a fictional passport spread to /output/entry.png.

Fully deterministic, no network, stdlib + Pillow only. Fonts are bundled in
fonts/ (DejaVu, permissive licence) so the sandboxed run renders identically.
All persons, places and dates are invented; the document is fictional.
"""
import math
import os
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 720
OUT = Path(os.environ.get("OUTPUT_PATH", "/output/entry.png"))

BASE = Path(__file__).resolve().parent
FDIR = BASE / "fonts"

# Palette — warm passport paper, restrained official colours.
PAPER = (243, 236, 216)
PAPER2 = (238, 229, 203)
INK = (32, 38, 46)
NAVY = (31, 58, 95)
NAVY_LT = (58, 90, 135)
GOLD = (176, 141, 58)
GOLD_LT = (201, 170, 90)
TEAL = (31, 106, 104)
RUST = (154, 63, 46)
GREY = (110, 112, 108)
LINE = (150, 142, 120)


def font(name, size):
    p = FDIR / name
    try:
        return ImageFont.truetype(str(p), size)
    except Exception:
        return ImageFont.load_default(size=size)


SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
MONO = lambda s: font("DejaVuSansMono.ttf", s)


# ---------------------------------------------------------------- MRZ (ICAO 9303)
def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = ("P<KST" + "MARLOWE<<ELENA<VERA").ljust(44, "<")
    pnum = "K8472913<"
    dob = "910612"
    exp = "330313"
    pers = "PORTANSELM<<<<"
    line2 = (
        pnum + mrz_check(pnum)
        + "KST" + dob + mrz_check(dob)
        + "F" + exp + mrz_check(exp)
        + pers + mrz_check(pers)
    )
    line2 = line2 + mrz_check(line2)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- helpers
def text(d, xy, s, f, fill=INK, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def centre(d, cx, y, s, f, fill=INK):
    d.text((cx, y), s, font=f, fill=fill, anchor="ma")


def label_value(d, x, y, label, value, vf, label_size=9, value_size=15, gap=11):
    d.text((x, y), label, font=SANS(9), fill=GREY, anchor="la")
    d.text((x, y + gap), value, font=vf, fill=INK, anchor="la")


def guilloche(d, box, colour, step=7, amp=2.2):
    """Fine wavy security lines inside a box."""
    x0, y0, x1, y1 = box
    rnd = random.Random(7)
    for yy in range(y0 + 4, y1 - 2, step):
        pts = []
        ph = rnd.uniform(0, 6)
        for xx in range(x0, x1 + 1, 6):
            pts.append((xx, yy + amp * math.sin(xx / 23.0 + ph)))
        d.line(pts, fill=colour, width=1)


def emblem(d, cx, cy, r):
    """Kestrelia coat of arms: gold ring, navy disc, kestrel in flight, waves."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=3)
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
              fill=NAVY, outline=GOLD_LT, width=1)
    # stylised kestrel: body + swept wings in gold
    d.polygon([(cx - r * 0.62, cy + r * 0.05), (cx - r * 0.05, cy - r * 0.42),
               (cx + r * 0.28, cy - r * 0.05), (cx + r * 0.05, cy + r * 0.10)],
              fill=GOLD_LT)
    d.polygon([(cx - r * 0.05, cy - r * 0.42), (cx + r * 0.55, cy - r * 0.55),
               (cx + r * 0.30, cy - r * 0.02)], fill=GOLD_LT)
    d.ellipse([cx + r * 0.28, cy - r * 0.28, cx + r * 0.44, cy - r * 0.12],
              fill=GOLD_LT)
    d.ellipse([cx + r * 0.36, cy - r * 0.24, cx + r * 0.40, cy - r * 0.20],
              fill=NAVY)
    # three waves, kept inside the disc
    for i, wy in enumerate((0.28, 0.44, 0.60)):
        y = cy + r * wy
        x_start = cx - r * 0.58
        pts = [(x_start + k * 4, y + 3 * math.sin(k / 2.4 + i))
               for k in range(int(r * 1.16 / 4) + 1)]
        d.line(pts, fill=GOLD_LT, width=2)
    d.text((cx, cy + r + 4), "★", font=SANS_B(11), fill=GOLD, anchor="ma")


def draw_portrait(d, box):
    """Stylised flat-illustration portrait (drawn in code, not a photo)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # background: pale blue-grey with faint guilloche
    d.rectangle(box, fill=(196, 208, 216))
    guilloche(d, box, (178, 192, 202), step=9, amp=1.6)
    cx = (x0 + x1) // 2
    # shoulders / teal jacket
    d.polygon([(x0 + 8, y1), (x0 + 8, y0 + h * 0.66), (cx - 34, y0 + h * 0.60),
               (cx, y0 + h * 0.58), (cx + 34, y0 + h * 0.60),
               (x1 - 8, y0 + h * 0.66), (x1 - 8, y1)], fill=(38, 96, 92))
    # shirt V + collar
    d.polygon([(cx - 26, y0 + h * 0.60), (cx, y0 + h * 0.86), (cx + 26, y0 + h * 0.60),
               (cx + 12, y0 + h * 0.58), (cx, y0 + h * 0.66), (cx - 12, y0 + h * 0.58)],
              fill=(238, 234, 222))
    d.polygon([(cx - 34, y0 + h * 0.60), (cx, y0 + h * 0.72), (cx - 14, y0 + h * 0.58)],
              fill=(24, 70, 68))
    d.polygon([(cx + 34, y0 + h * 0.60), (cx, y0 + h * 0.72), (cx + 14, y0 + h * 0.58)],
              fill=(24, 70, 68))
    # neck + face
    skin = (216, 178, 148)
    skin_d = (198, 158, 128)
    d.rectangle([cx - 13, y0 + h * 0.44, cx + 13, y0 + h * 0.62], fill=skin_d)
    d.ellipse([cx - 34, y0 + h * 0.10, cx + 34, y0 + h * 0.52], fill=skin)
    # hair: dark chestnut bob framing the face
    hair = (74, 48, 36)
    d.pieslice([cx - 40, y0 + h * 0.02, cx + 40, y0 + h * 0.46], 180, 360, fill=hair)
    d.ellipse([cx - 40, y0 + h * 0.06, cx - 8, y0 + h * 0.52], fill=hair)
    d.ellipse([cx + 8, y0 + h * 0.06, cx + 40, y0 + h * 0.52], fill=hair)
    d.pieslice([cx - 36, y0 + h * 0.04, cx + 36, y0 + h * 0.30], 180, 360, fill=hair)
    # brows, eyes, nose, lips — minimal, calm
    for sx in (-1, 1):
        ex = cx + sx * 15
        d.line([(ex - 8, y0 + h * 0.285), (ex + 8, y0 + h * 0.278)], fill=hair, width=2)
        d.ellipse([ex - 6, y0 + h * 0.305, ex + 6, y0 + h * 0.325], fill=(250, 246, 238))
        d.ellipse([ex - 2.5, y0 + h * 0.308, ex + 2.5, y0 + h * 0.322], fill=(58, 44, 34))
    d.line([(cx, y0 + h * 0.33), (cx - 2, y0 + h * 0.40)], fill=skin_d, width=2)
    d.arc([cx - 9, y0 + h * 0.425, cx + 9, y0 + h * 0.455], 0, 180, fill=(168, 96, 84), width=2)
    # small gold earring + jacket pin (kestrel)
    d.ellipse([cx - 38, y0 + h * 0.42, cx - 34, y0 + h * 0.435], fill=GOLD)
    d.ellipse([cx + 34, y0 + h * 0.42, cx + 38, y0 + h * 0.435], fill=GOLD)
    d.polygon([(cx + 22, y0 + h * 0.72), (cx + 30, y0 + h * 0.70),
               (cx + 27, y0 + h * 0.76)], fill=GOLD_LT)
    # frame
    d.rectangle(box, outline=NAVY, width=2)
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], outline=GOLD_LT, width=1)


def stamp_layer(size, lines, colour, shape="oval", angle=-14, font_size=15):
    """A rotated rubber stamp on its own transparent layer."""
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    if shape == "oval":
        d.ellipse([cx - 105, cy - 52, cx + 105, cy + 52], outline=colour, width=4)
        d.ellipse([cx - 96, cy - 44, cx + 96, cy + 44], outline=colour, width=1)
    else:
        d.rounded_rectangle([cx - 105, cy - 52, cx + 105, cy + 52], radius=8,
                            outline=colour, width=4)
        d.rounded_rectangle([cx - 97, cy - 44, cx + 97, cy + 44], radius=6,
                            outline=colour, width=1)
    y = cy - 38
    for i, (s, f) in enumerate(lines):
        centre(d, cx, y, s, f, fill=colour)
        y += 19 if i < len(lines) - 1 else 0
    # star separators on the date line
    return img.rotate(angle, resample=Image.BICUBIC, expand=False)


def draw_left_page(img, d):
    x0, y0, x1 = 28, 24, 500
    # header
    centre(d, (x0 + x1) // 2, y0, "REPUBLIC OF KESTRELIA", SERIF_B(21), fill=NAVY)
    centre(d, (x0 + x1) // 2, y0 + 26, "PASSPORT  ·  PASSEPORT", SANS(10), fill=GOLD)
    d.line([(x0 + 14, y0 + 46), (x1 - 14, y0 + 46)], fill=GOLD, width=2)
    emblem(d, 60, y0 + 78, 24)
    centre(d, (x0 + x1) // 2 + 18, y0 + 62, "DATA PAGE", SANS_B(11), fill=NAVY)
    d.text((132, y0 + 74), "Issued by the Passport Office,\nPort Anselm", font=SANS(10),
           fill=GREY)

    # portrait
    px0, py0, px1, py1 = x0 + 14, y0 + 118, x0 + 158, y0 + 306
    draw_portrait(d, (px0, py0, px1, py1))
    centre(d, (px0 + px1) // 2, py1 + 6, "PHOTOGRAPH  ·  35 × 45 mm", SANS(8), fill=GREY)

    # data fields, two columns right of portrait
    fx = x0 + 176
    label_value(d, fx, y0 + 118, "SURNAME / NOM", "MARLOWE", SERIF_B(16))
    label_value(d, fx, y0 + 152, "GIVEN NAMES / PRÉNOMS", "ELENA VERA", SERIF_B(16))
    label_value(d, fx, y0 + 186, "NATIONALITY / NATIONALITÉ", "KESTRELIAN", SERIF_B(14))
    label_value(d, fx, y0 + 220, "DATE OF BIRTH", "12 JUN 1991", SERIF_B(14))
    label_value(d, fx + 150, y0 + 220, "SEX / SEXE", "F", SERIF_B(14))
    label_value(d, fx + 210, y0 + 220, "HEIGHT", "1.68 m", SERIF_B(14))
    label_value(d, fx, y0 + 254, "PLACE OF BIRTH", "PORT ANSELM, KESTRELIA", SERIF_B(13))
    label_value(d, fx, y0 + 288, "DATE OF ISSUE", "14 MAR 2023", SERIF_B(14))
    label_value(d, fx + 150, y0 + 288, "DATE OF EXPIRY", "13 MAR 2033", SERIF_B(14))

    # type / code / number strip
    sy = y0 + 330
    d.line([(x0 + 14, sy), (x1 - 14, sy)], fill=LINE, width=1)
    for i, (lab, val) in enumerate([("TYPE", "P"), ("CODE", "KST"),
                                    ("PASSPORT No.", "K8472913")]):
        xx = x0 + 14 + i * 150
        d.text((xx, sy + 8), lab, font=SANS(9), fill=GREY)
        d.text((xx, sy + 20), val, font=SERIF_B(15), fill=NAVY)
    d.text((x0 + 14, sy + 52), "HOLDER'S SIGNATURE", font=SANS(9), fill=GREY)
    # signature in script-like serif italic
    d.text((x0 + 14, sy + 64), "Elena Vera Marlowe", font=SERIF(20), fill=(52, 58, 88))
    d.line([(x0 + 14, sy + 88), (x0 + 220, sy + 88)], fill=LINE, width=1)

    # MRZ
    l1, l2 = build_mrz()
    mz = y0 + 440
    d.rectangle([x0 + 8, mz - 8, x1 - 8, mz + 52], fill=(232, 224, 196))
    d.text((x0 + 16, mz), l1, font=MONO(15), fill=INK)
    d.text((x0 + 16, mz + 22), l2, font=MONO(15), fill=INK)
    d.text((x0 + 16, mz + 56), "MRZ — reads: P<KST MARLOWE ELENA VERA · K8472913 · 12 JUN 1991 · 13 MAR 2033",
           font=SANS(8), fill=GREY)


def draw_right_page(img, d):
    x0, y0, x1 = 524, 24, 996
    centre(d, (x0 + x1) // 2, y0, "VISAS", SERIF_B(19), fill=NAVY)
    centre(d, (x0 + x1) // 2, y0 + 26, "VISA  ·  ENTRY & EXIT STAMPS", SANS(10), fill=GOLD)
    d.line([(x0 + 14, y0 + 46), (x1 - 14, y0 + 46)], fill=GOLD, width=2)

    # visa vignette — Meridian Republic
    vy0 = y0 + 60
    d.rectangle([x0 + 14, vy0, x1 - 14, vy0 + 118], outline=TEAL, width=2)
    guilloche(d, (x0 + 16, vy0 + 2, x1 - 16, vy0 + 116), (178, 205, 198), step=8)
    centre(d, (x0 + x1) // 2, vy0 + 8, "MERIDIAN REPUBLIC — VISA", SERIF_B(13), fill=TEAL)
    centre(d, (x0 + x1) // 2, vy0 + 30, "SINGLE ENTRY  ·  TOURIST  ·  30 DAYS", SANS_B(11), fill=INK)
    d.text((x0 + 30, vy0 + 54), "Issued:  12 SEP 2024 — Meridian Consulate, Port Anselm",
           font=SANS(11), fill=INK)
    d.text((x0 + 30, vy0 + 72), "Valid until:  12 DEC 2024        Fee paid:  40 meridia",
           font=SANS(11), fill=INK)
    d.text((x0 + 30, vy0 + 90), "Visa No. MR-2024-118734  ·  See conditions overleaf",
           font=SANS(10), fill=GREY)

    # stamps
    stamps = [
        ((620, 300), [("THALASSA", SANS_B(15)), ("★  ARRIVAL  ★", SANS(11)),
                      ("02 APR 2024", SANS_B(15)), ("PORT OF THALASSA", SANS(10))],
         (44, 92, 150), "oval", -13),
        ((880, 330), [("MERIDIAN REPUBLIC", SANS_B(12)), ("★  ENTRY  ★", SANS(11)),
                      ("19 SEP 2024", SANS_B(15)), ("MERIDIAN BORDER", SANS(10))],
         (36, 110, 74), "rect", 11),
        ((700, 470), [("KESTRELIA", SANS_B(15)), ("★  ENTRY  ★", SANS(11)),
                      ("27 JAN 2025", SANS_B(15)), ("PORT ANSELM", SANS(10))],
         (154, 63, 46), "oval", -8),
    ]
    for (cx, cy), lines, colour, shape, angle in stamps:
        layer = stamp_layer((260, 150), lines, colour, shape, angle)
        img.paste(layer, (cx - 130, cy - 75), layer)

    # departure stamp, small, bottom right
    layer = stamp_layer((220, 130),
                        [("THALASSA", SANS_B(13)), ("DEPARTURE", SANS(10)),
                         ("09 APR 2024", SANS_B(13))], (44, 92, 150), "rect", 9)
    img.paste(layer, (790, 430), layer)

    # the telling paperwork detail — conditions box
    by0 = y0 + 556
    d.rectangle([x0 + 14, by0, x1 - 14, by0 + 96], outline=RUST, width=2)
    d.rectangle([x0 + 18, by0 + 4, x1 - 18, by0 + 92], outline=(214, 170, 150), width=1)
    centre(d, (x0 + x1) // 2, by0 + 10, "CONDITIONS OF ISSUE", SANS_B(11), fill=RUST)
    d.text((x0 + 30, by0 + 30),
           "Paid work in the pearl fisheries is prohibited\n"
           "without a seasonal permit — Kestrelian\n"
           "Maritime Code §7.  Permit stamp required\n"
           "at Port Anselm before embarkation.",
           font=SANS(12), fill=INK)
    d.text((x1 - 30, by0 + 30), "PERMIT\nNOT HELD", font=SANS_B(11), fill=RUST, anchor="ra")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # paper tint + faint guilloche wash
    guilloche(d, (0, 0, W, H), (233, 224, 198), step=11, amp=1.2)
    # outer border + centre fold
    d.rectangle([10, 10, W - 11, H - 11], outline=NAVY, width=3)
    d.rectangle([16, 16, W - 17, H - 17], outline=GOLD_LT, width=1)
    d.line([(W // 2, 18), (W // 2, H - 18)], fill=(200, 190, 160), width=2)
    # page numbers
    d.text((40, H - 34), "12", font=SANS(10), fill=GREY)
    d.text((W - 40, H - 34), "13", font=SANS(10), fill=GREY)
    centre(d, W // 2, H - 34, "SPECIMEN — FICTIONAL DOCUMENT · REPUBLIC OF KESTRELIA DOES NOT EXIST",
           SANS(8), fill=GREY)

    draw_left_page(img, d)
    draw_right_page(img, d)

    out = OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {out.stat().st_size} bytes {img.size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
