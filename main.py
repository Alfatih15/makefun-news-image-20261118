# SPDX-License-Identifier: MIT
"""Draw a newspaper front page summing up the world news of
Wednesday 18 November 2026, and write it as /output/entry.png.

Pure Python 3.13 standard library only: no network, no fonts, no PIL.
Every pixel is drawn in code -- a small 5x7 bitmap font defined below,
simple vector pictograms, and a hand-rolled PNG encoder (zlib + struct).
The output is byte-identical across runs.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (18, 22, 36)
NAVY = (16, 42, 86)
RED = (178, 34, 34)
BLUE = (31, 90, 160)
TEAL = (14, 118, 108)
AMBER = (196, 128, 18)
GREY = (96, 96, 92)
WHITE = (255, 255, 255)
SKY = (186, 214, 235)
LIGHT = (232, 236, 242)


# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells, '#' = ink, '.' = empty.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "\u2022": ("00000", "00100", "01110", "01110", "01110", "00100", "00000"),
}


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (6 units per char)."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color, thick=2):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = thick // 2
        while True:
            self.fill_rect(x0 - r, y0 - r, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=3):
        self.fill_circle(cx, cy, r, color)
        self.fill_circle(cx, cy, r - thick, PAPER)

    def arc(self, cx, cy, r, a0, a1, color, thick=3):
        steps = max(8, int(abs(a1 - a0) * r / 2.5))
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            self.fill_rect(x - thick // 2, y - thick // 2, thick, thick, color)

    def fill_triangle(self, p0, p1, p2, color):
        xs = sorted([p0, p1, p2], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = xs
        if y2 == y0:
            return
        for y in range(y0, y2 + 1):
            xa = x0 + (x2 - x0) * (y - y0) / (y2 - y0)
            if y < y1:
                xb = x0 if y1 == y0 else x0 + (x1 - x0) * (y - y0) / (y1 - y0)
            else:
                xb = x1 if y2 == y1 else x1 + (x2 - x1) * (y - y1) / (y2 - y1)
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.fill_rect(int(lo), y, int(hi) - int(lo) + 1, 1, color)

    def text(self, x, y, s, scale, color, align="left"):
        if align == "center":
            x -= text_width(s, scale) // 2
        elif align == "right":
            x -= text_width(s, scale)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
            cx += 6 * scale
        return cx


# ---------------------------------------------------------- pictograms
def pic_globe(c, cx, cy, r):
    """A globe: blue disc, meridians, three summit dots."""
    c.fill_circle(cx, cy, r, SKY)
    c.ring(cx, cy, r, NAVY, 4)
    c.arc(cx, cy, r - 2, math.pi * 0.15, math.pi * 0.85, NAVY, 3)
    c.arc(cx, cy, r - 2, math.pi * 1.15, math.pi * 1.85, NAVY, 3)
    c.line(cx - r + 2, cy, cx + r - 2, cy, NAVY, 3)
    c.line(cx, cy - r + 2, cx, cy + r - 2, NAVY, 3)
    for dx, dy, col in ((-r // 2, -r // 3, RED), (r // 3, -r // 2, BLUE),
                        (r // 2, r // 3, AMBER)):
        c.fill_circle(cx + dx, cy + dy, 7, col)
        c.arc(cx + dx, cy + dy, 7, 0, 2 * math.pi, INK, 2)


def pic_plane(c, cx, cy, s):
    """Paper plane with motion lines (travel / summit arrival)."""
    c.fill_triangle((cx - 34 * s // 10, cy), (cx + 36 * s // 10, cy - 14 * s // 10),
                    (cx + 10 * s // 10, cy + 6 * s // 10), BLUE)
    c.fill_triangle((cx - 34 * s // 10, cy), (cx + 10 * s // 10, cy + 6 * s // 10),
                    (cx + 2 * s // 10, cy + 18 * s // 10), NAVY)
    for i, yy in enumerate((-26, -14, -2)):
        c.line(cx - 58, cy + yy + i * 4, cx - 40, cy + yy + i * 4, GREY, 2)


def pic_bridge(c, cx, cy, w):
    """A suspension bridge: deck, arc, towers, suspenders."""
    deck_y = cy + 22
    c.line(cx - w // 2, deck_y, cx + w // 2, deck_y, INK, 5)
    c.arc(cx, deck_y + 4, w // 2 - 6, math.pi, 2 * math.pi, RED, 4)
    for tx in (-w // 2 + 8, w // 2 - 8):
        c.line(cx + tx, cy - 34, cx + tx, deck_y, INK, 5)
    for sx in range(-w // 2 + 22, w // 2 - 18, 16):
        top = deck_y - int(math.sqrt(max(0, (w // 2 - 6) ** 2 - sx * sx))) + 4
        c.line(cx + sx, top, cx + sx, deck_y, GREY, 2)
    c.fill_circle(cx, cy - 44, 9, AMBER)


def pic_drone(c, cx, cy, s):
    """A quadcopter drone: body, four arms, four rotors."""
    c.fill_circle(cx, cy, 12, INK)
    c.fill_circle(cx, cy, 5, RED)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ax, ay = cx + dx * 26, cy + dy * 26
        c.line(cx, cy, ax, ay, INK, 4)
        c.fill_circle(ax, ay, 6, INK)
        c.line(ax - 14, ay, ax + 14, ay, GREY, 3)
    c.line(cx - 34, cy + 34, cx - 22, cy + 44, AMBER, 3)
    c.line(cx + 34, cy + 34, cx + 22, cy + 44, AMBER, 3)


def pic_missile(c, cx, cy):
    """A missile climbing, with flame and motion lines."""
    c.fill_triangle((cx, cy - 52), (cx - 11, cy - 22), (cx + 11, cy - 22), INK)
    c.fill_rect(cx - 11, cy - 22, 22, 44, INK)
    c.fill_triangle((cx - 11, cy + 8), (cx - 24, cy + 26), (cx - 11, cy + 22), INK)
    c.fill_triangle((cx + 11, cy + 8), (cx + 24, cy + 26), (cx + 11, cy + 22), INK)
    c.fill_triangle((cx, cy + 52), (cx - 8, cy + 24), (cx + 8, cy + 24), AMBER)
    c.fill_triangle((cx, cy + 42), (cx - 4, cy + 24), (cx + 4, cy + 24), RED)
    for i, xx in enumerate((-38, -46, -30)):
        c.line(cx + xx, cy + 30 + i * 12, cx + xx, cy + 52 + i * 12, GREY, 2)


def pic_scales(c, cx, cy):
    """Scales of justice: pole, beam, two pans (sanctions)."""
    c.line(cx, cy - 44, cx, cy + 40, INK, 5)
    c.line(cx - 40, cy - 34, cx + 40, cy - 34, INK, 5)
    c.fill_circle(cx, cy - 48, 6, INK)
    for dx in (-40, 40):
        c.line(cx + dx, cy - 34, cx + dx - 14, cy - 6, INK, 3)
        c.line(cx + dx, cy - 34, cx + dx + 14, cy - 6, INK, 3)
        c.arc(cx + dx, cy - 6, 14, 0, math.pi, INK, 4)
        c.line(cx + dx - 14, cy - 6, cx + dx + 14, cy - 6, INK, 3)


def pic_cyclone(c, cx, cy):
    """A cyclone spiral: three arcs curling inward."""
    c.arc(cx, cy, 40, 0.3, 4.4, TEAL, 5)
    c.arc(cx, cy, 27, 2.2, 6.0, TEAL, 5)
    c.arc(cx, cy, 14, 4.2, 8.0, TEAL, 5)
    c.fill_circle(cx, cy, 5, TEAL)
    c.line(cx - 52, cy + 44, cx - 40, cy + 44, GREY, 2)
    c.line(cx + 40, cy + 44, cx + 52, cy + 44, GREY, 2)


# -------------------------------------------------------------- layout
M = 28  # page margin


def panel(c, x, y, w, h, kicker, headline, color, pic, hscale=3):
    c.fill_rect(x, y, w, h, WHITE)
    c.rect(x, y, w, h, INK, 2)
    c.fill_rect(x, y, w, 4, color)
    px = x + 64
    py = y + h // 2 + 6
    if pic == "globe":
        pic_globe(c, px, py, 52)
    elif pic == "plane":
        pic_plane(c, px, py, 10)
    elif pic == "bridge":
        pic_bridge(c, px, py - 6, 96)
    elif pic == "drone":
        pic_drone(c, px, py, 10)
    elif pic == "missile":
        pic_missile(c, px, py)
    elif pic == "scales":
        pic_scales(c, px, py)
    elif pic == "cyclone":
        pic_cyclone(c, px, py)
    tx = x + 138
    tw = w - 138 - 16
    c.text(tx, y + 16, kicker, 2, color)
    lines = wrap_text(headline, tw, hscale)
    ly = y + 40
    for ln in lines:
        c.text(tx, ly, ln, hscale, INK)
        ly += 7 * hscale + 3
    return ly


def build():
    c = Canvas(W, H, PAPER)
    # Masthead.
    c.text(W // 2, 34, "THE WORLD TODAY", 8, INK, align="center")
    c.hline(M, 116, W - 2 * M, INK, 3)
    c.hline(M, 122, W - 2 * M, INK, 1)
    # Date banner.
    c.fill_rect(M, 134, W - 2 * M, 54, NAVY)
    c.text(W // 2, 152, "WEDNESDAY 18 NOVEMBER 2026", 4, WHITE, align="center")
    c.text(W // 2, 198, "THE DAY IN WORLD NEWS - SIX STORIES, FIVE CONTINENTS",
           2, GREY, align="center")
    # Lead story: APEC opens, trilateral summit set for Thursday.
    x, y, w, h = M, 228, W - 2 * M, 208
    c.fill_rect(x, y, w, h, WHITE)
    c.rect(x, y, w, h, INK, 2)
    c.fill_rect(x, y, w, 4, RED)
    pic_globe(c, x + 108, y + h // 2 + 8, 74)
    tx = x + 220
    c.text(tx, y + 18, "SHENZHEN - CHINA", 2, RED)
    c.text(tx, y + 44, "APEC SUMMIT OPENS", 4, INK)
    c.text(tx, y + 80, "IN SHENZHEN", 4, INK)
    c.text(tx, y + 122, "TRUMP - XI - PUTIN SUMMIT", 3, NAVY)
    c.text(tx, y + 150, "SET FOR THURSDAY 19 NOV", 3, NAVY)
    c.text(tx, y + 182, "LEADERS GATHER FOR THE ASIA-PACIFIC SUMMIT", 2, GREY)
    # Grid of four stories.
    gw, gh = 474, 186
    rows = [
        (M, 452, "MANILA - QUAD TALKS",
         "TRUMP LANDS IN MANILA FOR QUAD TALKS; CANADA AND CHINA EXTEND TRADE DEALS",
         BLUE, "plane"),
        (M + 494, 452, "UKRAINE - WAR",
         "KYIV STRIKES KERCH BRIDGE FOR A SECOND DAY; RUSSIA HITS BRIDGES IN KYIV",
         RED, "bridge"),
        (M, 652, "GULF - TENSIONS",
         "IRAN DRONES TARGET US RADAR IN BAHRAIN - INTERCEPTED; KUWAIT INTERCEPTS DRONES TOO",
         AMBER, "drone"),
        (M + 494, 652, "KOREA - MISSILE",
         "NORTH KOREA FIRES BALLISTIC MISSILE INTO THE SEA, SOUTH KOREA REPORTS",
         NAVY, "missile"),
    ]
    for px, py, kicker, headline, color, pic in rows:
        panel(c, px, py, gw, gh, kicker, headline, color, pic)
    # Bottom strip: two short items.
    by, bh = 852, 118
    panel(c, M, by, gw, bh, "MIDDLE EAST",
          "UK SANCTIONS 8 ISRAELI SETTLEMENT FIRMS; GAZA TRUCE NEAR COLLAPSE",
          TEAL, "scales", hscale=2)
    panel(c, M + 494, by, gw, bh, "WEATHER - SPORT",
          "CYCLONE AKVAN NEARS INDIA; DHONI RETIRES FROM THE IPL",
          TEAL, "cyclone", hscale=2)
    # Footer.
    c.text(W // 2, 992, "WEDNESDAY 18 NOVEMBER 2026 - ALL STORIES REPORTED TODAY",
           2, GREY, align="center")
    return c


# ----------------------------------------------------------- PNG encode
def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(c):
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[yy * c.w * 3:(yy + 1) * c.w * 3]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", ihdr)
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += png_chunk(b"IEND", b"")
    return png


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "./out")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = encode_png(build())
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
