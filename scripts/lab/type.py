"""Typesetting for SVG without web fonts.

GitHub serves README images with a strict sandbox, so instead of relying on
@font-face every string is shaped with HarfBuzz (kerning included) and drawn
from the real glyph outlines of the bundled OFL fonts.

Two outputs:
  * Type.text()    -> <use> references to shared glyph <path>s in <defs>.
                      Compact; ideal for many small, solid-coloured labels.
  * Type.outline() -> one absolute <path>, so gradients, strokes, masks and
                      per-letter animation behave like ordinary shapes.
"""

from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).with_name("fonts")
FACES = {
    "display": "SpaceGrotesk-Bold.ttf",
    "medium": "SpaceGrotesk-Medium.ttf",
    "mono": "JetBrainsMono-Regular.ttf",
    "monobold": "JetBrainsMono-Bold.ttf",
    "serif": "InstrumentSerif-Italic.ttf",
}
KEYS = {"display": "D", "medium": "M", "mono": "m", "monobold": "b", "serif": "s"}
NO_LIGATURES = {"liga": False, "calt": False, "clig": False}


def _num(value):
    text = f"{value:.1f}"
    return text[:-2] if text.endswith(".0") else text


class Face:
    def __init__(self, name):
        self.name = name
        self.key = KEYS[name]
        path = FONTS / FACES[name]
        self.hb = hb.Font(hb.Face(path.read_bytes()))
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upm = self.tt["head"].unitsPerEm
        os2 = self.tt["OS/2"]
        self.cap = getattr(os2, "sCapHeight", 0) or int(self.upm * 0.7)
        self.xheight = getattr(os2, "sxHeight", 0) or int(self.upm * 0.5)

    def shape(self, text):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        hb.shape(self.hb, buffer, NO_LIGATURES)
        return [(info.codepoint, pos.x_advance) for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions)]

    def draw(self, gid, pen):
        self.glyphs[self.order[gid]].draw(pen)

    def is_blank(self, gid):
        pen = SVGPathPen(self.glyphs)
        self.draw(gid, pen)
        return not pen.getCommands()


@lru_cache(maxsize=None)
def face(name):
    return Face(name)


class Type:
    """Collects the glyphs a document uses and emits them once in <defs>."""

    def __init__(self, prefix="g"):
        self.prefix = prefix
        self.used = {}

    # Layout ---------------------------------------------------------------
    def layout(self, text, size, font="mono", tracking=0.0):
        """Returns ([(gid, x_px)], width_px). Tracking is in em."""
        f = face(font)
        scale = size / f.upm
        pen_x, placed = 0.0, []
        for gid, advance in f.shape(text):
            placed.append((gid, pen_x))
            pen_x += advance * scale + tracking * size
        width = pen_x - (tracking * size if placed else 0)
        return placed, width

    def width(self, text, size, font="mono", tracking=0.0):
        return self.layout(text, size, font, tracking)[1]

    def _origin(self, text, x, size, font, tracking, anchor):
        placed, width = self.layout(text, size, font, tracking)
        if anchor == "middle":
            x -= width / 2
        elif anchor == "end":
            x -= width
        return placed, x

    # <use> based labels ----------------------------------------------------
    def text(self, text, x, y, size, font="mono", fill=None, tracking=0.0, anchor="start", attrs=""):
        f = face(font)
        placed, x0 = self._origin(text, x, size, font, tracking, anchor)
        scale = size / f.upm
        uses = []
        for gid, px in placed:
            if f.is_blank(gid):
                continue
            ref = f"{self.prefix}{f.key}{gid}"
            self.used[ref] = (font, gid)
            uses.append(f'<use href="#{ref}" x="{_num(px / scale)}"/>')
        fill_attr = f' fill="{fill}"' if fill else ""
        extra = f" {attrs}" if attrs else ""
        return (f'<g transform="translate({_num(x0)} {_num(y)}) scale({scale:.5f} {-scale:.5f})"'
                f'{fill_attr}{extra}>{"".join(uses)}</g>')

    def defs(self):
        out = []
        for ref, (font, gid) in sorted(self.used.items()):
            pen = SVGPathPen(face(font).glyphs, ntos=lambda v: f"{v:.0f}")
            face(font).draw(gid, pen)
            out.append(f'<path id="{ref}" d="{pen.getCommands()}"/>')
        return "".join(out)

    # Absolute outlines -----------------------------------------------------
    def outline_glyphs(self, text, x, y, size, font="display", tracking=0.0, anchor="start"):
        """Per-glyph absolute path data: [(d, x_px, advance_px)]."""
        f = face(font)
        placed, x0 = self._origin(text, x, size, font, tracking, anchor)
        scale = size / f.upm
        glyphs = []
        for index, (gid, px) in enumerate(placed):
            pen = SVGPathPen(f.glyphs, ntos=lambda v: _num(v))
            f.draw(gid, TransformPen(pen, (scale, 0, 0, -scale, x0 + px, y)))
            d = pen.getCommands()
            nxt = placed[index + 1][1] if index + 1 < len(placed) else None
            if d:
                glyphs.append((d, x0 + px, (nxt - px) if nxt is not None else None))
        return glyphs

    def outline(self, text, x, y, size, font="display", tracking=0.0, anchor="start"):
        return "".join(d for d, _, _ in self.outline_glyphs(text, x, y, size, font, tracking, anchor))
