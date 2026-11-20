#!/usr/bin/env python3
"""Render the Friday 20 November 2026 front page (1024x1024 PNG).

Build-time only: main.py ships the baked entry.png, nothing here runs at
grade time. Every figure was verified against a live source on 20 Nov 2026
(see RESEARCH.md). Deterministic: no clock, no randomness, fixed fonts, so
two runs produce identical bytes.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 20                       # page margin
CW = W - 2 * M               # content width: 984

PAPER = (251, 246, 236)
INK = (25, 23, 19)
RED = (168, 30, 35)
RULE = (201, 191, 169)
CARD = (255, 255, 255)
CARD_LINE = (216, 205, 180)
MUTED = (96, 90, 78)
DARK = (30, 33, 40)
CREAM = (245, 233, 200)
GREEN = (30, 122, 52)
AMBER = (178, 106, 0)
BLUE = (29, 78, 158)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(d, text, font, max_w):
    """Greedy word wrap measured in pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, font, fill, max_w, lh, max_lines=None):
    lines = wrap(d, text, font, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def tracked(d, x, y, text, font, fill, tr=2):
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=fill)
        cx += d.textlength(ch, font=font) + tr
    return cx


def tracked_w(d, text, font, tr=2):
    return sum(d.textlength(c, font=font) + tr for c in text) - tr


def centered_tracked(d, cx, y, text, font, fill, tr=2):
    tracked(d, cx - tracked_w(d, text, font, tr) / 2, y, text, font, fill, tr)


def pill(d, x, y, label, kind, size=8):
    bg = {"REPORTED": GREEN, "CLAIM": AMBER, "FORECAST": BLUE}[kind]
    f = F(SANS_B, size)
    w = d.textlength(label, font=f) + 12
    h = size + 6
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    d.text((x + 6, y + 3), label, font=f, fill=(255, 255, 255))
    return w


def numdot(d, cx, cy, n, r=9):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
              outline=(255, 255, 255), width=1)
    f = F(SANS_B, 9)
    t = str(n)
    d.text((cx - d.textlength(t, font=f) / 2, cy - 6), t, font=f,
           fill=(255, 255, 255))


def fit_line(d, text, font, max_w):
    """Shorten with an ellipsis so the line always fits its column."""
    if d.textlength(text, font=font) <= max_w:
        return text
    while text and d.textlength(text + " ...", font=font) > max_w:
        text = text.rsplit(" ", 1)[0] if " " in text else text[:-1]
    return text + " ..."


# ---------------------------------------------------------------- masthead
def masthead(d):
    f_kick = F(SANS_B, 11)
    centered_tracked(d, W / 2, 10, "THE WORLD IN ONE DAY", f_kick, RED, tr=3)
    d.line([(M, 30), (W - M, 30)], fill=RULE, width=1)
    f_date = F(SERIF, 36)
    d.text(((W - d.textlength("Friday 20 November 2026", font=f_date)) / 2, 33),
           "Friday 20 November 2026", font=f_date, fill=INK)
    f_sub = F(SANS_B, 12)
    sub = "Kyiv under fire  |  Cyclone Akvan hits India  |  Asia's markets rout"
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 80), sub,
           font=f_sub, fill=RED)


def stat_strip(d):
    stats = [
        ("242", "DRONES OVER KYIV"),
        ("300,000+", "EVACUATED: AKVAN"),
        ("$2.36bn", "GTA VI DAY ONE*"),
        ("60.7%", "TUMOUR RESPONSE"),
        ("$97.17", "ANTHROPIC CLOSE"),
        ("13", "BALLISTIC MISSILES"),
    ]
    y, h = 96, 40
    bw = (CW - 5 * 8) / 6
    f_n = F(SANS_B, 19)
    f_l = F(SANS_B, 7)
    for i, (num, lab) in enumerate(stats):
        x = M + i * (bw + 8)
        d.rounded_rectangle([x, y, x + bw, y + h], radius=4, fill=DARK)
        nw = d.textlength(num, font=f_n)
        d.text((x + (bw - nw) / 2, y + 3), num, font=f_n, fill=CREAM)
        lw = d.textlength(lab, font=f_l)
        d.text((x + (bw - lw) / 2, y + 26), lab, font=f_l, fill=(185, 178, 160))
    d.text((M, 140), "EUROPE 10  ·  AMERICAS 4  ·  ASIA-PACIFIC 9  ·  MIDEAST 1  ·  "
                     "AFRICA 3  ·  OCEANIA 2  ·  WORLD 7",
           font=F(SANS_B, 9), fill=MUTED)
    tag = "36 STORIES  ·  6 CONTINENTS"
    d.text((W - M - d.textlength(tag, font=F(SANS_B, 9)), 140), tag,
           font=F(SANS_B, 9), fill=RED)


# ------------------------------------------------------- lead illustrations
def illo_kyiv(d, x, y, w, h):
    """Night sky over Kyiv: dark sky, missile streaks, burning skyline."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 46))
    for sx, sy in [(28, 14), (90, 8), (150, 20), (210, 10), (268, 18), (300, 8)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    # missile streaks with glowing heads
    for (x0, y0, x1, y1) in [(40, 8, 90, 52), (150, 4, 185, 46), (250, 10, 285, 44)]:
        d.line([(x + x0, y + y0), (x + x1, y + y1)], fill=(255, 170, 60), width=3)
        d.ellipse([x + x1 - 4, y + y1 - 4, x + x1 + 4, y + y1 + 4],
                  fill=(255, 210, 120))
    # skyline
    base = y + h
    for bx, bw_, bh in [(0, 42, 52), (46, 34, 70), (84, 40, 58), (128, 30, 78),
                        (162, 44, 62), (210, 36, 84), (250, 38, 56), (292, 28, 66)]:
        d.rectangle([x + bx, base - bh, x + bx + bw_, base], fill=(8, 12, 24))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(bx + 6, bx + bw_ - 6, 10):
                if (wx * 7 + wy * 3) % 11 < 4:
                    d.rectangle([x + wx, wy, x + wx + 3, wy + 4],
                                fill=(255, 200, 90))
    # explosion bursts
    for ex, ey, r in [(100, 62, 16), (235, 52, 19), (180, 78, 12)]:
        d.ellipse([x + ex - r, y + ey - r, x + ex + r, y + ey + r],
                  fill=(255, 120, 30))
        d.ellipse([x + ex - r // 2, y + ey - r // 2, x + ex + r // 2,
                   y + ey + r // 2], fill=(255, 220, 120))
    # bridge arc, damaged
    d.arc([x + 200, base - 26, x + 300, base + 6], 180, 360, fill=(120, 130, 150),
          width=3)


def illo_akvan(d, x, y, w, h):
    """Cyclone spiral over a stormy coast, rain bands and bending palm."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 110, 107))
    # spiral arms
    cx, cy = x + w * 0.42, y + h * 0.46
    for k in range(3):
        pts = []
        for a in range(0, 540, 12):
            import math
            r = 4 + a * 0.085
            ang = math.radians(a + k * 120)
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.85))
        d.line(pts, fill=(255, 255, 255), width=5)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 240, 200))
    # rain streaks
    for rx in range(10, w, 26):
        d.line([(x + rx, y + 8), (x + rx - 6, y + 30)], fill=(200, 235, 235),
               width=2)
    # sea + waves at the bottom
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(8, 70, 90))
    for wx in range(0, w, 34):
        d.arc([x + wx, y + h - 24, x + wx + 30, y + h - 8], 200, 340,
              fill=(255, 255, 255), width=2)
    # bending palm on the right
    d.line([(x + w - 26, y + h - 24), (x + w - 40, y + h - 66)],
           fill=(90, 60, 30), width=4)
    for dx, dy in [(-16, -8), (-4, -14), (10, -12), (18, -4)]:
        d.line([(x + w - 40, y + h - 66), (x + w - 40 + dx, y + h - 66 + dy)],
               fill=(46, 140, 70), width=3)
    # coastline houses
    for hx in (8, 34, 60):
        d.polygon([(x + hx, y + h - 26), (x + hx + 9, y + h - 38),
                   (x + hx + 18, y + h - 26)], fill=(200, 60, 40))
        d.rectangle([x + hx, y + h - 26, x + hx + 18, y + h - 14],
                    fill=(240, 220, 180))


def illo_cop31(d, x, y, w, h):
    """COP31 hall: flags, a globe, and a clock running to midnight."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 217, 176))
    # hall back wall + stage
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(120, 84, 50))
    d.rectangle([x + 20, y + h - 52, x + w - 20, y + h - 34], fill=(90, 60, 36))
    # row of flags
    cols = [(200, 40, 40), (30, 120, 60), (220, 180, 40), (40, 90, 160),
            (240, 200, 60), (180, 30, 30)]
    for i, c in enumerate(cols):
        fx = x + 24 + i * 48
        d.line([(fx, y + 12), (fx, y + 52)], fill=(80, 70, 60), width=2)
        d.polygon([(fx, y + 12), (fx + 26, y + 18), (fx, y + 26)], fill=c)
    # globe centre
    gx, gy, gr = x + w // 2, y + h // 2 + 6, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(46, 130, 90))
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=(255, 255, 255),
              width=2)
    for lat in (-18, 0, 18):
        d.arc([gx - gr, gy + lat - 8, gx + gr, gy + lat + 8], 0, 360,
              fill=(255, 255, 255), width=1)
    d.ellipse([gx - 6, gy - 26, gx + 6, gy + 26], outline=(255, 255, 255),
              width=1)
    # clock, midnight approaching
    ccx, ccy, cr = x + w - 46, y + 34, 20
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(255, 255, 255),
              outline=INK, width=2)
    d.line([(ccx, ccy), (ccx, ccy - cr + 5)], fill=INK, width=2)
    d.line([(ccx, ccy), (ccx + 9, ccy + 6)], fill=INK, width=2)
    d.text((ccx - 22, ccy + cr + 3), "MIDNIGHT", font=F(SANS_B, 7), fill=RED)
    # audience dots
    for ax in range(30, w - 20, 26):
        d.ellipse([x + ax, y + h - 30, x + ax + 10, y + h - 20],
                  fill=(60, 50, 40))


# ------------------------------------------------------------------- leads
LEADS = [
    dict(n=1, kick="WAR IN EUROPE",
         head="Kyiv hit overnight: 13 ballistic missiles, one Oreshnik",
         deck="242 drones and 22 cruise missiles; 4 killed, Qatar embassy "
              "damaged, 20 homes hit, 3 bridges damaged.",
         pill="REPORTED", illo=illo_kyiv),
    dict(n=2, kick="WEATHER · INDIA",
         head="Cyclone Akvan makes landfall as 300,000 flee",
         deck="Winds 70-80 km/h gusting 90 at Gopalpur; 423 rescue teams, "
              "9,341 shelters; no major damage yet.",
         pill="REPORTED", illo=illo_akvan),
    dict(n=3, kick="CLIMATE · ANTALYA",
         head="COP31's last day: draft drops every fossil-fuel mention",
         deck="Adaptation finance tripled but with no number; final text due "
              "at midnight, likely to run over.",
         pill="REPORTED", illo=illo_cop31),
]


def lead_cards(d):
    y, h = 156, 232
    bw = (CW - 2 * 12) // 3
    for i, s in enumerate(LEADS):
        x = M + i * (bw + 12)
        d.rounded_rectangle([x, y, x + bw, y + h], radius=5, fill=CARD,
                            outline=CARD_LINE, width=1)
        d.rectangle([x, y, x + bw, y + 3], fill=RED)
        s["illo"](d, x + 1, y + 4, int(bw) - 2, 118)
        tx = x + 12
        numdot(d, tx + 9, y + 138, s["n"], r=9)
        d.text((tx + 24, y + 131), s["kick"], font=F(SANS_B, 8), fill=RED)
        block(d, tx, y + 148, s["head"], F(SERIF, 15), INK, bw - 24, 18,
              max_lines=2)
        block(d, tx, y + 186, s["deck"], F(SANS, 9), (60, 56, 48), bw - 24,
              12, max_lines=3)
        pill(d, tx, y + h - 18, s["pill"], s["pill"])


# ------------------------------------------------- small-story illustrations
def illo_selloff(d, x, y, w, h):
    """Red market chart plunging across a grid, with a falling chip."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 244, 232))
    for gx in range(0, w, 24):
        d.line([(x + gx, y), (x + gx, y + h)], fill=(230, 220, 200), width=1)
    for gy in range(0, h, 14):
        d.line([(x, y + gy), (x + w, y + gy)], fill=(230, 220, 200), width=1)
    pts = [(x + 6, y + 12), (x + 40, y + 18), (x + 70, y + 14),
           (x + 100, y + 30), (x + 130, y + 28), (x + 160, y + 48),
           (x + w - 6, y + h - 8)]
    d.line(pts, fill=(200, 30, 35), width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 12, pts[-1][1] - 2),
               (pts[-1][0] - 2, pts[-1][1] - 12)], fill=(200, 30, 35))
    d.text((x + 8, y + 4), "NIKKEI -4.1%", font=F(SANS_B, 8), fill=(200, 30, 35))
    d.rectangle([x + w - 34, y + 6, x + w - 12, y + 22], fill=(20, 40, 70))
    d.text((x + w - 32, y + 9), "AI", font=F(SANS_B, 8), fill=(255, 255, 255))


def illo_anthropic(d, x, y, w, h):
    """Green opening chart over a dark exchange floor."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 40))
    pts = [(x + 6, y + h - 14), (x + 40, y + h - 26), (x + 70, y + h - 20),
           (x + 100, y + h - 34), (x + 130, y + h - 30), (x + 160, y + 16),
           (x + w - 6, y + 10)]
    d.line(pts, fill=(80, 200, 120), width=3)
    d.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 12, pts[-1][1] + 2),
               (pts[-1][0] - 2, pts[-1][1] + 12)], fill=(80, 200, 120))
    d.text((x + 8, y + 4), "ANT  $97.17  +17%", font=F(SANS_B, 8),
           fill=(120, 220, 150))
    for bx in range(0, 5):
        bh = 8 + bx * 4
        d.rectangle([x + 14 + bx * 30, y + h - 4 - bh, x + 30 + bx * 30,
                     y + h - 4], fill=(60, 90, 130))


def illo_gta(d, x, y, w, h):
    """Vice City dusk: gradient sky, palms, neon sign, skyline."""
    for i in range(h):
        t = i / h
        r = int(70 + (255 - 70) * t)
        g = int(40 + (140 - 40) * t)
        b = int(110 + (60 - 110) * t)
        d.line([(x, y + i), (x + w, y + i)], fill=(r, g, b))
    d.ellipse([x + w - 46, y + 8, x + w - 14, y + 40], fill=(255, 220, 130))
    for bx, bw_, bh in [(0, 30, 22), (34, 22, 34), (60, 28, 26), (92, 24, 40),
                        (120, 30, 28), (154, 26, 36)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw_, y + h], fill=(30, 16, 50))
        for wy in range(y + h - bh + 5, y + h - 4, 8):
            d.rectangle([x + bx + 5, wy, x + bx + 8, wy + 3],
                        fill=(255, 200, 90))
    d.rectangle([x + 8, y + 6, x + 92, y + 22], fill=(20, 10, 40))
    d.text((x + 12, y + 9), "VICE CITY", font=F(SANS_B, 9), fill=(255, 80, 200))
    for px, ph in [(150, 26), (168, 20)]:
        d.line([(x + px, y + h), (x + px, y + h - ph)], fill=(20, 60, 30),
               width=3)
        for dx, dy in [(-10, -4), (0, -8), (10, -4)]:
            d.line([(x + px, y + h - ph), (x + px + dx, y + h - ph + dy)],
                   fill=(20, 90, 40), width=2)


def illo_bepi(d, x, y, w, h):
    """Mercury's cratered face, a gold spacecraft, and the Sun."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 8, 16))
    for sx, sy in [(14, 10), (60, 6), (120, 12), (160, 8), (30, 30), (100, 26)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    d.ellipse([x + w - 30, y + 4, x + w - 6, y + 28], fill=(255, 200, 60))
    # Mercury
    mx, my, mr = x + 52, y + h // 2 + 6, 24
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(170, 160, 145))
    for cx_, cy_, cr in [(mx - 8, my - 6, 5), (mx + 10, my + 4, 4),
                         (mx - 2, my + 12, 3), (mx + 12, my - 12, 3)]:
        d.ellipse([cx_ - cr, cy_ - cr, cx_ + cr, cy_ + cr],
                  fill=(130, 120, 105))
    # spacecraft with two solar wings
    sx, sy = x + 128, y + 22
    d.rectangle([sx - 8, sy, sx + 30, sy + 14], fill=(60, 90, 160))
    d.rectangle([sx - 26, sy + 3, sx - 8, sy + 11], fill=(200, 160, 40))
    d.rectangle([sx + 30, sy + 3, sx + 48, sy + 11], fill=(200, 160, 40))
    d.line([(sx + 4, sy + 14), (sx - 2, sy + 26)], fill=(255, 255, 255), width=2)
    d.line([(sx + 18, sy + 14), (sx + 24, sy + 26)], fill=(255, 255, 255),
           width=2)
    d.text((x + 96, y + h - 14), "8 YEARS · 6BN MILES", font=F(SANS_B, 7),
           fill=(255, 255, 255))


def illo_phillips(d, x, y, w, h):
    """Cricket: green outfield, batsman mid-drive, red ball, stumps."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 50))
    d.ellipse([x + 10, y + h - 22, x + w - 10, y + h - 6], fill=(120, 170, 80))
    # pitch strip
    d.rectangle([x + w // 2 - 16, y + 8, x + w // 2 + 16, y + h - 8],
                fill=(210, 180, 130))
    # stumps
    for sx in range(3):
        d.line([(x + w // 2 - 6 + sx * 6, y + h - 30),
                (x + w // 2 - 6 + sx * 6, y + h - 16)], fill=(240, 220, 160),
               width=2)
    # batsman
    bx, by = x + w // 2 - 34, y + h - 34
    d.ellipse([bx - 5, by - 22, bx + 5, by - 12], fill=(240, 230, 200))
    d.line([(bx, by - 12), (bx, by + 2)], fill=(240, 230, 200), width=4)
    d.line([(bx, by + 2), (bx - 8, by + 12)], fill=(240, 230, 200), width=3)
    d.line([(bx, by + 2), (bx + 8, by + 12)], fill=(240, 230, 200), width=3)
    d.line([(bx, by - 8), (bx + 16, by - 2)], fill=(240, 230, 200), width=3)
    # bat
    d.line([(bx + 16, by - 2), (bx + 30, by + 10)], fill=(200, 160, 100),
           width=4)
    # red ball flying
    d.ellipse([x + w - 30, y + 12, x + w - 20, y + 22], fill=(200, 30, 35))
    d.text((x + 8, y + 2), "118", font=F(SERIF, 16), fill=(255, 255, 255))
    d.text((x + 8, y + 22), "off 216 balls", font=F(SANS_B, 7),
           fill=(255, 255, 255))


def illo_italy(d, x, y, w, h):
    """Rome: Colosseum silhouette, picket signs, a stopped bus."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 214, 170))
    # Colosseum
    d.ellipse([x + 8, y + h - 30, x + 92, y + h - 6], fill=(190, 120, 60))
    d.rectangle([x + 12, y + h - 44, x + 88, y + h - 26], fill=(190, 120, 60))
    for ax in range(18, 86, 12):
        d.arc([x + ax, y + h - 42, x + ax + 8, y + h - 30], 0, 180,
              fill=(240, 214, 170), width=2)
    # picket signs
    for px, lab in [(112, "SCIOPERO"), (148, "24H")]:
        d.line([(x + px, y + 16), (x + px, y + h - 10)], fill=(90, 60, 40),
               width=2)
        d.rectangle([x + px - 14, y + 6, x + px + 16, y + 20], fill=(255, 255, 255),
                    outline=RED, width=2)
        d.text((x + px - 12, y + 10), lab, font=F(SANS_B, 6), fill=RED)
    # stopped bus
    d.rounded_rectangle([x + 108, y + h - 26, x + w - 8, y + h - 6], radius=4,
                        fill=(200, 60, 40))
    for wx in range(114, w - 14, 14):
        d.rectangle([x + wx, y + h - 22, x + wx + 9, y + h - 14],
                    fill=(180, 220, 240))
    d.ellipse([x + 118, y + h - 8, x + 126, y + h], fill=(30, 30, 30))
    d.ellipse([x + w - 22, y + h - 8, x + w - 14, y + h], fill=(30, 30, 30))


def illo_senegal(d, x, y, w, h):
    """Atlantic swell, a wooden pirogue, an orange life ring."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 96, 143))
    for wy in (14, 30):
        for wx in range(0, w, 30):
            d.arc([x + wx, y + wy, x + wx + 26, y + wy + 10], 200, 340,
                  fill=(255, 255, 255), width=2)
    # pirogue hull
    d.polygon([(x + 30, y + h - 26), (x + 150, y + h - 26),
               (x + 140, y + h - 12), (x + 40, y + h - 12)], fill=(120, 80, 40))
    d.polygon([(x + 30, y + h - 26), (x + 150, y + h - 26),
               (x + 140, y + h - 20), (x + 40, y + h - 20)], fill=(150, 100, 50))
    # figures aboard
    for fx in (60, 84, 108):
        d.ellipse([x + fx, y + h - 38, x + fx + 6, y + h - 32], fill=(60, 40, 25))
        d.rectangle([x + fx - 1, y + h - 32, x + fx + 7, y + h - 24],
                    fill=(220, 180, 120))
    # life ring
    rx, ry, rr = x + w - 24, y + 16, 10
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(255, 120, 30))
    d.ellipse([rx - 5, ry - 5, rx + 5, ry + 5], fill=(20, 96, 143))
    d.text((x + 8, y + 4), "YENNE, SENEGAL", font=F(SANS_B, 7),
           fill=(255, 255, 255))


def illo_pill(d, x, y, w, h):
    """Clinic white: a big capsule, a DNA helix, and a 60.7% gauge."""
    d.rectangle([x, y, x + w, y + h], fill=(245, 250, 250))
    # DNA helix on the left
    for i in range(9):
        yy = y + 6 + i * 5
        xx1 = x + 16 + (6 if i % 2 == 0 else -6)
        xx2 = x + 40 - (6 if i % 2 == 0 else -6)
        d.ellipse([xx1 - 2, yy - 2, xx1 + 2, yy + 2], fill=(30, 140, 140))
        d.ellipse([xx2 - 2, yy - 2, xx2 + 2, yy + 2], fill=(220, 80, 60))
        d.line([(xx1, yy), (xx2, yy)], fill=(180, 200, 200), width=1)
    # capsule
    cx, cy = x + 118, y + 26
    d.rounded_rectangle([cx - 42, cy - 11, cx + 42, cy + 11], radius=11,
                        fill=(30, 140, 140))
    d.rounded_rectangle([cx, cy - 11, cx + 42, cy + 11], radius=11,
                        fill=(255, 255, 255), outline=(30, 140, 140), width=2)
    d.line([(cx - 42, cy - 11), (cx - 42, cy + 11)], fill=(30, 140, 140), width=2)
    # gauge arc (kept inside the illustration box)
    d.arc([x + w - 40, y + h - 24, x + w - 8, y + h - 6], 180, 360,
          fill=(200, 210, 210), width=4)
    d.arc([x + w - 40, y + h - 24, x + w - 8, y + h - 6], 180, 290,
          fill=(30, 140, 140), width=4)
    d.text((x + 96, y + h - 14), "60.7%", font=F(SANS_B, 9), fill=(30, 140, 140))


def illo_china(d, x, y, w, h):
    """Bank of China red: columns, a yuan coin, and the held rates."""
    d.rectangle([x, y, x + w, y + h], fill=(180, 20, 30))
    # bank pediment + columns (stop short so the rates line sits on red)
    d.polygon([(x + 10, y + 12), (x + w // 2, y + 2), (x + w - 10, y + 12)],
              fill=(240, 200, 90))
    for cx_ in range(22, w - 16, 24):
        d.rectangle([x + cx_, y + 14, x + cx_ + 8, y + h - 28],
                    fill=(245, 235, 210))
    d.rectangle([x + 10, y + h - 28, x + w - 10, y + h - 22],
                fill=(245, 235, 210))
    # yuan coin
    d.ellipse([x + w - 44, y + 8, x + w - 16, y + 36], fill=(240, 200, 90),
              outline=(255, 255, 255), width=2)
    d.text((x + w - 37, y + 12), "¥", font=F(SANS_B, 14), fill=(180, 20, 30))
    d.text((x + 12, y + h - 18), "3.00%  ·  3.50%", font=F(SANS_B, 9),
           fill=(255, 255, 255))


def illo_bukele(d, x, y, w, h):
    """Ballot box in El Salvador blue and white, with a voting date."""
    d.rectangle([x, y, x + w, y + h], fill=(245, 245, 240))
    # flag stripes
    d.rectangle([x, y, x + w, y + 10], fill=(0, 80, 160))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(0, 80, 160))
    # ballot box (upper half only, so the date line below stays clear)
    bx, by = x + w // 2 - 34, y + 14
    d.rectangle([bx, by, bx + 68, by + 22], fill=(0, 80, 160))
    d.rectangle([bx - 6, by - 5, bx + 74, by + 2], fill=(0, 60, 130))
    d.rectangle([bx + 28, by - 1, bx + 40, by + 2], fill=(255, 255, 255))
    # ballot paper going in
    d.polygon([(bx + 30, by - 12), (bx + 46, by - 12), (bx + 42, by - 1),
               (bx + 34, by - 1)], fill=(255, 255, 255), outline=INK, width=1)
    # date line in white on the bottom stripe, tick at the right
    d.text((x + 8, y + h - 11), "VOTE 28 FEB 2027", font=F(SANS_B, 7),
           fill=(255, 255, 255))
    d.line([(x + w - 24, y + h - 8), (x + w - 19, y + h - 3),
            (x + w - 9, y + h - 11)], fill=(255, 255, 255), width=2)


# -------------------------------------------------------------- small stories
SMALLS = [
    dict(n=4, kick="MARKETS · ASIA",
         head="Asia's AI sell-off: Nikkei -4.1%, Kospi -4.7%",
         deck="Taiex -6.75%; SoftBank -15%; MSCI Asia -7% on the week.",
         pill="REPORTED", illo=illo_selloff),
    dict(n=5, kick="WALL STREET",
         head="Anthropic's first close: $97.17, up 17%",
         deck="Opened at $111.50; valued near $1.27tn.",
         pill="REPORTED", illo=illo_anthropic),
    dict(n=6, kick="GAMING",
         head="GTA VI: $2.36bn day one, says estimate",
         deck="24.58m copies; Metacritic 99. Take-Two silent.",
         pill="CLAIM", illo=illo_gta),
    dict(n=7, kick="SPACE",
         head="BepiColombo reaches Mercury after 8 years",
         deck="6bn miles flown; orbit capture on Saturday.",
         pill="REPORTED", illo=illo_bepi),
    dict(n=8, kick="CRICKET · WELLINGTON",
         head="Phillips 118 makes history vs India",
         deck="Centuries in all 3 formats in one year.",
         pill="REPORTED", illo=illo_phillips),
    dict(n=9, kick="EUROPE · ITALY",
         head="Italy stops for 24 hours in CGIL strike",
         deck="~100 rallies against Meloni's 2027 budget.",
         pill="REPORTED", illo=illo_italy),
    dict(n=10, kick="AFRICA",
         head="Boat sinks off Senegal; 4 dead, dozens missing",
         deck="50-100 aboard the pirogue near Yenne.",
         pill="REPORTED", illo=illo_senegal),
    dict(n=11, kick="HEALTH",
         head="Pancreatic pill: tumours shrink in 60.7%",
         deck="Small trial, no control group; presented in Barcelona.",
         pill="REPORTED", illo=illo_pill),
    dict(n=12, kick="ECONOMY · CHINA",
         head="China holds rates for an 18th month",
         deck="1-year 3.00%, 5-year 3.50%, unchanged.",
         pill="REPORTED", illo=illo_china),
    dict(n=13, kick="AMERICAS",
         head="Bukele files for a third term",
         deck="El Salvador votes 28 Feb 2027.",
         pill="REPORTED", illo=illo_bukele),
]


def small_cards(d):
    bw, bh = 187, 130
    step = 199
    for i, s in enumerate(SMALLS):
        row, col = divmod(i, 5)
        x = M + col * step
        y = 392 + row * (bh + 4)
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=4, fill=CARD,
                            outline=CARD_LINE, width=1)
        s["illo"](d, x + 1, y + 1, bw - 2, 58)
        tx = x + 8
        numdot(d, tx + 7, y + 68, s["n"], r=7)
        d.text((tx + 18, y + 62), s["kick"], font=F(SANS_B, 7), fill=RED)
        block(d, tx, y + 74, s["head"], F(SERIF, 10), INK, bw - 16, 12,
              max_lines=2)
        block(d, tx, y + 98, s["deck"], F(SANS, 8), (60, 56, 48), bw - 16, 10,
              max_lines=2)
        pill(d, tx, y + bh - 13, s["pill"], s["pill"], size=7)


# --------------------------------------------------------------------- map
# Coarse continent outlines (lon, lat), drawn from general geography.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73), (-100, 72),
     (-90, 74), (-82, 73), (-76, 70), (-68, 62), (-60, 55), (-55, 47),
     (-60, 44), (-68, 44), (-74, 39), (-76, 34), (-80, 27), (-84, 30),
     (-89, 29), (-91, 19), (-95, 16), (-100, 16), (-105, 20), (-110, 23),
     (-115, 29), (-120, 34), (-124, 42), (-124, 48), (-130, 55), (-140, 60),
     (-152, 58), (-160, 58), (-166, 60), (-168, 66)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-58, 6), (-52, 4), (-50, -2),
     (-44, -3), (-38, -6), (-35, -9), (-35, -15), (-38, -20), (-40, -28),
     (-46, -32), (-52, -33), (-58, -35), (-62, -39), (-66, -45), (-68, -50),
     (-70, -54), (-73, -50), (-73, -42), (-72, -35), (-71, -28), (-70, -19),
     (-76, -14), (-79, -8), (-81, -3), (-80, 2), (-79, 9)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50),
     (2, 51), (5, 53), (8, 55), (8, 57), (10, 59), (14, 58), (18, 56),
     (21, 55), (24, 58), (26, 60), (30, 62), (32, 66), (36, 68), (42, 68),
     (44, 66), (40, 62), (36, 60), (32, 58), (30, 55), (28, 51), (28, 46),
     (24, 45), (23, 40), (22, 38), (19, 42), (15, 44), (12, 44), (8, 44),
     (3, 42), (0, 39), (-2, 37), (-6, 36), (-10, 36)],
    # Africa
    [(-6, 35), (-9, 32), (-13, 28), (-16, 21), (-17, 15), (-16, 12),
     (-13, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (11, 0), (13, -3),
     (12, -8), (13, -12), (12, -17), (14, -22), (16, -28), (18, -33),
     (20, -35), (26, -34), (30, -30), (33, -26), (35, -22), (36, -18),
     (40, -15), (40, -10), (42, -5), (46, -1), (51, 2), (51, 11), (48, 11),
     (44, 12), (41, 14), (39, 18), (37, 22), (34, 28), (32, 31), (28, 31),
     (24, 33), (20, 33), (15, 33), (11, 34), (10, 37), (4, 37), (-1, 35),
     (-6, 35)],
    # Asia
    [(30, 36), (33, 36), (36, 36), (36, 40), (39, 42), (42, 44), (44, 42),
     (47, 40), (49, 38), (50, 34), (52, 30), (54, 27), (57, 27), (58, 25),
     (61, 25), (64, 25), (67, 24), (70, 23), (72, 20), (75, 16), (77, 8),
     (80, 8), (80, 13), (82, 17), (86, 20), (89, 22), (91, 22), (92, 17),
     (94, 17), (97, 15), (98, 10), (100, 7), (102, 4), (104, 1), (106, -3),
     (108, -6), (110, -7), (113, -8), (116, -9), (119, -10), (122, -11),
     (125, -9), (128, -6), (131, -3), (134, -1), (137, 0), (140, 3),
     (141, 8), (140, 13), (139, 18), (138, 24), (137, 30), (135, 34),
     (131, 34), (129, 36), (127, 38), (126, 40), (128, 42), (131, 43),
     (135, 44), (138, 46), (141, 50), (142, 54), (142, 58), (146, 59),
     (150, 59), (155, 59), (158, 56), (162, 58), (162, 62), (166, 64),
     (170, 66), (173, 64), (178, 65), (178, 62), (172, 60), (166, 60),
     (162, 58), (158, 52), (156, 51), (150, 46), (146, 44), (142, 42),
     (140, 39), (138, 36), (134, 35), (130, 33), (126, 33), (122, 31),
     (120, 28), (118, 25), (114, 22), (110, 20), (108, 18), (106, 16),
     (104, 12), (102, 10), (100, 8), (98, 8), (96, 10), (94, 14), (92, 16),
     (90, 18), (88, 21), (86, 20), (84, 19), (80, 15), (77, 10), (74, 12),
     (72, 18), (70, 22), (68, 23), (66, 25), (63, 25), (60, 25), (57, 26),
     (54, 27), (51, 29), (49, 30), (48, 30), (46, 31), (44, 30), (42, 29),
     (40, 29), (38, 30), (36, 32), (34, 33), (32, 34), (30, 36)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (116, -35), (120, -34), (124, -33),
     (128, -32), (132, -32), (135, -35), (138, -35), (140, -38), (144, -38),
     (148, -38), (150, -37), (153, -32), (153, -27), (151, -24), (149, -20),
     (146, -19), (143, -15), (142, -11), (139, -14), (136, -12), (132, -12),
     (129, -14), (126, -14), (123, -17), (120, -20), (117, -20), (113, -22)],
    # Greenland
    [(-46, 60), (-42, 63), (-38, 66), (-32, 68), (-28, 70), (-22, 70),
     (-20, 74), (-24, 77), (-30, 80), (-38, 80), (-46, 78), (-52, 76),
     (-56, 72), (-58, 68), (-56, 64), (-52, 61), (-46, 60)],
]

PINS = [  # (story number, lon, lat)
    (1, 30.5, 50.4), (2, 84.9, 19.3), (3, 30.7, 36.9), (4, 139.7, 35.7),
    (5, -122.4, 37.8), (6, -74.0, 40.7), (7, 8.7, 49.9), (8, 174.8, -41.3),
    (9, 12.5, 41.9), (10, -17.2, 14.7), (11, 2.2, 41.4), (12, 116.4, 39.9),
    (13, -89.2, 13.7),
]


def world_map(d):
    y0, y1 = 656, 768
    d.text((M, y0), "WHERE IT HAPPENED", font=F(SANS_B, 9), fill=RED)
    d.text((W - M - d.textlength("1-13: the stories above, numbered",
                                 font=F(SANS, 8)), y0 + 1),
           "1-13: the stories above, numbered", font=F(SANS, 8), fill=MUTED)
    mx, my, mw, mh = M, y0 + 14, CW, y1 - y0 - 14
    d.rounded_rectangle([mx, my, mx + mw, my + mh], radius=4, fill=(31, 47, 74),
                        outline=CARD_LINE, width=1)

    def px(lon):
        return mx + (lon + 180) / 360 * mw

    def py(lat):
        return my + (78 - lat) / 136 * mh

    for poly in CONTINENTS:
        pts = [(px(lon), py(lat)) for lon, lat in poly]
        d.polygon(pts, fill=(232, 216, 172), outline=(198, 178, 128))
    for n, lon, lat in PINS:
        numdot(d, px(lon), py(lat), n, r=9)


# ------------------------------------------------------- also on, timeline
BRIEFS = [
    "Kharkiv hospital hit by drone; 4 injured",
    "Japan core CPI 2.2%; Bank of Japan hike eyed",
    "Gold ~$3,600 an ounce, down 7% on the week",
    "Bitcoin slips below $62,000",
    "S&P 500 -2%+ and Nasdaq -2.2% on Thursday",
    "Hang Seng near bear market, -20% from peak",
    "COP31: Africa wants $120bn a year by 2035",
    "COP31: 92,000 attendees in Antalya",
    "Anthropic fully diluted value put near $1.8tn",
    "GTA VI: Take-Two gives no official figures",
    "BepiColombo orbiters split 9-10 Dec",
    "Phillips only 2nd after Rohit Sharma (2017)",
    "New Zealand 368 all out; Nicholls 175*",
    "Italy rail stoppage 21:00 Fri to 20:00 Sat",
    "UNHCR: ~600 died on Canary route in 2026",
    "Daraxonrasib: 12-month survival 76.6%",
    "Riyadh: Houthi missile damages PIF Tower",
    "China rates unchanged, 18th month running",
    "Akvan: 423 rescue teams, 9,341 shelters",
    "Akvan: no major damage or deaths so far",
    "Kyiv: three Dnipro bridges damaged",
    "Kyiv: strike hit as cold spell gripped Ukraine",
    "Italy: CGIL's 5th strike; ~100 rallies",
]


def also_on(d):
    y = 772
    d.text((M, y), "ALSO ON FRIDAY 20 NOVEMBER", font=F(SANS_B, 10), fill=INK)
    d.line([(M + 220, y + 6), (W - M, y + 6)], fill=RULE, width=1)
    f = F(SANS, 8)
    cols = [BRIEFS[i:i + 8] for i in range(0, len(BRIEFS), 8)]
    for ci, col in enumerate(cols):
        x = M + ci * 328
        for ri, item in enumerate(col):
            yy = y + 16 + ri * 9
            d.text((x, yy), "·", font=f, fill=RED)
            d.text((x + 8, yy), fit_line(d, item, f, 312), font=f, fill=INK)


def timeline(d):
    y = 866
    d.text((M, y), "THE DAY BY HOURS (UTC)", font=F(SANS_B, 9), fill=RED)
    entries = ("21:00 Thu  Anthropic closes +17%   ·   23:25 Thu  explosions "
               "over Kyiv   ·   01:00  China holds rates   ·   02:00  Akvan "
               "landfall   ·   07:30  Rome buses stop   ·   21:00  COP31 text due")
    d.text((M, y + 13), fit_line(d, entries, F(SANS, 8), CW), font=F(SANS, 8),
           fill=INK)
    d.line([(M, y + 26), (W - M, y + 26)], fill=RULE, width=1)


def verdict_row(d):
    y, h = 896, 48
    boxes = [
        ("THE VERDICT",
         "COP31's final draft drops every fossil-fuel mention. Any deal "
         "comes after midnight."),
        ("HOW SURE ARE WE?",
         "13 of 13 main stories sourced. Two figures are estimates or early "
         "trials, labelled CLAIM on the page."),
        ("MARKETS & MONEY",
         "Nikkei -4.1%, Kospi -4.7%, Taiex -6.75%, SoftBank -15%, gold ~$3,600, "
         "Bitcoin under $62,000."),
    ]
    bw = (CW - 2 * 12) // 3
    for i, (head, body) in enumerate(boxes):
        x = M + i * (bw + 12)
        d.rounded_rectangle([x, y, x + bw, y + h], radius=4, fill=CARD,
                            outline=CARD_LINE, width=1)
        d.text((x + 10, y + 5), head, font=F(SANS_B, 8), fill=RED)
        block(d, x + 10, y + 18, body, F(SANS, 8), INK, bw - 20, 10,
              max_lines=3)


def footer(d):
    y = 952
    d.text((M, y), "DATE CHECK — first reported Thursday 19 Nov, not 20 Nov news:",
           font=F(SANS_B, 8), fill=RED)
    dc = ("Shenzhen summit + Declaration · Anthropic $83 IPO pricing + Nasdaq "
          "debut · ICJ Myanmar verdict · GTA VI midnight launch · Van Gogh "
          "$190.4m sale · Voyager 1 · Senate 48-51 Iran vote · Korea Suneung · "
          "Crimean Bridge strike · Houthi strike on Riyadh · COP31 second draft · "
          "Dutch/Austrian/Swedish embassy damage in Kyiv")
    block(d, M, y + 11, dc, F(SANS, 7), MUTED, CW, 9, max_lines=3)
    y2 = y + 40
    d.line([(M, y2), (W - M, y2)], fill=RULE, width=1)
    src = ("Sources: Reuters · AP · AFP · BBC · Al Jazeera · IMD · ESA/JAXA · "
           "PBOC · ANSA · Kyiv Independent · Revolution Medicines · Sensor "
           "Tower.  *GTA VI figure is a Sensor Tower estimate.  Original "
           "drawings.  All figures checked 20 Nov 2026.")
    block(d, M, y2 + 5, src, F(SANS, 7), MUTED, CW, 9, max_lines=2)


# -------------------------------------------------------------------- main
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    stat_strip(d)
    lead_cards(d)
    small_cards(d)
    world_map(d)
    also_on(d)
    timeline(d)
    verdict_row(d)
    footer(d)
    return img


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = render()
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    print(f"{out}: {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
