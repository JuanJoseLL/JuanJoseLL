"""EXP. 001 — the double-slit hero.

Particles leave a source, cross two slits and land on a detector screen.
They do not build interference fringes: they build a name. When the
"measurement" sweeps the screen, the wave function collapses into solid type.
"""

import io
import math
import random
import shutil
import subprocess

from .theme import (AMBER, BG, CYAN, DIM, LINE, LINE2, MUTED, PANEL, ROSE, TEXT, VIOLET,
                    card, card_defs, corners, document, mix)
from .type import Type

W, H = 1200, 660
NAME, NAME_SIZE, NAME_X, NAME_Y = "JUAN JOSÉ", 172, 270, 360
SCREEN = (252, 198, 1152, 388)
CURVE_BASE, CURVE_H = 168, 60
SLITS = (284, 316)
BARRIER_X = 212

T_HIT0, T_HIT1 = 0.5, 4.8     # particles accumulate
T_SCAN, SCAN_DUR = 5.0, 1.0   # measurement sweep
T_TAG = 5.9                   # the human side appears


def _alpha_mask(path_d, scale=2):
    """Rasterises the name so particles can be sampled inside the glyphs."""
    from PIL import Image  # local build only

    if not shutil.which("rsvg-convert"):
        raise SystemExit("hero needs rsvg-convert (brew install librsvg)")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * scale}" height="{H * scale}" '
           f'viewBox="0 0 {W} {H}"><path d="{path_d}" fill="#000"/></svg>')
    png = subprocess.run(["rsvg-convert"], input=svg.encode(), capture_output=True, check=True).stdout
    image = Image.open(io.BytesIO(png)).getchannel("A")
    return image, scale


def _poisson(inside, box, spacing, rng, tries=90000):
    """Dart throwing with a grid: evenly spread but organic particle hits."""
    x0, y0, x1, y1 = box
    cell = spacing / math.sqrt(2)
    grid, points = {}, []
    for _ in range(tries):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if not inside(x, y):
            continue
        gx, gy = int(x / cell), int(y / cell)
        if any(
            math.dist((x, y), grid[(i, j)]) < spacing
            for i in range(gx - 2, gx + 3) for j in range(gy - 2, gy + 3) if (i, j) in grid
        ):
            continue
        grid[(gx, gy)] = (x, y)
        points.append((x, y))
    return points


def intensity(x):
    """Two-slit pattern: cos² fringes under a sinc² single-slit envelope."""
    centre, period, envelope = (NAME_X + 1135) / 2, 74.0, 300.0
    u = math.pi * (x - centre) / envelope
    sinc = 1.0 if abs(u) < 1e-6 else math.sin(u) / u
    return math.cos(math.pi * (x - centre) / period) ** 2 * (0.25 + 0.75 * sinc ** 2)


def build():
    rng = random.Random(1204)
    t = Type("h")
    name_glyphs = t.outline_glyphs(NAME, NAME_X, NAME_Y, NAME_SIZE, "display", tracking=-0.03)
    name_d = "".join(d for d, _, _ in name_glyphs)
    name_right = 1135
    sweep = name_right + 30 - NAME_X

    mask, scale = _alpha_mask(name_d)
    inside = lambda x, y: mask.getpixel((int(x * scale), int(y * scale))) > 140
    outside = lambda x, y: mask.getpixel((int(x * scale), int(y * scale))) < 10

    letters = _poisson(inside, (NAME_X - 4, SCREEN[1], name_right + 4, NAME_Y + 4), 5.3, rng)
    fringe = []
    while len(fringe) < 420:
        x = rng.uniform(SCREEN[0] + 10, SCREEN[2] - 10)
        y = rng.uniform(SCREEN[1] + 10, SCREEN[3] - 10)
        if rng.random() < intensity(x) and outside(x, y):
            fringe.append((x, y))

    hits_total = len(letters) + len(fringe)
    window = T_HIT1 - T_HIT0

    # Particles ----------------------------------------------------------------
    bands = 12
    by_band = [[] for _ in range(bands)]
    for x, y in letters:
        band = min(bands - 1, int((x - NAME_X) / (name_right - NAME_X) * bands))
        by_band[band].append((x, y, T_HIT0 + rng.random() * window))
    letter_svg = []
    for band, dots in enumerate(by_band):
        colour = mix(CYAN, VIOLET, band / (bands - 1))
        circles = "".join(
            f'<circle class="p" cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(1.45, 2.05):.2f}" '
            f'style="animation-delay:{delay:.2f}s"/>' for x, y, delay in dots)
        letter_svg.append(f'<g fill="{colour}">{circles}</g>')
    fringe_svg = "".join(
        f'<circle class="q" cx="{x:.1f}" cy="{y:.1f}" r="{rng.uniform(.9, 1.4):.2f}" '
        f'style="animation-delay:{T_HIT0 + rng.random() * window:.2f}s"/>' for x, y in fringe)

    impacts = []
    for x, y in rng.sample(letters, 46):
        delay = T_HIT0 + rng.random() * window
        impacts.append(f'<circle class="ring" cx="{x:.1f}" cy="{y:.1f}" r="3" style="animation-delay:{delay:.2f}s"/>')

    # Measured histogram and theoretical curve above the screen ---------------
    bins, x_lo, x_hi = 58, NAME_X, name_right
    counts = [0] * bins
    for x, _ in fringe:
        if x_lo <= x < x_hi:
            counts[int((x - x_lo) / (x_hi - x_lo) * bins)] += 1
    peak = max(counts) or 1
    bin_w = (x_hi - x_lo) / bins
    bars = "".join(
        f'<rect x="{x_lo + i * bin_w + 1.5:.1f}" y="{CURVE_BASE - c / peak * CURVE_H:.1f}" '
        f'width="{bin_w - 3:.1f}" height="{c / peak * CURVE_H:.1f}" rx="1"/>'
        for i, c in enumerate(counts) if c)
    curve_pts = []
    xs = [x_lo + i * 2 for i in range(int((x_hi - x_lo) / 2) + 1)]
    imax = max(intensity(x) for x in xs)
    for x in xs:
        curve_pts.append(f"{x:.0f},{CURVE_BASE - intensity(x) / imax * CURVE_H * 1.02:.1f}")
    curve = "M" + " L".join(curve_pts)
    ticks = "".join(f"M{x_lo + i * (x_hi - x_lo) / 16:.1f} {CURVE_BASE + 4}v{6 if i % 4 == 0 else 3}" for i in range(17))
    tick_labels = "".join(
        t.text(f"{v:+d}λ".replace("-", "−") if v else "0", x_lo + (v + 4) * (x_hi - x_lo) / 8, CURVE_BASE + 22, 10, "mono", DIM, anchor="middle")
        for v in (-4, -2, 0, 2, 4))

    # Ripples from both slits -------------------------------------------------
    ripples = []
    for slit, colour in zip(SLITS, (CYAN, VIOLET)):
        for k in range(6):
            ripples.append(
                f'<circle class="wave" cx="{BARRIER_X}" cy="{slit}" r="10" stroke="{colour}" '
                f'style="animation-delay:{-k * 0.9 + (0.45 if colour == VIOLET else 0):.2f}s"/>')

    # Photon packets between source and barrier -------------------------------
    packets = "".join(
        f'<circle class="photon" cx="112" cy="300" r="2.4" fill="{CYAN}" style="animation-delay:{-i * 0.35:.2f}s"/>'
        for i in range(3))

    # Odometer for the hit counter -------------------------------------------
    digits = f"{hits_total:04d}"
    odometer, digit_w, row_h = [], 12.4, 28
    for i, digit in enumerate(digits):
        loops = [0, 1, 3, 6][i]
        sequence = [str(n % 10) for n in range(loops * 10 + int(digit) + 1)]
        column = "".join(t.text(ch, 0, j * row_h, 20, "mono", TEXT) for j, ch in enumerate(sequence))
        shift = (len(sequence) - 1) * row_h
        odometer.append(
            f'<g transform="translate({i * digit_w + (8 if i >= 1 else 0):.1f} 0)">'
            f'<g class="odo" style="transform:translateY(-{shift}px)">{column}</g></g>')

    # Glitch slices -------------------------------------------------------------
    slices = [(SCREEN[1], 268), (268, 305), (305, NAME_Y + 6)]
    glitch = "".join(
        f'<clipPath id="slice{i}"><rect x="0" y="{a}" width="{W}" height="{b - a}"/></clipPath>' for i, (a, b) in enumerate(slices))

    # Copy ------------------------------------------------------------------------
    tagline_q = t.outline("Quantum", NAME_X + 2, 446, 58, "display", tracking=-0.015)
    q_width = t.width("Quantum", 58, "display", -0.015)
    slash_x = NAME_X + q_width + 24
    tagline_h = t.outline("human", slash_x + 36, 446, 76, "serif")
    descriptor = t.text("SOFTWARE DEVELOPER  ·  IA  ·  SISTEMAS DISTRIBUIDOS  ·  COMPUTACIÓN CUÁNTICA",
                        NAME_X + 3, 494, 14, "mono", MUTED, tracking=0.08)

    header = (
        t.text("JJ—LAB", 48, 47, 14, "monobold", TEXT, tracking=0.16)
        + t.text("/  EXP. 001  ·  DOBLE RENDIJA", 48 + t.width("JJ—LAB", 14, "monobold", 0.16) + 14, 47, 14, "mono", MUTED, tracking=0.16)
        + t.text("EN VIVO  ·  OBSERVADOR: TÚ", 1152, 47, 14, "mono", MUTED, tracking=0.16, anchor="end")
    )
    live_x = 1152 - t.width("EN VIVO  ·  OBSERVADOR: TÚ", 14, "mono", 0.16) - 14

    labels = (
        t.text("FUENTE", 76, 344, 10, "mono", DIM, tracking=0.14, anchor="middle")
        + t.text("A", BARRIER_X + 10, SLITS[0] - 8, 10, "monobold", CYAN)
        + t.text("B", BARRIER_X + 10, SLITS[1] + 18, 10, "monobold", VIOLET)
        + t.text("λ = CURIOSIDAD", 48, 470, 10, "mono", DIM, tracking=0.12)
        + t.text("PANTALLA DE DETECCIÓN", SCREEN[2], SCREEN[3] + 20, 10, "mono", DIM, tracking=0.14, anchor="end")
        + t.text("DISTRIBUCIÓN MEDIDA vs. TEÓRICA", NAME_X, 100, 10, "mono", DIM, tracking=0.14)
    )
    collapsed_note = t.text("⟶ FUNCIÓN DE ONDA COLAPSADA AL OBSERVAR", SCREEN[2], 432, 11, "mono", CYAN, tracking=0.1, anchor="end")

    cells = [("ESTADO", 48), ("IMPACTOS", 336), ("FUNCIÓN DE ONDA", 624), ("VELOCIDAD", 912)]
    readouts = "".join(t.text(label, x, 588, 11, "mono", DIM, tracking=0.16) for label, x in cells)
    state_super = t.text("SUPERPOSICIÓN", 48, 620, 19, "monobold", AMBER, tracking=0.04)
    state_done = t.text("COLAPSADO", 70, 620, 19, "monobold", CYAN, tracking=0.04)
    wave = t.text("|ψ⟩ = α|build⟩ + β|explore⟩", 624, 619, 15, "mono", TEXT)
    speed = t.text("SOY VELOZ", 912, 620, 19, "monobold", TEXT, tracking=0.04)

    style = f"""
.p{{animation:hit .7s cubic-bezier(.2,.7,.3,1) both}}
.q{{opacity:.38;animation:hit .7s ease-out both}}
@keyframes hit{{0%{{opacity:0}}6%{{opacity:1;fill:#fff}}}}
.ring{{fill:none;stroke:#fff;stroke-width:1;opacity:0;transform-box:fill-box;transform-origin:center;animation:ring .9s ease-out both}}
@keyframes ring{{0%{{opacity:.9;transform:scale(.4)}}100%{{opacity:0;transform:scale(5)}}}}
.reveal{{transform:translateX(0);animation:reveal {SCAN_DUR}s cubic-bezier(.65,0,.35,1) {T_SCAN}s both}}
@keyframes reveal{{from{{transform:translateX(-{sweep}px)}}}}
.scan{{opacity:0;animation:scan {SCAN_DUR}s cubic-bezier(.65,0,.35,1) {T_SCAN}s both}}
@keyframes scan{{0%{{opacity:0;transform:translateX(0)}}4%,92%{{opacity:1}}100%{{opacity:0;transform:translateX({sweep}px)}}}}
.bars{{transform-box:fill-box;transform-origin:bottom;animation:grow {T_HIT1 - T_HIT0}s steps(14) {T_HIT0}s both}}
@keyframes grow{{from{{transform:scaleY(0)}}}}
.curve{{stroke-dasharray:1600;animation:draw {T_HIT1 - T_HIT0 + .4}s ease-in-out {T_HIT0}s both}}
@keyframes draw{{from{{stroke-dashoffset:1600}}to{{stroke-dashoffset:0}}}}
.wave{{fill:none;stroke-width:1;vector-effect:non-scaling-stroke;opacity:0;transform-box:fill-box;transform-origin:center;animation:wave 5.4s linear infinite}}
@keyframes wave{{0%{{opacity:0;transform:scale(1)}}6%{{opacity:.5}}100%{{opacity:0;transform:scale(96)}}}}
.photon{{animation:fly 1.05s linear infinite}}
@keyframes fly{{from{{transform:translateX(0);opacity:0}}15%{{opacity:1}}85%{{opacity:1}}to{{transform:translateX({BARRIER_X - 116}px);opacity:0}}}}
.beam{{stroke-dasharray:3 7;animation:flow .6s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-10}}}}
.core{{animation:core 1.05s ease-in-out infinite}}
@keyframes core{{50%{{opacity:.45}}}}
.streak{{stroke-dasharray:10 6;animation:flow .4s linear infinite}}
.blink{{animation:blink 1.6s steps(2,end) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.super{{opacity:0;animation:super 9s steps(1,end) both}}
@keyframes super{{0%{{opacity:1}}{(T_SCAN + .5) / 9 * 100:.1f}%{{opacity:0}}100%{{opacity:0}}}}
.done{{animation:done .5s ease {T_SCAN + .5}s both}}
@keyframes done{{from{{opacity:0;transform:translateY(8px)}}}}
.flicker{{animation:flicker .45s steps(2,end) 13}}
@keyframes flicker{{50%{{opacity:.35}}}}
.odo{{animation:odo {T_HIT1 - T_HIT0 + .2}s cubic-bezier(.12,.6,.3,1) {T_HIT0}s both}}
@keyframes odo{{from{{transform:translateY(0)}}}}
.rise{{animation:rise .9s cubic-bezier(.2,.8,.2,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}}}
.type{{animation:type 1.3s steps(40,end) {T_TAG + .45}s both}}
@keyframes type{{from{{transform:scaleX(0)}}}}
.fade{{animation:fade 1s ease both}}
@keyframes fade{{from{{opacity:0}}}}
.glitch{{opacity:0;mix-blend-mode:screen;animation:glitch 7s steps(1,end) {T_SCAN + 2.2}s infinite}}
.g1{{animation-delay:{T_SCAN + 2.25}s}}.g2{{animation-delay:{T_SCAN + 2.3}s}}
@keyframes glitch{{0%{{opacity:.85;transform:translateX(-7px)}}2%{{opacity:.75;transform:translateX(5px)}}4%{{opacity:.9;transform:translateX(-3px)}}6%,100%{{opacity:0;transform:none}}}}
.sheen{{animation:sheen 7s ease-in-out {T_SCAN + 1.4}s infinite}}
@keyframes sheen{{0%{{transform:translateX(-500px)}}35%,100%{{transform:translateX({W}px)}}}}
"""

    defs = f"""{card_defs(W, H)}
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{NAME_X}" x2="{NAME_X + 560}"><stop stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="solid" gradientUnits="userSpaceOnUse" y1="{NAME_Y - 125}" y2="{NAME_Y}" x1="0" x2="0"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#c9d3f5"/></linearGradient>
<linearGradient id="beamfade" x2="1"><stop stop-color="{CYAN}" stop-opacity="0"/><stop offset=".85" stop-color="{CYAN}" stop-opacity=".9"/><stop offset="1" stop-color="#fff"/></linearGradient>
<linearGradient id="edge" x2="1"><stop offset="0" stop-color="#fff"/><stop offset=".97" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="sheenband" x2="1"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop stop-color="{VIOLET}" stop-opacity=".16"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="corehalo"><stop stop-color="{CYAN}" stop-opacity=".55"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.4"/></filter>
<filter id="soft" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="9"/></filter>
<clipPath id="field"><rect x="{BARRIER_X + 2}" y="78" width="{W - BARRIER_X}" height="470"/></clipPath>
<clipPath id="namearea"><path d="{name_d}"/></clipPath>
<mask id="revealmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="reveal" x="{-W + sweep + NAME_X}" y="0" width="{W}" height="{H}" fill="url(#edge)"/></mask>
<mask id="dimmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#fff"/><rect class="reveal" x="{-W + sweep + NAME_X}" y="0" width="{W}" height="{H}" fill="#3a3a3a"/></mask>
<mask id="typemask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="type" style="transform-origin:{NAME_X}px 0" x="{NAME_X}" y="470" width="820" height="34" fill="#fff"/></mask>
{glitch}"""

    slit_gap = 6
    barrier = (f"M{BARRIER_X} 168V{SLITS[0] - slit_gap}M{BARRIER_X} {SLITS[0] + slit_gap}V{SLITS[1] - slit_gap}"
               f"M{BARRIER_X} {SLITS[1] + slit_gap}V432")

    body = f"""{card(W, H)}
<ellipse cx="{(NAME_X + name_right) / 2:.0f}" cy="300" rx="560" ry="240" fill="url(#halo)"/>
<g class="fade">{header}</g>
<circle class="blink" cx="{live_x:.1f}" cy="42.5" r="4" fill="{ROSE}"/>
<path d="M48 76H1152" stroke="{LINE}"/>

<g clip-path="url(#field)">{"".join(ripples)}</g>

<g>
  <rect x="48" y="276" width="58" height="48" rx="9" fill="{PANEL}" stroke="{LINE2}"/>
  <path d="M58 286h10M58 314h10" stroke="{DIM}"/>
  <circle cx="90" cy="300" r="18" fill="url(#corehalo)" class="core"/>
  <circle cx="90" cy="300" r="5" fill="{CYAN}"/>
  <path class="beam" d="M106 300H{BARRIER_X - 2}" stroke="{CYAN}" stroke-opacity=".5"/>
  {packets}
  <path d="{barrier}" stroke="{MUTED}" stroke-width="3" stroke-linecap="round"/>
  <path d="M{BARRIER_X - 7} 168h14M{BARRIER_X - 7} 432h14" stroke="{DIM}"/>
</g>

{corners(*SCREEN, size=12)}
<g class="fade" style="animation-delay:.2s">
  <path d="M{x_lo} {CURVE_BASE + .5}H{x_hi}{ticks}" stroke="{LINE2}"/>
  <g class="bars" fill="{VIOLET}" fill-opacity=".22">{bars}</g>
  <path class="curve" d="{curve}" stroke="{CYAN}" stroke-width="1.4" fill="none"/>
  {tick_labels}
</g>

<g mask="url(#dimmask)">
  <g fill="{MUTED}">{fringe_svg}</g>
  {"".join(letter_svg)}
</g>
<g>{"".join(impacts)}</g>

<g mask="url(#revealmask)">
  <path d="{name_d}" fill="url(#ink)" filter="url(#soft)" opacity=".55"/>
  <path d="{name_d}" fill="url(#solid)"/>
  <g clip-path="url(#namearea)"><g transform="skewX(-18)"><rect class="sheen" x="0" y="{SCREEN[1]}" width="260" height="{NAME_Y - SCREEN[1] + 10}" fill="url(#sheenband)"/></g></g>
</g>
<g class="glitch" clip-path="url(#slice0)"><path d="{name_d}" fill="{CYAN}"/></g>
<g class="glitch g1" clip-path="url(#slice1)"><path d="{name_d}" fill="{ROSE}"/></g>
<g class="glitch g2" clip-path="url(#slice2)"><path d="{name_d}" fill="{VIOLET}"/></g>

<g class="scan">
  <rect x="{NAME_X - 70}" y="{SCREEN[1] + 14}" width="70" height="{SCREEN[3] - SCREEN[1] - 28}" fill="url(#beamfade)" opacity=".35" filter="url(#soft)"/>
  <path d="M{NAME_X} {SCREEN[1] - 10}V{SCREEN[3] + 10}" stroke="#fff" stroke-width="2"/>
  <path d="M{NAME_X} {SCREEN[1] - 10}V{SCREEN[3] + 10}" stroke="{CYAN}" stroke-width="7" filter="url(#glow)"/>
</g>

<g class="fade" style="animation-delay:.3s">{labels}</g>
<g class="done" style="animation-delay:{T_SCAN + 1.1}s">{collapsed_note}</g>

<g class="rise" style="animation-delay:{T_TAG}s">
  <path d="{tagline_q}" fill="url(#ink)"/>
  <path d="M{slash_x + 14:.1f} 404L{slash_x - 2:.1f} 452" stroke="{DIM}" stroke-width="2"/>
  <path d="{tagline_h}" fill="{TEXT}"/>
</g>
<g mask="url(#typemask)">{descriptor}</g>

<path d="M48 552H1152" stroke="{LINE}"/>
<path d="M324 566V632M612 566V632M900 566V632" stroke="{LINE}"/>
<g class="fade" style="animation-delay:.4s">{readouts}</g>
<g class="super"><g class="flicker">{state_super}</g></g>
<g class="done"><path d="M49 611l6 6 10-12" stroke="{CYAN}" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>{state_done}</g>
<svg x="336" y="600" width="64" height="26" overflow="hidden"><g transform="translate(0 20)">{"".join(odometer)}</g></svg>
{t.text("/ 1 OBSERVADOR", 402, 619, 11, "mono", DIM, tracking=0.1)}
{wave}
<g>{speed}<path class="streak" d="M1036 606h16M1030 613h22M1040 620h12" stroke="{AMBER}" stroke-width="2" stroke-linecap="round" opacity=".55"/><path class="core" d="M1068 598l-11 16h8l-4 13 12-17h-8l5-12z" fill="{AMBER}"/></g>
"""
    title = "Juan José — Quantum / Human"
    desc = ("Experimento de doble rendija animado: partículas cruzan dos rendijas y en la pantalla "
            "de detección forman el nombre JUAN JOSÉ; al observarlo, la función de onda colapsa en "
            "letras sólidas. Software developer: IA, sistemas distribuidos y computación cuántica.")
    return document(W, H, title, desc, body, style, defs, t), hits_total
