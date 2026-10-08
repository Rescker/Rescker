#!/usr/bin/env python3
"""Generates assets/terminal.svg -- the profile README hero.

Deterministic by construction:

* The wordmark uses a hand-defined 5x7 bitmap font (the classic terminal/BIOS
  face) drawn as SVG rectangles. No font is loaded or guessed, so it renders
  pixel-identically everywhere -- unlike figlet art, whose Unicode quadrant
  glyphs fall back to whatever the viewer's font happens to provide.
* Body text carries textLength + lengthAdjust="spacingAndGlyphs" so columns
  hold even when the fallback face is not truly monospace.

The layout is three columns across (wordmark | identity | stack) with the
session output spanning the full width underneath. Aspect is deliberately
~2:1 so the README can render it at width="100%" and fill the column without
becoming absurdly tall.

GitHub strips <style>/<script> from README HTML, but an SVG referenced through
<img> keeps its declarative SMIL animation. No third-party host is involved,
so nothing here can rate-limit, 402, or vanish.

Run:  python assets/generate-terminal.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).with_name("terminal.svg")

# ---------------------------------------------------------------- palette ----
BG = "#0D1117"
SURFACE = "#161B22"
BORDER = "#30363D"
RULE = "#21262D"
TEXT = "#C9D1D9"
MUTED = "#8B949E"
ACCENT = "#39D353"
DOT_R, DOT_Y, DOT_G = "#FF5F56", "#FFBD2E", "#27C93F"

# ------------------------------------------------------------------- type ----
FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'Liberation Mono', monospace")
FS = 17.0            # body font-size
CW = 10.2            # advance per character (0.6em for a monospace face)
LH = 25.5            # body line height
TITLE_FS = 12.5

# ------------------------------------------------------------------ layout ----
PAD = 22.0
TITLE_H = 38.0
RADIUS = 10.0
GAP_AB = 34.0        # wordmark -> identity
GAP_BC = 40.0        # identity -> stack

# -------------------------------------------------- 5x7 bitmap wordmark ------
FONT_5X7 = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
}
WORDMARK = ["JOAQUIM", "MENDES"]

CELL_W = 6.6         # one bitmap pixel, horizontally
CELL_H = 8.7         # one bitmap pixel, vertically (bitmap faces are ~1:1.3)
LETTER_GAP = 1       # blank pixel columns between letters
LINE_GAP = 2         # blank pixel rows between the two words


def word_units(word: str) -> int:
    return len(word) * 5 + (len(word) - 1) * LETTER_GAP


ART_UNITS_W = max(word_units(w) for w in WORDMARK)
ART_UNITS_H = len(WORDMARK) * 7 + (len(WORDMARK) - 1) * LINE_GAP
ART_W = ART_UNITS_W * CELL_W
ART_H = ART_UNITS_H * CELL_H

# ------------------------------------------------------------------ content --
# (kind, text) -- "rule" draws a real line, avoiding box-drawing font drift.
IDENTITY = [
    ("accent", "rescker@github"),
    ("rule", ""),
    ("strong", "Joaquim Mendes"),
    ("muted", "full stack engineer"),
]

STACK = [
    ("accent", "~/stack"),
    ("rule", ""),
    ("text", "Java · Spring Boot"),
    ("text", "React / TypeScript"),
    ("text", "PostgreSQL · MySQL"),
    ("text", "Docker · MongoDB"),
]

PROMPT = "rescker@github:~$"
COMMAND = "cat /etc/motd"
MOTD = [
    "State? It ain't. Hit the road, dude.",
    "This ain't no state property. 🚜",
]

# --------------------------------------------------------------- geometry ----
def col_width(lines) -> float:
    return max(len(t) for k, t in lines if k != "rule") * CW


IDENT_W = col_width(IDENTITY)
STACK_W = col_width(STACK)
IDENT_X = PAD + ART_W + GAP_AB
STACK_X = IDENT_X + IDENT_W + GAP_BC

row1_h = max(ART_H, len(IDENTITY) * LH, len(STACK) * LH)
body_w = ART_W + GAP_AB + IDENT_W + GAP_BC + STACK_W

W = round(PAD * 2 + body_w)
ROW1_TOP = TITLE_H + PAD
rule_y = ROW1_TOP + row1_h + 20
CODE_TOP = rule_y + 26
CODE_LINES = 1 + len(MOTD) + 1                 # command + motd + trailing prompt
H = round(CODE_TOP + (CODE_LINES - 1) * LH + FS + PAD - 6)

o = []
add = o.append
add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="Terminal: Joaquim Mendes, full stack engineer. '
    f'Java, Spring Boot, React, TypeScript, PostgreSQL, MySQL, Docker, '
    f'MongoDB. State? It ain\'t. Hit the road, dude.">')
add('<title>rescker@github: ~</title>')

# --- window ------------------------------------------------------------------
add(f'<clipPath id="win"><rect x="0" y="0" width="{W}" height="{H}" '
    f'rx="{RADIUS}"/></clipPath>')
add('<g clip-path="url(#win)">')
add(f'<rect x="0" y="0" width="{W}" height="{TITLE_H}" fill="{SURFACE}"/>')
add(f'<rect x="0" y="{TITLE_H}" width="{W}" height="{H - TITLE_H}" fill="{BG}"/>')
add('</g>')
add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="{RADIUS}" '
    f'fill="none" stroke="{BORDER}"/>')

# --- title bar ---------------------------------------------------------------
cy = TITLE_H / 2
for i, color in enumerate((DOT_R, DOT_Y, DOT_G)):
    add(f'<circle cx="{PAD + i * 18}" cy="{cy}" r="5.5" fill="{color}"/>')
add(f'<text x="{W / 2:.1f}" y="{cy + 4:.1f}" fill="{MUTED}" font-family="{FONT}" '
    f'font-size="{TITLE_FS}" text-anchor="middle">rescker@github — zsh</text>')

# --- column A: wordmark as bitmap rects --------------------------------------
add(f'<g fill="{ACCENT}">')
for li, word in enumerate(WORDMARK):
    y0 = ROW1_TOP + li * (7 + LINE_GAP) * CELL_H
    x0 = PAD
    for ch in word:
        for ry, row in enumerate(FONT_5X7[ch]):
            for rx, bit in enumerate(row):
                if bit == "1":
                    add(f'<rect x="{x0 + rx * CELL_W:.2f}" '
                        f'y="{y0 + ry * CELL_H:.2f}" '
                        f'width="{CELL_W:.2f}" height="{CELL_H:.2f}"/>')
        x0 += (5 + LETTER_GAP) * CELL_W
add('</g>')

# --- columns B and C: text blocks --------------------------------------------
def text_col(lines, x: float, width: float) -> None:
    add(f'<g font-family="{FONT}" font-size="{FS}">')
    for i, (kind, text) in enumerate(lines):
        y = ROW1_TOP + i * LH + FS * 0.86
        if kind == "rule":
            add(f'<line x1="{x:.1f}" y1="{y - FS * 0.42:.1f}" '
                f'x2="{x + width * 0.72:.1f}" y2="{y - FS * 0.42:.1f}" '
                f'stroke="{BORDER}" stroke-width="1.5"/>')
            continue
        color = {"accent": ACCENT, "strong": TEXT, "muted": MUTED, "text": TEXT}[kind]
        weight = ' font-weight="600"' if kind in ("strong", "accent") else ""
        add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}"{weight} '
            f'textLength="{len(text) * CW:.1f}" '
            f'lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
    add('</g>')


text_col(IDENTITY, IDENT_X, IDENT_W)
text_col(STACK, STACK_X, STACK_W)

# --- divider -----------------------------------------------------------------
add(f'<line x1="{PAD}" y1="{rule_y:.1f}" x2="{W - PAD}" y2="{rule_y:.1f}" '
    f'stroke="{RULE}" stroke-width="1"/>')

# --- full-width session output ----------------------------------------------
y0 = CODE_TOP + FS * 0.86
# NOTE: the prompt carries no trailing space -- a trailing space is dropped when
# textLength compresses the run, which would jam the command against the '$'.
# The gap is instead one explicit character cell.
prompt_w = len(PROMPT) * CW
cmd_x = PAD + prompt_w + CW
cmd_w = len(COMMAND) * CW

add(f'<g font-family="{FONT}" font-size="{FS}">')
add(f'<text x="{PAD}" y="{y0:.1f}" fill="{ACCENT}" font-weight="600" '
    f'textLength="{prompt_w:.1f}" lengthAdjust="spacingAndGlyphs">'
    f'{escape(PROMPT)}</text>')
# typed command, revealed by a clip rect
add('<clipPath id="cmd" clipPathUnits="userSpaceOnUse">')
add(f'<rect x="{cmd_x:.1f}" y="{y0 - LH * 0.8:.1f}" width="0" height="{LH:.1f}">')
steps = ";".join(f"{i * CW:.1f}" for i in range(len(COMMAND) + 1))
add(f'<animate attributeName="width" calcMode="discrete" dur="0.72s" '
    f'begin="0.55s" fill="freeze" values="{steps}"/>')
add('</rect></clipPath>')
add(f'<text x="{cmd_x:.1f}" y="{y0:.1f}" fill="{TEXT}" clip-path="url(#cmd)" '
    f'textLength="{cmd_w:.1f}" lengthAdjust="spacingAndGlyphs">'
    f'{escape(COMMAND)}</text>')
# waiting cursor, hidden once typing starts
add(f'<rect x="{cmd_x:.1f}" y="{y0 - FS * 0.78:.1f}" width="{CW * 0.62:.1f}" '
    f'height="{FS * 0.95:.1f}" fill="{ACCENT}">')
add('<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
    'dur="1.06s" repeatCount="indefinite"/>')
add('<animate attributeName="opacity" values="1;0" begin="0.55s" dur="0.01s" '
    'fill="freeze"/>')
add('</rect>')
# motd output
for i, line in enumerate(MOTD):
    ly = y0 + (i + 1) * LH
    begin = 1.4 + i * 0.14
    add(f'<text x="{PAD}" y="{ly:.1f}" fill="{TEXT}" opacity="0" '
        f'textLength="{len(line) * CW:.1f}" lengthAdjust="spacingAndGlyphs">'
        f'{escape(line)}')
    add(f'<animate attributeName="opacity" values="0;1" begin="{begin:.2f}s" '
        f'dur="0.28s" fill="freeze"/>')
    add('</text>')
# trailing prompt + blinking cursor
py = y0 + CODE_LINES * LH - LH / 2
add('<g opacity="0"><animate attributeName="opacity" values="0;1" '
    'begin="1.85s" dur="0.2s" fill="freeze"/>')
add(f'<text x="{PAD}" y="{py:.1f}" fill="{ACCENT}" font-weight="600" '
    f'textLength="{prompt_w:.1f}" lengthAdjust="spacingAndGlyphs">'
    f'{escape(PROMPT)}</text>')
add(f'<rect x="{PAD + prompt_w + CW:.1f}" y="{py - FS * 0.78:.1f}" '
    f'width="{CW * 0.62:.1f}" height="{FS * 0.95:.1f}" fill="{ACCENT}">')
add('<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
    'dur="1.06s" repeatCount="indefinite"/>')
add('</rect></g>')
add('</g>')
add('</svg>')

OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT}  ({W}x{H}, aspect {W / H:.2f}; "
      f"cols art {ART_W:.0f} | ident {IDENT_W:.0f} | stack {STACK_W:.0f})")
