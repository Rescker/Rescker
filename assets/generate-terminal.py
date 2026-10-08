#!/usr/bin/env python3
"""Generates the profile README hero SVGs.

Emits two variants, selected at render time by a <picture> media query:

  terminal.svg          wide 3-column layout, aspect ~3:1  (desktop)
  terminal-compact.svg  2-column layout,   aspect ~1.4:1  (narrow viewports)

The split exists because the README renders the hero at width=100%. A single
asset cannot serve both: the wide variant is 1021px of artwork, so on a 336px
phone it scales to 0.33 and the 17px body text lands at ~5.6px, which is
unreadable. The compact variant scales to ~0.73 and stays legible.

Deterministic by construction:

* The wordmark uses a hand-defined 5x7 bitmap font (the classic terminal/BIOS
  face) drawn as SVG rectangles. No font is loaded or guessed, so it renders
  pixel-identically everywhere -- unlike figlet art, whose Unicode quadrant
  glyphs fall back to whatever the viewer's font happens to provide.
* Body text carries textLength + lengthAdjust="spacingAndGlyphs" so columns
  hold even when the fallback face is not truly monospace.

GitHub strips <style>/<script> from README HTML, but an SVG referenced through
<img> keeps its declarative SMIL animation. No third-party host is involved,
so nothing here can rate-limit, 402, or vanish.

Run:  python assets/generate-terminal.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent

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
LETTER_GAP = 1       # blank pixel columns between letters
LINE_GAP = 2         # blank pixel rows between the two words

# ------------------------------------------------------------------ content --
IDENTITY = [
    ("accent", "rescker@github"),
    ("rule", ""),
    ("strong", "Joaquim Mendes"),
    ("muted", "full stack engineer"),
]

# Two data lines rather than four: this is what keeps row 1 short in the wide
# variant, which is what buys the ~3:1 aspect.
STACK = [
    ("accent", "~/stack"),
    ("rule", ""),
    ("text", "Java · Spring Boot · React / TypeScript"),
    ("text", "PostgreSQL · MySQL · Docker · MongoDB"),
]

PROMPT = "rescker@github:~$"
COMMAND = "cat /etc/motd"
MOTD = [
    "State? It ain't. Hit the road, dude.",
    "This ain't no state property. 🚜",
]

ARIA = ("Terminal: Joaquim Mendes, full stack engineer. Java, Spring Boot, "
        "React, TypeScript, PostgreSQL, MySQL, Docker, MongoDB. "
        "State? It ain't. Hit the road, dude. This ain't no state property.")


def build(compact: bool) -> tuple[str, int, int, float]:
    """Render the hero. `compact` drops the stack column and shrinks the
    wordmark cells so the frame stays legible on narrow viewports."""
    # The compact variant must stay legible at ~336px (a 400px phone),
    # so it uses tighter padding and a narrower wordmark cell.
    pad = 16.0 if compact else 22.0
    title_h = 34.0
    radius = 10.0
    gap_ab = 24.0 if compact else 34.0
    gap_bc = 40.0
    cell_w = 5.6 if compact else 7.6
    cell_h = 8.6

    art_units_w = max(len(w) * 5 + (len(w) - 1) * LETTER_GAP for w in WORDMARK)
    art_units_h = len(WORDMARK) * 7 + (len(WORDMARK) - 1) * LINE_GAP
    art_w = art_units_w * cell_w
    art_h = art_units_h * cell_h

    def col_w(lines) -> float:
        return max(len(t) for k, t in lines if k != "rule") * CW

    ident_w = col_w(IDENTITY)
    ident_x = pad + art_w + gap_ab

    if compact:
        stack = []
        stack_w = 0.0
        stack_x = 0.0
        body_w = art_w + gap_ab + ident_w
    else:
        stack = STACK
        stack_w = col_w(STACK)
        stack_x = ident_x + ident_w + gap_bc
        body_w = art_w + gap_ab + ident_w + gap_bc + stack_w

    row1_h = max([art_h, len(IDENTITY) * LH] + ([len(stack) * LH] if stack else []))
    w = round(pad * 2 + body_w)
    row1_top = title_h + pad
    rule_y = row1_top + row1_h + 16
    code_top = rule_y + 22
    code_lines = 1 + len(MOTD) + 1
    h = round(code_top + (code_lines - 1) * LH + FS + pad - 6)

    o = []
    add = o.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="{escape(ARIA)}">')
    add('<title>rescker@github: ~</title>')

    # --- window ---
    add(f'<clipPath id="win"><rect x="0" y="0" width="{w}" height="{h}" '
        f'rx="{radius}"/></clipPath>')
    add('<g clip-path="url(#win)">')
    add(f'<rect x="0" y="0" width="{w}" height="{title_h}" fill="{SURFACE}"/>')
    add(f'<rect x="0" y="{title_h}" width="{w}" height="{h - title_h}" fill="{BG}"/>')
    add('</g>')
    add(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{radius}" '
        f'fill="none" stroke="{BORDER}"/>')

    # --- title bar ---
    cy = title_h / 2
    for i, color in enumerate((DOT_R, DOT_Y, DOT_G)):
        add(f'<circle cx="{pad + i * 18}" cy="{cy}" r="5.5" fill="{color}"/>')
    add(f'<text x="{w / 2:.1f}" y="{cy + 4:.1f}" fill="{MUTED}" '
        f'font-family="{FONT}" font-size="{TITLE_FS}" text-anchor="middle">'
        f'rescker@github — zsh</text>')

    # --- column A: wordmark as bitmap rects ---
    add(f'<g fill="{ACCENT}">')
    for li, word in enumerate(WORDMARK):
        y0 = row1_top + li * (7 + LINE_GAP) * cell_h
        x0 = pad
        for ch in word:
            for ry, row in enumerate(FONT_5X7[ch]):
                for rx, bit in enumerate(row):
                    if bit == "1":
                        add(f'<rect x="{x0 + rx * cell_w:.2f}" '
                            f'y="{y0 + ry * cell_h:.2f}" '
                            f'width="{cell_w:.2f}" height="{cell_h:.2f}"/>')
            x0 += (5 + LETTER_GAP) * cell_w
    add('</g>')

    # --- columns B (and C): text blocks ---
    def text_col(lines, x: float, width: float) -> None:
        add(f'<g font-family="{FONT}" font-size="{FS}">')
        for i, (kind, text) in enumerate(lines):
            y = row1_top + i * LH + FS * 0.86
            if kind == "rule":
                add(f'<line x1="{x:.1f}" y1="{y - FS * 0.42:.1f}" '
                    f'x2="{x + width * 0.72:.1f}" y2="{y - FS * 0.42:.1f}" '
                    f'stroke="{BORDER}" stroke-width="1.5"/>')
                continue
            color = {"accent": ACCENT, "strong": TEXT, "muted": MUTED,
                     "text": TEXT}[kind]
            weight = ' font-weight="600"' if kind in ("strong", "accent") else ""
            add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}"{weight} '
                f'textLength="{len(text) * CW:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
        add('</g>')

    text_col(IDENTITY, ident_x, ident_w)
    if stack:
        text_col(stack, stack_x, stack_w)

    # --- divider ---
    add(f'<line x1="{pad}" y1="{rule_y:.1f}" x2="{w - pad}" y2="{rule_y:.1f}" '
        f'stroke="{RULE}" stroke-width="1"/>')

    # --- full-width session output ---
    y0 = code_top + FS * 0.86
    # NOTE: the prompt carries no trailing space -- a trailing space is dropped
    # when textLength compresses the run, which would jam the command against
    # the '$'. The gap is instead one explicit character cell.
    prompt_w = len(PROMPT) * CW
    cmd_x = pad + prompt_w + CW
    cmd_w = len(COMMAND) * CW

    add(f'<g font-family="{FONT}" font-size="{FS}">')
    add(f'<text x="{pad}" y="{y0:.1f}" fill="{ACCENT}" font-weight="600" '
        f'textLength="{prompt_w:.1f}" lengthAdjust="spacingAndGlyphs">'
        f'{escape(PROMPT)}</text>')
    add('<clipPath id="cmd" clipPathUnits="userSpaceOnUse">')
    add(f'<rect x="{cmd_x:.1f}" y="{y0 - LH * 0.8:.1f}" width="0" '
        f'height="{LH:.1f}">')
    steps = ";".join(f"{i * CW:.1f}" for i in range(len(COMMAND) + 1))
    add(f'<animate attributeName="width" calcMode="discrete" dur="0.72s" '
        f'begin="0.55s" fill="freeze" values="{steps}"/>')
    add('</rect></clipPath>')
    add(f'<text x="{cmd_x:.1f}" y="{y0:.1f}" fill="{TEXT}" clip-path="url(#cmd)" '
        f'textLength="{cmd_w:.1f}" lengthAdjust="spacingAndGlyphs">'
        f'{escape(COMMAND)}</text>')
    add(f'<rect x="{cmd_x:.1f}" y="{y0 - FS * 0.78:.1f}" '
        f'width="{CW * 0.62:.1f}" height="{FS * 0.95:.1f}" fill="{ACCENT}">')
    add('<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.5;0.5;1" dur="1.06s" repeatCount="indefinite"/>')
    add('<animate attributeName="opacity" values="1;0" begin="0.55s" '
        'dur="0.01s" fill="freeze"/>')
    add('</rect>')
    for i, line in enumerate(MOTD):
        ly = y0 + (i + 1) * LH
        begin = 1.4 + i * 0.14
        add(f'<text x="{pad}" y="{ly:.1f}" fill="{TEXT}" opacity="0" '
            f'textLength="{len(line) * CW:.1f}" '
            f'lengthAdjust="spacingAndGlyphs">{escape(line)}')
        add(f'<animate attributeName="opacity" values="0;1" begin="{begin:.2f}s" '
            f'dur="0.28s" fill="freeze"/>')
        add('</text>')
    py = y0 + code_lines * LH - LH / 2
    add('<g opacity="0"><animate attributeName="opacity" values="0;1" '
        'begin="1.85s" dur="0.2s" fill="freeze"/>')
    add(f'<text x="{pad}" y="{py:.1f}" fill="{ACCENT}" font-weight="600" '
        f'textLength="{prompt_w:.1f}" lengthAdjust="spacingAndGlyphs">'
        f'{escape(PROMPT)}</text>')
    add(f'<rect x="{pad + prompt_w + CW:.1f}" y="{py - FS * 0.78:.1f}" '
        f'width="{CW * 0.62:.1f}" height="{FS * 0.95:.1f}" fill="{ACCENT}">')
    add('<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.5;0.5;1" dur="1.06s" repeatCount="indefinite"/>')
    add('</rect></g>')
    add('</g>')
    add('</svg>')
    return "\n".join(o) + "\n", w, h, w / h


for name, compact in (("terminal.svg", False), ("terminal-compact.svg", True)):
    svg, w, h, ratio = build(compact)
    (HERE / name).write_text(svg, encoding="utf-8")
    print(f"wrote {name:22} {w}x{h}  aspect {ratio:.2f}")
