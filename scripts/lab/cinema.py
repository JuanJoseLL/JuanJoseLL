"""FIG. A–C — "Fuera del editor": three original, animated illustrations.

Arrival (perspective), Creed (perseverance), Avatar (imagination). Nothing is
traced from the films: an ink ring around a hovering shell, a runner climbing
toward a sunrise, and a luminous willow releasing floating seeds.
"""

import math
import random

from .theme import (AMBER, CYAN, DIM, LINE, LINE2, MUTED, TEXT, VIOLET,
                    card, card_defs, corners, document, mix)
from .type import Type

W, H = 1200, 440
PANEL = 400
ART_Y = 196                 # vertical centre of each illustration
PHRASE = "#c3cadf"


def wrap(t, text, size, font, max_width):
    """Greedy wrap, then rebalanced so a two-line phrase never leaves a widow."""
    words = text.split()
    if t.width(text, size, font) > max_width and len(words) > 2:
        splits = [(" ".join(words[:i]), " ".join(words[i:])) for i in range(1, len(words))]
        fits = [pair for pair in splits if all(t.width(x, size, font) <= max_width for x in pair)]
        if fits:
            return list(min(fits, key=lambda pair: max(t.width(x, size, font) for x in pair)))
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if not current or t.width(trial, size, font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def panel_text(t, x0, index, tag, title, phrase, colour):
    out = [
        t.text(tag, x0 + 32, 106, 12, "mono", MUTED, tracking=0.14),
        t.text(f"FIG. {'ABC'[index]}", x0 + 368, 106, 12, "mono", DIM, tracking=0.14, anchor="end"),
        t.text(title, x0 + 32, 344, 30, "display", colour, tracking=0.05),
    ]
    for i, line in enumerate(wrap(t, phrase, 21, "serif", 336)):
        out.append(t.text(line, x0 + 32, 376 + i * 25, 21, "serif", PHRASE))
    return "".join(out)


# ARRIVAL ----------------------------------------------------------------------
def arrival(x0, rng):
    cx, cy, r = x0 + 200, ART_Y, 74
    tendrils = []
    for angle in (-128, -96, -61, -18, 22, 57, 101, 139, 176):
        a = math.radians(angle + rng.uniform(-6, 6))
        length = rng.uniform(10, 24)
        bend = math.radians(rng.uniform(-14, 14))
        sx, sy = cx + (r + 4) * math.cos(a), cy + (r + 4) * math.sin(a)
        ex, ey = cx + (r + 4 + length) * math.cos(a + bend), cy + (r + 4 + length) * math.sin(a + bend)
        qx, qy = cx + (r + 4 + length * .6) * math.cos(a), cy + (r + 4 + length * .6) * math.sin(a)
        width = rng.uniform(2.4, 5.5)
        tendrils.append(f'<path d="M{sx:.1f} {sy:.1f}Q{qx:.1f} {qy:.1f} {ex:.1f} {ey:.1f}" stroke-width="{width:.1f}"/>')
        if rng.random() < .55:
            tendrils.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{width * .75:.1f}" fill="#d5dcec" stroke="none"/>')
    # Ring drawn as a path so pathLength normalises the dash animation.
    ring_path = f"M{cx} {cy - r}a{r} {r} 0 1 1 0 {2 * r}a{r} {r} 0 1 1 0 {-2 * r}"
    shell = (f"M{cx} {cy - 64}C{cx + 30} {cy - 30} {cx + 30} {cy + 30} {cx} {cy + 66}"
             f"C{cx - 30} {cy + 30} {cx - 30} {cy - 30} {cx} {cy - 64}Z")
    return f"""
<ellipse cx="{cx}" cy="{cy + 6}" rx="178" ry="118" fill="url(#mistA)"/>
<circle class="spin" cx="{cx}" cy="{cy}" r="100" stroke="#65728b" stroke-dasharray="1 12" fill="none"/>
<g class="hover">
  <path d="{shell}" fill="url(#shell)"/>
  <path d="{shell}" stroke="#a9b4cf" stroke-opacity=".28" fill="none"/>
  <path d="M{cx} {cy - 50}C{cx + 14} {cy - 20} {cx + 14} {cy + 20} {cx} {cy + 52}" stroke="#c5cedf" stroke-opacity=".12" stroke-width="3" fill="none"/>
</g>
<g class="ink">
  <g mask="url(#drawA)">
    <g filter="url(#inkwarp)" fill="none" stroke="#d5dcec" stroke-linecap="round">
      <circle cx="{cx}" cy="{cy}" r="{r}" stroke-width="10" stroke-dasharray="150 7 40 12 108 10 66 72" opacity=".9"/>
      <circle cx="{cx}" cy="{cy}" r="{r - 6}" stroke-width="2.6" stroke-dasharray="24 15 82 8 58 24 30 12 60 20" opacity=".65"/>
      <circle cx="{cx}" cy="{cy}" r="{r + 7}" stroke-width="1.4" stroke-dasharray="6 30 14 50 4 90" opacity=".5"/>
    </g>
  </g>
  <g class="tendrils" filter="url(#inkwarp)" fill="none" stroke="#d5dcec" stroke-linecap="round" opacity=".8">{"".join(tendrils)}</g>
</g>
<g class="fog"><ellipse cx="{cx - 40}" cy="{cy + 78}" rx="150" ry="22" fill="url(#fog)"/></g>
<g class="fog late"><ellipse cx="{cx + 50}" cy="{cy + 92}" rx="170" ry="18" fill="url(#fog)"/></g>
<defs><mask id="drawA" maskUnits="userSpaceOnUse" x="{x0}" y="0" width="{PANEL}" height="{H}">
  <path class="draw" d="{ring_path}" pathLength="100" stroke="#fff" stroke-width="46" fill="none"/>
</mask></defs>"""


# CREED -------------------------------------------------------------------------
def creed(x0):
    bx, by, tread, rise, steps = x0 + 52, 286, 40, 22, 6
    d = f"M{bx} {by}" + "".join(f"h{tread}v{-rise}" for _ in range(steps)) + "h48"
    fill_d = d + f"V{by}Z"
    sun_x, sun_y = x0 + 346, by - rise * steps
    rays = "".join(
        f'<path d="M{sun_x + 33 * math.cos(math.radians(a)):.1f} {sun_y + 33 * math.sin(math.radians(a)):.1f}'
        f'L{sun_x + (37 if i % 2 else 41) * math.cos(math.radians(a)):.1f} {sun_y + (37 if i % 2 else 41) * math.sin(math.radians(a)):.1f}"/>'
        for i, a in enumerate(range(195, 346, 15)))
    shafts = "".join(
        f'<path class="shaft" style="animation-delay:{-i * 2.1:.1f}s" d="M{sun_x} {sun_y}L{x0 + a} 300L{x0 + b} 300Z" fill="url(#shaft)"/>'
        for i, (a, b) in enumerate([(70, 128), (150, 196), (226, 262)]))

    # Figure: feet at the origin, moved with CSS. Rest state = victory at the top.
    targets = [(bx + tread * k + 20, by - rise * k) for k in range(steps)] + [(bx + tread * steps + 12, by - rise * steps)]
    frames = [f"0%{{transform:translate({targets[0][0]}px,{targets[0][1]}px);opacity:0}}",
              f"4%{{transform:translate({targets[0][0]}px,{targets[0][1]}px);opacity:1}}"]
    start, end = 4, 60
    hop = (end - start) / (len(targets) - 1)
    for i in range(len(targets) - 1):
        (xa, ya), (xb, yb) = targets[i], targets[i + 1]
        mid = start + hop * (i + .5)
        frames.append(f"{mid:.2f}%{{transform:translate({(xa + xb) / 2:.0f}px,{min(ya, yb) - 8}px)}}")
        frames.append(f"{start + hop * (i + 1):.2f}%{{transform:translate({xb}px,{yb}px)}}")
    top = targets[-1]
    frames.append(f"88%{{transform:translate({top[0]}px,{top[1]}px);opacity:1}}")
    frames.append(f"96%,100%{{transform:translate({top[0]}px,{top[1]}px);opacity:0}}")
    climb = "@keyframes climb{" + "".join(frames) + "}"

    s = 1.35
    def P(points):
        return "M" + "L".join(f"{x * s:.1f} {y * s:.1f}" for x, y in points)
    head = f'<circle cx="{1.5 * s:.1f}" cy="{-17 * s:.1f}" r="{3 * s:.1f}" fill="#ffe2b0" stroke="none"/>'
    run_a = P([(1.5, -14), (-1, -6)]) + P([(1, -12), (5, -9), (8, -12)]) + P([(1, -12), (-3, -9), (-5, -6)]) \
        + P([(-1, -6), (3.5, -3), (3, 0)]) + P([(-1, -6), (-4, -3), (-8, -2)])
    run_b = P([(1.5, -14), (-1, -6)]) + P([(1, -12), (-3, -9), (-1, -6)]) + P([(1, -12), (4, -8), (7, -9)]) \
        + P([(-1, -6), (-3, -3), (-5, 0)]) + P([(-1, -6), (4, -4), (6, -1)])
    victory = P([(0, -14), (0, -6)]) + P([(0, -12), (-5, -20)]) + P([(0, -12), (5, -20)]) \
        + P([(0, -6), (-3, 0)]) + P([(0, -6), (3, 0)])
    figure = f"""<g class="runner" style="transform:translate({top[0]}px,{top[1]}px)" stroke="#ffe2b0" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" fill="none">
  <g class="running"><g class="legA">{head}<path d="{run_a}"/></g><g class="legB">{head}<path d="{run_b}"/></g></g>
  <g class="victory"><circle cx="0" cy="{-17 * s:.1f}" r="{3 * s:.1f}" fill="#ffe2b0" stroke="none"/><path d="{victory}"/></g>
</g>"""

    # ECG along the ground: a bright pulse travels a faint trace.
    beat = [(0, 0), (26, 0), (30, -4), (34, 0), (42, 0), (45, 3), (49, -24), (53, 8), (57, 0), (66, 0), (72, -6), (78, 0), (86, 0)]
    pts, ox, oy = [], x0 + 28, 308
    for b in range(4):
        for dx, dy in beat if b == 0 else beat[1:]:
            pts.append((ox + b * 86 + dx, oy + dy))
    ecg = "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
    return f"""
<circle class="bloom" cx="{sun_x}" cy="{sun_y}" r="150" fill="url(#sunglow)"/>
{shafts}
<clipPath id="horizon"><rect x="{x0}" y="60" width="{PANEL}" height="{sun_y - 60}"/></clipPath>
<g clip-path="url(#horizon)">
  <g class="rays" stroke="{AMBER}" stroke-width="2" stroke-linecap="round" opacity=".75">{rays}</g>
  <circle class="sunrise" cx="{sun_x}" cy="{sun_y}" r="28" fill="url(#sun)"/>
</g>
<path d="{fill_d}" fill="url(#stepfill)"/>
<path d="{d}" stroke="url(#steps)" stroke-width="2.6" stroke-linejoin="round" fill="none"/>
{"".join(f'<path d="M{bx + tread * k} {by - rise * k}h{tread}" stroke="#ffe7c2" stroke-opacity="{.08 + k * .05:.2f}" stroke-width="2.6"/>' for k in range(steps))}
{figure}
<path d="{ecg}" stroke="{AMBER}" stroke-opacity=".2" stroke-width="1.4" fill="none" stroke-linejoin="round"/>
<path class="ecg" d="{ecg}" stroke="#ffd79a" stroke-width="1.9" fill="none" stroke-linejoin="round" stroke-linecap="round"
  style="stroke-dasharray:64 {length:.0f};--len:{length:.0f}"/>
<style>{climb}.ecg{{animation:ecg 3.4s linear infinite}}@keyframes ecg{{from{{stroke-dashoffset:64}}to{{stroke-dashoffset:-{length:.0f}}}}}</style>"""


# AVATAR ------------------------------------------------------------------------
def avatar(x0, rng):
    cx, ground = x0 + 200, 292
    branches = [
        (f"M{cx} 176Q{cx - 46} 112 {cx - 118} 146", (cx, 176), (cx - 46, 112), (cx - 118, 146)),
        (f"M{cx} 176Q{cx + 48} 108 {cx + 122} 150", (cx, 176), (cx + 48, 108), (cx + 122, 150)),
        (f"M{cx} 168Q{cx - 20} 116 {cx - 66} 120", (cx, 168), (cx - 20, 116), (cx - 66, 120)),
        (f"M{cx} 168Q{cx + 22} 114 {cx + 70} 122", (cx, 168), (cx + 22, 114), (cx + 70, 122)),
    ]
    strands = []
    for _, p0, p1, p2 in branches:
        for k in range(7):
            u = .22 + k * .12 + rng.uniform(-.03, .03)
            if u > 1:
                break
            x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0]
            y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]
            length = rng.uniform(38, min(110, ground - 18 - y))
            colour = CYAN if rng.random() < .68 else VIOLET
            beads = "".join(
                f'<circle cx="{x:.1f}" cy="{y + length * f:.1f}" r="1.1" fill="{colour}" opacity=".7"/>'
                for f in (.35, .62, .82) if rng.random() < .7)
            strands.append(
                f'<g class="sway" style="animation-duration:{rng.uniform(4.5, 7.5):.1f}s;animation-delay:{-rng.uniform(0, 6):.1f}s">'
                f'<path d="M{x:.1f} {y:.1f}v{length:.1f}" stroke="{colour}" stroke-opacity=".55" stroke-width="1.1"/>{beads}'
                f'<circle cx="{x:.1f}" cy="{y + length:.1f}" r="7" fill="url(#halo{"C" if colour == CYAN else "V"})"/>'
                f'<circle cx="{x:.1f}" cy="{y + length:.1f}" r="1.9" fill="{colour}"/></g>')
    seeds = []
    for i in range(13):
        sx = cx + rng.uniform(-150, 150)
        sy = ground - rng.uniform(0, 30)
        colour = mix(CYAN, VIOLET, rng.random() * .6) if i % 3 else "#e9fffb"
        filaments = "".join(
            f'<path d="M0 0L{5.5 * math.cos(math.radians(a)):.1f} {5.5 * math.sin(math.radians(a)):.1f}"/>'
            for a in range(-160, 0, 26))
        seeds.append(
            f'<g transform="translate({sx:.1f} {sy:.1f})"><g class="seed s{i % 3}" '
            f'style="animation-duration:{rng.uniform(10, 15):.1f}s;animation-delay:{-rng.uniform(0, 14):.1f}s">'
            f'<circle r="9" fill="url(#haloC)" class="pulse"/>'
            f'<g stroke="{colour}" stroke-width=".8" stroke-linecap="round" opacity=".85">{filaments}</g>'
            f'<circle r="1.8" fill="{colour}"/></g></g>')
    sparks = "".join(
        f'<circle class="twinkle" cx="{x0 + rng.uniform(30, 370):.1f}" cy="{rng.uniform(118, 290):.1f}" r="{rng.uniform(.6, 1.2):.1f}" '
        f'fill="{CYAN if rng.random() < .5 else VIOLET}" style="animation-delay:{-rng.uniform(0, 4):.1f}s"/>' for _ in range(22))
    ferns = []
    for fx, flip, colour, size in [(cx - 128, 1, CYAN, 1.15), (cx - 100, -1, VIOLET, .85), (cx + 104, -1, CYAN, 1.05),
                                   (cx + 128, 1, VIOLET, .8), (cx - 160, -1, CYAN, .8), (cx + 162, -1, CYAN, .65)]:
        radius, stem = 8 * size, 28 * size
        ccx, ccy = fx + flip * radius, ground - stem
        pts = [(fx, ground), (fx - flip * 2 * size, ground - stem * .55)]
        for k in range(36):
            theta = math.pi + k / 35 * 2.3 * math.pi
            rad = radius * (1 - .72 * k / 35)
            pts.append((ccx + flip * rad * math.cos(theta), ccy + rad * math.sin(theta)))
        ferns.append(f'<path class="pulse" style="animation-delay:{-size * 3:.1f}s" d="M' + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
                     + f'" stroke="{colour}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>')
    mushrooms = "".join(
        f'<g class="pulse" style="animation-delay:{-i * .9:.1f}s"><path d="M{mx} {ground}v-{h}" stroke="#2b3a52" stroke-width="2"/>'
        f'<path d="M{mx - w} {ground - h}q{w} -{w * .9:.1f} {2 * w} 0z" fill="{VIOLET}" fill-opacity=".85"/>'
        f'<circle cx="{mx}" cy="{ground - h - 2}" r="{w * 2.2:.1f}" fill="url(#haloV)"/></g>'
        for i, (mx, h, w) in enumerate([(cx - 52, 9, 6), (cx - 40, 6, 4), (cx + 58, 8, 5), (cx + 150, 7, 4)]))
    trunk = (f"M{cx - 9} {ground}C{cx - 4} {ground - 40} {cx - 10} {ground - 70} {cx - 4} {ground - 104}"
             f"C{cx - 2} {ground - 116} {cx - 3} 172 {cx} 166C{cx + 3} 172 {cx + 2} {ground - 116} {cx + 5} {ground - 104}"
             f"C{cx + 11} {ground - 70} {cx + 4} {ground - 40} {cx + 10} {ground}Z")
    return f"""
<ellipse cx="{cx}" cy="{ground - 60}" rx="190" ry="140" fill="url(#forest)"/>
{sparks}
<path d="{trunk}" fill="#140f26" stroke="{VIOLET}" stroke-opacity=".6" stroke-width="1.2"/>
<g fill="none" stroke-linecap="round">{"".join(f'<path d="{b[0]}" stroke="#2a1f4a" stroke-width="5"/><path d="{b[0]}" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="1.3"/>' for b in branches)}</g>
{"".join(strands)}
<ellipse cx="{cx}" cy="{ground + 4}" rx="176" ry="12" fill="url(#mound)"/>
{"".join(ferns)}
{mushrooms}
{"".join(seeds)}"""


def build():
    rng = random.Random(7)
    t = Type("c")
    header = (
        t.text("JJ—LAB", 48, 46, 14, "monobold", TEXT, tracking=0.16)
        + t.text("/  FUERA DEL EDITOR", 48 + t.width("JJ—LAB", 14, "monobold", 0.16) + 14, 46, 14, "mono", MUTED, tracking=0.16)
        + t.text("3 HISTORIAS  ·  LOOP ∞", 1152, 46, 14, "mono", MUTED, tracking=0.16, anchor="end")
    )
    panels = [
        (arrival(0, rng), panel_text(t, 0, 0, "01 / PERSPECTIVA", "ARRIVAL", "Cambiar la perspectiva puede cambiarlo todo.", TEXT)),
        (creed(PANEL), panel_text(t, PANEL, 1, "02 / PERSEVERANCIA", "CREED", "Avanzar también es volver a intentarlo.", AMBER)),
        (avatar(2 * PANEL, rng), panel_text(t, 2 * PANEL, 2, "03 / IMAGINACIÓN", "AVATAR", "Imaginar mundos es el primer paso para construirlos.", CYAN)),
    ]
    clips = "".join(f'<clipPath id="pan{i}"><rect x="{i * PANEL + 1}" y="72" width="{PANEL - 2}" height="244"/></clipPath>' for i in range(3))
    art = "".join(f'<g clip-path="url(#pan{i})">{a}</g>' for i, (a, _) in enumerate(panels))
    copy = "".join(c for _, c in panels)
    marks = "".join(corners(i * PANEL + 18, 86, i * PANEL + 382, 418, size=8, color=LINE2) for i in range(3))

    style = """
.spin{transform-box:fill-box;transform-origin:center;animation:spin 60s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.hover{animation:hover 6s ease-in-out infinite}
@keyframes hover{50%{transform:translateY(-6px)}}
.draw{stroke-dasharray:100;transform-box:fill-box;transform-origin:center;animation:draw 10s cubic-bezier(.6,0,.3,1) infinite}
@keyframes draw{0%{stroke-dashoffset:100}32%,100%{stroke-dashoffset:0}}
.ink{animation:inkfade 10s ease infinite}
@keyframes inkfade{0%,86%{opacity:1}95%,100%{opacity:0}}
.tendrils{animation:tendril 10s ease infinite}
@keyframes tendril{0%,28%{opacity:0}38%,100%{opacity:.8}}
.fog{animation:fog 11s ease-in-out infinite alternate}
.fog.late{animation-duration:14s;animation-direction:alternate-reverse}
@keyframes fog{from{transform:translateX(-22px)}to{transform:translateX(22px)}}
.bloom{animation:bloom 7s ease-in-out infinite}
@keyframes bloom{0%,52%{opacity:.6}64%{opacity:1}88%{opacity:.85}100%{opacity:.6}}
.rays{transform-box:fill-box;transform-origin:center;animation:spin 40s linear infinite}
.shaft{animation:shaft 6.3s ease-in-out infinite}
.sunrise{animation:sunrise 7s ease-in-out infinite}
@keyframes sunrise{0%,100%{transform:translateY(6px)}60%,88%{transform:translateY(0)}}
@keyframes shaft{50%{opacity:.35}}
.runner{animation:climb 7s cubic-bezier(.45,0,.55,1) infinite}
.running{opacity:0;animation:runvis 7s step-end infinite}
@keyframes runvis{0%{opacity:1}60%{opacity:0}}
.victory{animation:vicvis 7s step-end infinite}
@keyframes vicvis{0%{opacity:0}60%{opacity:1}}
.legA{animation:legA .36s step-end infinite}.legB{opacity:0;animation:legB .36s step-end infinite}
@keyframes legA{0%{opacity:1}50%{opacity:0}}@keyframes legB{0%{opacity:0}50%{opacity:1}}
.sway{transform-box:fill-box;transform-origin:50% 0;animation:sway 6s ease-in-out infinite alternate}
@keyframes sway{from{transform:rotate(-2.6deg)}to{transform:rotate(2.6deg)}}
.seed{animation:rise0 12s linear infinite}.s1{animation-name:rise1}.s2{animation-name:rise2}
@keyframes rise0{0%{transform:translate(0,0);opacity:0}12%{opacity:1}50%{transform:translate(14px,-90px)}86%{opacity:1}100%{transform:translate(-4px,-190px);opacity:0}}
@keyframes rise1{0%{transform:translate(0,0);opacity:0}12%{opacity:1}50%{transform:translate(-16px,-84px)}86%{opacity:1}100%{transform:translate(8px,-180px);opacity:0}}
@keyframes rise2{0%{transform:translate(0,0);opacity:0}12%{opacity:1}35%{transform:translate(9px,-60px)}70%{transform:translate(-9px,-130px)}86%{opacity:1}100%{transform:translate(4px,-196px);opacity:0}}
.pulse{animation:pulse 2.6s ease-in-out infinite}
@keyframes pulse{50%{opacity:.35}}
.twinkle{animation:pulse 3.2s ease-in-out infinite}
"""
    defs = f"""{card_defs(W, H)}
<radialGradient id="mistA"><stop stop-color="#a5b1cd" stop-opacity=".2"/><stop offset="1" stop-color="#a5b1cd" stop-opacity="0"/></radialGradient>
<radialGradient id="fog"><stop stop-color="#c5cedf" stop-opacity=".22"/><stop offset="1" stop-color="#c5cedf" stop-opacity="0"/></radialGradient>
<linearGradient id="shell" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#2b3449"/><stop offset=".55" stop-color="#121826"/><stop offset="1" stop-color="#080b13"/></linearGradient>
<filter id="inkwarp" x="-25%" y="-25%" width="150%" height="150%"><feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="3" seed="7"/><feDisplacementMap in="SourceGraphic" scale="9" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation=".35"/></filter>
<radialGradient id="sunglow"><stop stop-color="{AMBER}" stop-opacity=".36"/><stop offset=".45" stop-color="{AMBER}" stop-opacity=".1"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>
<radialGradient id="sun" cx=".42" cy=".38"><stop stop-color="#fff6df"/><stop offset=".45" stop-color="#ffd59a"/><stop offset="1" stop-color="#e89a45"/></radialGradient>
<linearGradient id="shaft" x1="1" y1="0" x2="0" y2="1"><stop stop-color="{AMBER}" stop-opacity=".16"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>
<linearGradient id="steps" x1="0" x2="1" y1="1" y2="0"><stop stop-color="#5a4128"/><stop offset=".6" stop-color="{AMBER}"/><stop offset="1" stop-color="#fff0d4"/></linearGradient>
<linearGradient id="stepfill" x1="0" x2="0" y1="0" y2="1"><stop stop-color="{AMBER}" stop-opacity=".12"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>
<radialGradient id="forest" cy=".6"><stop stop-color="{CYAN}" stop-opacity=".16"/><stop offset=".5" stop-color="{VIOLET}" stop-opacity=".06"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="mound"><stop stop-color="{CYAN}" stop-opacity=".22"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="haloC"><stop stop-color="{CYAN}" stop-opacity=".55"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="haloV"><stop stop-color="{VIOLET}" stop-opacity=".55"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
{clips}"""
    body = f"""{card(W, H)}
{header}
<path d="M48 72H1152" stroke="{LINE}"/>
<path d="M400 92V412M800 92V412" stroke="{LINE}"/>
{marks}
{art}
{copy}"""
    title = "Fuera del editor — Arrival, Creed, Avatar"
    desc = ("Tres ilustraciones originales animadas: un logograma de tinta que se dibuja alrededor de una "
            "nave suspendida en la niebla (Arrival, perspectiva), una figura que sube escalones hacia un "
            "amanecer con un latido (Creed, perseverancia) y un árbol bioluminiscente que suelta semillas "
            "flotantes (Avatar, imaginación).")
    return {"cinema.svg": document(W, H, title, desc, body, style, defs, t)}
