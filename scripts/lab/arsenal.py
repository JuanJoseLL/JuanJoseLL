"""The stack as a periodic table: six groups, twenty-four elements.

A spectrometer beam sweeps the table; every element it crosses lights up.
Desktop: groups are columns. Mobile: groups are rows.
"""

from .theme import (AMBER, BLUE, CYAN, DIM, GREEN, LINE, LINE2, MUTED, PANEL, ROSE, TEXT, VIOLET,
                    card, card_defs, document)
from .type import Type

GROUPS = [
    ("LENGUAJES", CYAN, [("Ja", "Java"), ("Py", "Python"), ("Ts", "TypeScript"), ("Go", "Go")]),
    ("INTERFACES", VIOLET, [("Re", "React"), ("Nx", "Next.js"), ("Vu", "Vue"), ("Tw", "Tailwind CSS")]),
    ("BACKEND", AMBER, [("Sb", "Spring Boot"), ("Fa", "FastAPI"), ("Dj", "Django"), ("Ns", "NestJS")]),
    ("DATOS", GREEN, [("Pg", "PostgreSQL"), ("Mg", "MongoDB"), ("Rd", "Redis"), ("Or", "Oracle")]),
    ("CLOUD", BLUE, [("Aw", "AWS"), ("Az", "Azure"), ("Dk", "Docker"), ("Tf", "Terraform")]),
    ("DEVOPS · IA", ROSE, [("Ga", "GitHub Actions"), ("Jk", "Jenkins"), ("An", "Ansible"), ("Lg", "LangGraph")]),
]
SWEEP = 9.0  # seconds per spectrometer pass


def tile(t, x, y, w, h, number, symbol, name, colour, sweep_x, total_w, intro, scale=1.0):
    """One element. sweep_x/total_w sync the highlight with the beam."""
    k = scale
    orbit_cx, orbit_cy, orbit_r = x + w - 22 * k, y + 22 * k, 9 * k
    period = 3 + (number * 7 % 11) / 2
    flash = -SWEEP + (sweep_x / total_w) * SWEEP * 0.8
    return f'''<g class="tile" style="animation-delay:{intro:.2f}s">
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{10 * k:.1f}" fill="{PANEL}" stroke="{LINE2}"/>
<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{10 * k:.1f}" fill="{colour}" fill-opacity=".05"/>
<rect class="lit" x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" rx="{10 * k:.1f}" fill="{colour}" fill-opacity=".07" stroke="{colour}" stroke-width="1.5" style="animation-delay:{flash:.2f}s"/>
<path d="M{x + 14 * k:.1f} {y + h - 1}h{28 * k:.1f}" stroke="{colour}" stroke-width="2"/>
{t.text(f"{number:02d}", x + 14 * k, y + 24 * k, 11 * k, "mono", DIM, tracking=.08)}
<circle cx="{orbit_cx:.1f}" cy="{orbit_cy:.1f}" r="{orbit_r:.1f}" fill="none" stroke="{colour}" stroke-opacity=".35"/>
<circle cx="{orbit_cx:.1f}" cy="{orbit_cy:.1f}" r="{2 * k:.1f}" fill="{colour}" fill-opacity=".7"/>
<g class="spin" style="transform-origin:{orbit_cx:.1f}px {orbit_cy:.1f}px;animation-duration:{period:.1f}s"><circle cx="{orbit_cx + orbit_r:.1f}" cy="{orbit_cy:.1f}" r="{2.2 * k:.1f}" fill="{colour}"/></g>
{t.text(symbol, x + 13 * k, y + h * .64, 44 * k, "display", TEXT, tracking=-.02)}
{t.text(name, x + 14 * k, y + h - 16 * k, 12 * k, "mono", MUTED, tracking=.02)}
</g>'''


STYLE = f"""
.tile{{animation:rise .7s cubic-bezier(.2,.8,.2,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(16px)}}}}
.lit{{opacity:0;animation:lit {SWEEP}s linear infinite}}
@keyframes lit{{0%{{opacity:1}}12%{{opacity:0}}100%{{opacity:0}}}}
.spin{{animation:spin 4s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.beam{{animation:beam {SWEEP}s linear infinite}}
.fade{{animation:fade 1s ease both}}
@keyframes fade{{from{{opacity:0}}}}
"""


def _beam_style(x0, x1):
    return f"@keyframes beam{{0%{{transform:translateX({x0}px);opacity:0}}3%{{opacity:1}}77%{{opacity:1}}80%,100%{{transform:translateX({x1}px);opacity:0}}}}"


def desktop():
    W, H = 1200, 650
    t = Type("a")
    x0, y0, tw, th, gap = 48, 150, 174, 98, 12
    total = 6 * tw + 5 * gap
    tiles, heads = [], []
    number = 0
    for g, (group, colour, elements) in enumerate(GROUPS):
        gx = x0 + g * (tw + gap)
        heads.append(
            f'<path d="M{gx} 128h{tw}" stroke="{colour}" stroke-opacity=".5"/>'
            + t.text(f"G{g + 1}", gx, 116, 12, "monobold", colour, tracking=.12)
            + t.text(group, gx + 30, 116, 11, "mono", MUTED, tracking=.12))
        for r, (symbol, name) in enumerate(elements):
            number += 1
            gy = y0 + r * (th + gap)
            tiles.append(tile(t, gx, gy, tw, th, number, symbol, name, colour,
                              gx - x0 + tw / 2, total, .25 + (g + r) * .07))
    header = (t.text("JJ—LAB", 48, 47, 14, "monobold", TEXT, tracking=.16)
              + t.text("/  TABLA PERIÓDICA DEL ARSENAL", 48 + t.width("JJ—LAB", 14, "monobold", .16) + 14, 47, 14, "mono", MUTED, tracking=.16)
              + t.text("24 ELEMENTOS  ·  6 GRUPOS  ·  ESTABLES", 1152, 47, 14, "mono", MUTED, tracking=.16, anchor="end"))
    beam_y0, beam_y1 = 96, y0 + 4 * th + 3 * gap + 10
    body = f"""{card(W, H)}
<g class="fade">{header}</g>
<path d="M48 76H1152" stroke="{LINE}"/>
<g class="fade" style="animation-delay:.15s">{"".join(heads)}</g>
{"".join(tiles)}
<g class="beam">
  <rect x="-60" y="{beam_y0}" width="60" height="{beam_y1 - beam_y0}" fill="url(#beamfade)"/>
  <path d="M0 {beam_y0}V{beam_y1}" stroke="#fff" stroke-opacity=".7"/>
</g>
{t.text("Las herramientas cambian. La curiosidad es el elemento estable.", 48, H - 30, 21, "serif", MUTED)}
{t.text("Z = NÚMERO ATÓMICO  ·  COLOR = GRUPO", 1152, H - 33, 11, "mono", DIM, tracking=.14, anchor="end")}
"""
    defs = card_defs(W, H) + f'<linearGradient id="beamfade" x2="1"><stop stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".16"/></linearGradient>'
    style = STYLE + _beam_style(x0 - 10, x0 + total + 10)
    desc = "Tabla periódica con mi stack: " + "; ".join(
        f"{group.title()}: " + ", ".join(n for _, n in elements) for group, _, elements in GROUPS) + "."
    return document(W, H, "El arsenal — tabla periódica del stack", desc, body, style, defs, t)


def mobile():
    W = 640
    t = Type("a")
    x0, y0, label_w, tw, th, gap = 20, 104, 0, 145, 108, 8
    rows = []
    number = 0
    total = 4 * tw + 3 * gap
    for g, (group, colour, elements) in enumerate(GROUPS):
        gy = y0 + g * (th + 44)
        rows.append(t.text(f"G{g + 1}", x0, gy - 12, 14, "monobold", colour, tracking=.12)
                    + t.text(group, x0 + 34, gy - 12, 13, "mono", MUTED, tracking=.12))
        for c, (symbol, name) in enumerate(elements):
            number += 1
            gx = x0 + c * (tw + gap)
            rows.append(tile(t, gx, gy, tw, th, number, symbol, name.replace("GitHub ", "GH "), colour,
                             gx - x0 + tw / 2, total, .2 + (g + c) * .06, scale=1.04))
    H = y0 + 6 * (th + 44) - 10
    header = (t.text("JJ—LAB", 20, 44, 16, "monobold", TEXT, tracking=.14)
              + t.text("/  ARSENAL", 20 + t.width("JJ—LAB", 16, "monobold", .14) + 12, 44, 16, "mono", MUTED, tracking=.14)
              + t.text("24 ELEMENTOS", 620, 44, 16, "mono", MUTED, tracking=.14, anchor="end"))
    body = f"""{card(W, H)}
<g class="fade">{header}</g>
<path d="M20 68H620" stroke="{LINE}"/>
{"".join(rows)}
<g class="beam">
  <rect x="-50" y="78" width="50" height="{H - 100}" fill="url(#beamfade)"/>
  <path d="M0 78V{H - 22}" stroke="#fff" stroke-opacity=".6"/>
</g>
"""
    defs = card_defs(W, H) + f'<linearGradient id="beamfade" x2="1"><stop stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".16"/></linearGradient>'
    style = STYLE + _beam_style(x0 - 10, x0 + total + 10)
    desc = "Versión móvil de la tabla periódica del stack: los mismos 24 elementos en seis grupos."
    return document(W, H, "El arsenal — versión móvil", desc, body, style, defs, t)


def build():
    return {"stack.svg": desktop(), "stack-mobile.svg": mobile()}
