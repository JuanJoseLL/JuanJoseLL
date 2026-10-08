"""EXP. 002–005 — one animated specimen card per featured repository.

Every card shares the same shell (header, registration marks, title, chips)
and a mini-visual that tells what the project actually does. All motion is
CSS keyframes on one shared clock per card, so every loop is seamless and
`prefers-reduced-motion` falls back to a complete resting frame.
"""

import math
import random

from .theme import (AMBER, BG, BLUE, CYAN, DIM, GREEN, LINE, LINE2, MUTED, PANEL, ROSE, TEXT,
                    VIOLET, card, card_defs, corners, document, mix)
from .type import Type

W, H = 600, 360
CHIP_TEXT = "#c3cbe3"


# Timeline helpers -------------------------------------------------------------
def keyframes(name, period, frames):
    """frames: [(seconds, 'css declarations')] -> @keyframes with strictly rising stops."""
    out, last = [], -1.0
    for seconds, decls in sorted(frames, key=lambda f: f[0]):
        stop = min(100.0, max(0.0, seconds / period * 100))
        if stop <= last:
            stop = last + 0.01
        out.append(f"{stop:.2f}%{{{decls}}}")
        last = stop
    return f"@keyframes {name}{{{''.join(out)}}}"


def windows(period, spans, off, on, ramp=0.15):
    """Off/on toggles: `on` during each (start, end) span, `off` elsewhere."""
    frames = [(0, off)]
    for start, end in spans:
        frames += [(max(0.0, start - ramp), off), (start, on), (end, on), (min(period, end + ramp), off)]
    return frames + [(period, off)]


def cubic(p0, p1, p2, p3, n=18):
    pts = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def route(period, legs, fade=0.08):
    """A packet travelling legs [(points, t0, t1)] at constant speed per leg; hidden otherwise."""
    frames = []
    first, last = legs[0][0][0], legs[-1][0][-1]
    frames += [(0, first, 0), (legs[0][1] - fade, first, 0)]
    for pts, t0, t1 in legs:
        cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            cum.append(cum[-1] + math.dist(a, b))
        total = cum[-1] or 1
        frames += [(t0 + (t1 - t0) * c / total, p, 1) for c, p in zip(cum, pts)]
    frames += [(legs[-1][2] + fade, last, 0), (period, last, 0)]
    return [(t, f"transform:translate({p[0]:.1f}px,{p[1]:.1f}px);opacity:{o}") for t, p, o in frames]


def packet(name, period, colour, size=1.0):
    return (f'<g class="pk" style="animation:{name} {period}s linear infinite">'
            f'<circle r="{8.5 * size:.1f}" fill="{colour}" opacity=".18"/>'
            f'<circle r="{3.6 * size:.1f}" fill="{colour}"/><circle r="{1.6 * size:.1f}" fill="#fff"/></g>')


def arrow(x, y, angle, colour, size=5):
    """Chevron arrowhead pointing along `angle` degrees with its tip at (x, y)."""
    a = math.radians(angle)
    pts = []
    for side in (-1, 1):
        b = a + math.pi + side * 0.55
        pts.append((x + size * math.cos(b), y + size * math.sin(b)))
    return (f'<path d="M{pts[0][0]:.1f} {pts[0][1]:.1f}L{x} {y}L{pts[1][0]:.1f} {pts[1][1]:.1f}" '
            f'stroke="{colour}" stroke-width="1.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def anim(cls, name, period, timing="linear"):
    return f".{cls}{{animation:{name} {period}s {timing} infinite}}"


# Shell ----------------------------------------------------------------------------
def shell(t, number, key, title, desc, chips, accent, visual, style, defs, aria):
    label = f"EXP. {number:03d}"
    label_w = t.width(label, 12, "monobold", 0.16)
    chip_svg, x = [], 28
    for chip in chips:
        w = t.width(chip, 13, "mono") + 24
        chip_svg.append(f'<rect x="{x}" y="316.5" width="{w:.1f}" height="27" rx="13.5" fill="{PANEL}" stroke="{LINE2}"/>'
                        + t.text(chip, x + 12, 334.5, 13, "mono", CHIP_TEXT))
        x += w + 8
    body = f"""{card(W, H, radius=22)}
<g fill="none">
<ellipse cx="300" cy="148" rx="300" ry="120" fill="url(#accentglow)"/>
{t.text(label, 28, 38, 12, "monobold", TEXT, tracking=0.16)}
{t.text("·  " + key, 28 + label_w + 10, 38, 12, "mono", MUTED, tracking=0.16)}
{t.text("REPO", 532, 38, 12, "mono", MUTED, tracking=0.16, anchor="end")}
<circle cx="555" cy="34" r="12" stroke="{accent}" stroke-opacity=".55"/>
<path d="M550.5 38.5l9-9M552.5 29.5h7v7" stroke="{accent}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M28 54H572" stroke="{LINE}"/>
{corners(28, 66, 572, 228, size=8)}
<g>{visual}</g>
<path d="{t.outline(f"{number:02d}", 574, 308, 96, "serif", anchor="end")}" fill="{accent}" fill-opacity=".13"/>
<path d="{t.outline(title, 26, 272, 36, "display", tracking=-0.02)}" fill="{TEXT}"/>
{t.text(desc, 28, 300, 16, "medium", MUTED)}
{"".join(chip_svg)}
</g>"""
    defs = f"""{card_defs(W, H)}
<radialGradient id="accentglow"><stop stop-color="{accent}" stop-opacity=".07"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
{defs}"""
    style = ".pk{opacity:0}" + style
    return document(W, H, f"{label} — {title}", aria, body, style, defs, t)


# EXP. 002 — Stock Recommender ------------------------------------------------------
def stock():
    t, P = Type("s"), 9.0
    rng = random.Random(7)
    x0, x1, top, bot = 46, 404, 88, 212
    closes = [52, 50.5, 48, 47.2, 45.5, 44.2, 43.6, 45.4, 47.6, 49.2, 52.4, 55.1, 57.3, 58.2, 57.4,
              58.6, 57.9, 60.2, 63.4, 66.1, 68.0, 65.2, 62.1, 63.0, 61.2, 62.4]
    lo, hi = min(closes) - 2.2, max(closes) + 1.6
    y = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)
    step = (x1 - x0) / len(closes)
    T0, T1, FADE = 0.4, 5.4, 8.1
    at = lambda x: T0 + (x - x0) / (x1 - x0) * (T1 - T0)

    candles, pts = [], []
    for i, close in enumerate(closes):
        open_ = closes[i - 1] if i else close + 1
        high = max(open_, close) + rng.uniform(.3, 1.4)
        low = min(open_, close) - rng.uniform(.3, 1.4)
        cx = x0 + step * (i + .5)
        up = close >= open_
        colour = GREEN if up else ROSE
        body_top, body_h = y(max(open_, close)), max(1.6, abs(y(open_) - y(close)))
        fill = f'fill="{colour}" fill-opacity=".55"' if up else f'fill="{BG}"'
        candles.append(f'<path d="M{cx:.1f} {y(high):.1f}V{y(low):.1f}" stroke="{colour}" stroke-opacity=".6"/>'
                       f'<rect x="{cx - 3.4:.1f}" y="{body_top:.1f}" width="6.8" height="{body_h:.1f}" rx="1" {fill} stroke="{colour}" stroke-opacity=".8"/>')
        pts.append((cx, y(close)))
    line = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    area = line + f" L{pts[-1][0]:.1f},{bot} L{pts[0][0]:.1f},{bot}Z"
    grid = "".join(f'<path d="M{x0} {top + i * (bot - top) / 4:.1f}H{x1}" stroke="{LINE}" stroke-dasharray="2 4"/>' for i in range(5))

    # Signals: index, label, colour, score
    signals = [(6, "BUY", GREEN, 82), (15, "HOLD", CYAN, 61), (22, "WATCH", AMBER, 44)]
    tags, styles = [], []
    for k, (i, word, colour, score) in enumerate(signals):
        px, py = pts[i]
        tw = t.width(word, 11, "monobold", 0.08) + 14
        ta = at(px)
        tags.append(
            f'<g class="tag{k}"><circle cx="{px:.1f}" cy="{py:.1f}" r="5" stroke="{colour}" stroke-width="1.5" fill="{BG}"/>'
            f'<path d="M{px:.1f} {py - 6:.1f}V{py - 13:.1f}" stroke="{colour}"/>'
            f'<rect x="{px - tw / 2:.1f}" y="{py - 32:.1f}" width="{tw:.1f}" height="19" rx="4" fill="{BG}"/>'
            f'<rect x="{px - tw / 2:.1f}" y="{py - 32:.1f}" width="{tw:.1f}" height="19" rx="4" fill="{colour}" fill-opacity=".14" stroke="{colour}"/>'
            + t.text(word, px, py - 18.5, 11, "monobold", colour, tracking=0.08, anchor="middle") + "</g>")
        styles.append(keyframes(f"tag{k}", P, [(0, "opacity:0;transform:translateY(5px)"), (ta - .02, "opacity:0;transform:translateY(5px)"),
                                              (ta + .25, "opacity:1;transform:translateY(0)"), (FADE, "opacity:1;transform:translateY(0)"),
                                              (FADE + .5, "opacity:0;transform:translateY(0)"), (P, "opacity:0")]))
        styles.append(anim(f"tag{k}", f"tag{k}", P, "ease-out"))

    lead = [(0, f"transform:translate({pts[0][0]:.1f}px,{pts[0][1]:.1f}px);opacity:0"), (T0 - .05, f"transform:translate({pts[0][0]:.1f}px,{pts[0][1]:.1f}px);opacity:0")]
    guide = [(0, f"transform:translateY({pts[0][1]:.1f}px);opacity:0"), (T0 - .05, f"transform:translateY({pts[0][1]:.1f}px);opacity:0")]
    for px, py in pts:
        lead.append((at(px), f"transform:translate({px:.1f}px,{py:.1f}px);opacity:1"))
        guide.append((at(px), f"transform:translateY({py:.1f}px);opacity:1"))
    end = pts[-1]
    lead += [(FADE, f"transform:translate({end[0]:.1f}px,{end[1]:.1f}px);opacity:1"), (FADE + .5, f"transform:translate({end[0]:.1f}px,{end[1]:.1f}px);opacity:0"), (P, f"transform:translate({end[0]:.1f}px,{end[1]:.1f}px);opacity:0")]
    guide += [(FADE, f"transform:translateY({end[1]:.1f}px);opacity:1"), (FADE + .5, f"transform:translateY({end[1]:.1f}px);opacity:0"), (P, f"transform:translateY({end[1]:.1f}px);opacity:0")]

    sweep = [(0, "transform:scaleX(0);opacity:1"), (T0, "transform:scaleX(0);opacity:1"), (T1, "transform:scaleX(1);opacity:1"),
             (FADE, "transform:scaleX(1);opacity:1"), (FADE + .5, "transform:scaleX(1);opacity:0"), (P, "transform:scaleX(0);opacity:0")]

    # Score gauge -------------------------------------------------------------------
    gx, gy, r = 490, 152, 50
    def arc(v0, v1, radius):
        a0, a1 = math.radians(180 + v0 * 1.8), math.radians(180 + v1 * 1.8)
        return (f"M{gx + radius * math.cos(a0):.1f} {gy + radius * math.sin(a0):.1f}"
                f"A{radius} {radius} 0 0 1 {gx + radius * math.cos(a1):.1f} {gy + radius * math.sin(a1):.1f}")
    ticks = "".join(
        f'M{gx + (r - 9) * math.cos(math.radians(180 + v * 1.8)):.1f} {gy + (r - 9) * math.sin(math.radians(180 + v * 1.8)):.1f}'
        f'L{gx + (r - (14 if v % 50 else 17)) * math.cos(math.radians(180 + v * 1.8)):.1f} {gy + (r - (14 if v % 50 else 17)) * math.sin(math.radians(180 + v * 1.8)):.1f}'
        for v in range(0, 101, 10))
    needle_frames = [(0, "transform:rotate(0deg)")]
    readouts = []
    for k, (i, word, colour, score) in enumerate(signals):
        ta = at(pts[i][0])
        prev = signals[k - 1][3] * 1.8 if k else 0
        needle_frames += [(ta - .05, f"transform:rotate({prev}deg)"), (ta + .55, f"transform:rotate({score * 1.8}deg)")]
        nxt = at(pts[signals[k + 1][0]][0]) if k + 1 < len(signals) else FADE + .5
        base = 1 if k == 0 else 0
        readouts.append(
            f'<g class="val{k}" style="opacity:{base}"><path d="{t.outline(str(score), gx, 194, 30, "display", anchor="middle")}" fill="{TEXT}"/>'
            + t.text(word, gx, 213, 12, "monobold", colour, tracking=0.14, anchor="middle") + "</g>")
        styles.append(keyframes(f"val{k}", P, [(0, "opacity:0"), (ta + .1, "opacity:0"), (ta + .35, "opacity:1"), (nxt, "opacity:1"), (nxt + .15, "opacity:0"), (P, "opacity:0")]))
        styles.append(anim(f"val{k}", f"val{k}", P))
    needle_frames += [(FADE, f"transform:rotate({signals[-1][3] * 1.8}deg)"), (P, "transform:rotate(0deg)")]

    visual = f"""
{grid}
<g mask="url(#sweep)">
  <path d="{area}" fill="url(#area)"/>
  {"".join(candles)}
  <path d="{line}" stroke="{AMBER}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
</g>
<g class="guide"><path d="M{x0} 0H{x1}" stroke="{AMBER}" stroke-opacity=".35" stroke-dasharray="3 4"/></g>
<g class="lead"><circle r="9" fill="{AMBER}" opacity=".22"/><circle r="3.6" fill="{AMBER}"/><circle r="1.6" fill="#fff"/></g>
{"".join(tags)}
{t.text("PRECIO · SEÑALES", x0, 82, 11, "mono", DIM, tracking=0.14)}
<path d="M424 80V214" stroke="{LINE}"/>
{t.text("SCORE", gx, 82, 11, "mono", DIM, tracking=0.18, anchor="middle")}
<path d="{arc(0, 100, r)}" stroke="{LINE2}" stroke-width="7" stroke-linecap="round"/>
<path d="{arc(0, 49.4, r + 8)}" stroke="{AMBER}" stroke-width="2.5"/>
<path d="{arc(50.6, 69.4, r + 8)}" stroke="{CYAN}" stroke-width="2.5"/>
<path d="{arc(70.6, 100, r + 8)}" stroke="{GREEN}" stroke-width="2.5"/>
<path d="{ticks}" stroke="{DIM}"/>
<g class="needle" style="transform-origin:{gx}px {gy}px;transform:rotate({82 * 1.8}deg)"><path d="M{gx} {gy}H{gx - r + 12}" stroke="{TEXT}" stroke-width="2.2" stroke-linecap="round"/></g>
<circle cx="{gx}" cy="{gy}" r="5" fill="{BG}" stroke="{TEXT}" stroke-width="2"/>
{"".join(readouts)}
"""
    style = f"""
{keyframes("sweep", P, sweep)}{anim("sweepr", "sweep", P)}
.sweepr{{transform-origin:{x0 - 4}px 0}}
{keyframes("lead", P, lead)}{anim("lead", "lead", P)}
.lead{{opacity:0}}
{keyframes("guide", P, guide)}{anim("guide", "guide", P)}
.guide{{opacity:0}}
{keyframes("needle", P, needle_frames)}{anim("needle", "needle", P, "cubic-bezier(.3,1.5,.5,1)")}
{"".join(styles)}"""
    defs = f"""<linearGradient id="area" x1="0" x2="0" y1="0" y2="1"><stop stop-color="{AMBER}" stop-opacity=".22"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>
<mask id="sweep" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="sweepr" x="{x0 - 4}" y="70" width="{x1 - x0 + 8}" height="150" fill="#fff"/></mask>"""
    aria = ("Tarjeta animada: una gráfica de velas se dibuja y emite señales BUY, HOLD y WATCH mientras un medidor "
            "de score multifactor se mueve. Stock Recommender: API en Go, frontend Vue 3 y despliegue en AWS con Terraform y Ansible.")
    return shell(t, 2, "STOCK RECOMMENDER", "Stock Recommender",
                 "Señales BUY · HOLD · WATCH con datos de mercado, en AWS.",
                 ["Go", "Vue 3", "TypeScript", "Terraform", "Ansible", "AWS"], AMBER, visual, style, defs, aria)


# EXP. 003 — Agentic RAG -----------------------------------------------------------
def rag():
    t, P = Type("r"), 8.0
    A = VIOLET
    styles = []

    def node(cx, cy, w, h, label, sub=None, cls=None):
        x, y = cx - w / 2, cy - h / 2
        glow = (f'<g class="{cls}" style="opacity:0"><rect x="{x - 3}" y="{y - 3}" width="{w + 6}" height="{h + 6}" rx="{h / 2 + 3}" fill="{A}" opacity=".35" filter="url(#glow)"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{A}" fill-opacity=".16" stroke="{A}" stroke-width="1.5"/></g>') if cls else ""
        text_y = cy + (0 if sub else 5)
        out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{PANEL}" stroke="{LINE2}"/>{glow}'
               + t.text(label, cx, text_y, 14, "monobold", TEXT, anchor="middle"))
        if sub:
            out += t.text(sub, cx, cy + 14, 9.5, "mono", DIM, anchor="middle")
        return out

    # Geometry
    start, end = (56, 162), (542, 162)
    agent, retrieve, generate = (178, 162), (178, 94), (412, 162)
    edges = {
        "e_start": [(65, 162), (124, 162)],
        "e_up": [(163, 140), (163, 114)],
        "e_down": [(193, 112), (193, 140)],
        "e_gen": [(232, 162), (350, 162)],
        "e_end": [(474, 162), (532, 162)],
    }
    edge_svg = (
        f'<path d="M65 162H122" stroke="{LINE2}" stroke-width="1.4"/>{arrow(124, 162, 0, MUTED)}'
        f'<path d="M163 140V116" stroke="{LINE2}" stroke-width="1.4" stroke-dasharray="4 3"/>{arrow(163, 114, -90, MUTED)}'
        f'<path d="M193 112V138" stroke="{LINE2}" stroke-width="1.4"/>{arrow(193, 140, 90, MUTED)}'
        f'<path d="M232 162H348" stroke="{LINE2}" stroke-width="1.4" stroke-dasharray="4 3"/>{arrow(350, 162, 0, MUTED)}'
        f'<path d="M474 162H530" stroke="{LINE2}" stroke-width="1.4"/>{arrow(532, 162, 0, MUTED)}')
    hot = "".join(f'<path class="{k}" d="M{a[0]} {a[1]}L{b[0]} {b[1]}" stroke="{A}" stroke-width="2" style="opacity:0"/>' for k, (a, b) in edges.items())

    timeline = {"e_start": (0.85, 1.2), "e_up": (1.75, 2.0), "e_down": (2.85, 3.1), "e_gen": (3.65, 4.1), "e_end": (4.85, 5.15)}
    legs = [(edges[k], *timeline[k]) for k in ("e_start", "e_up", "e_down", "e_gen", "e_end")]
    # One token, hidden while a node is "thinking": separate packets per leg keep it clean.
    packets = []
    for idx, (pts, t0, t1) in enumerate(legs):
        packets.append(packet(f"tok{idx}", P, A))
        styles.append(keyframes(f"tok{idx}", P, route(P, [(pts, t0, t1)], fade=.06)))
    for k, (t0, t1) in timeline.items():
        styles.append(keyframes(k, P, windows(P, [(t0, t1 + .1)], "opacity:0", "opacity:1", .08)) + anim(k, k, P))

    glows = {"g_agent": [(1.2, 1.75), (3.1, 3.65)], "g_retrieve": [(2.0, 2.85)], "g_generate": [(4.1, 4.85)]}
    for k, spans in glows.items():
        styles.append(keyframes(k, P, windows(P, spans, "opacity:0", "opacity:1", .12)) + anim(k, k, P))

    # BM25 store and fetched document
    store_x = 262
    store = "".join(f'<rect x="{store_x + i * 5}" y="{78 + i * 5}" width="34" height="26" rx="3" fill="{PANEL}" stroke="{LINE2}"/>' for i in range(3))
    store += "".join(f'<path d="M{store_x + 16} {94 + j * 5}h{18 - j * 4}" stroke="{DIM}"/>' for j in range(3))
    store += t.text("BM25", store_x + 24, 126, 10, "mono", DIM, tracking=0.12, anchor="middle")
    doc = (f'<g class="doc"><rect x="-8" y="-6" width="16" height="12" rx="2" fill="{A}" fill-opacity=".25" stroke="{A}"/>'
           f'<path d="M-4 -1h8M-4 2h5" stroke="{A}"/></g>')
    styles.append(keyframes("doc", P, route(P, [([(store_x + 8, 96), (236, 94)], 2.1, 2.55)], fade=.06)))
    styles.append(anim("doc", "doc", P) + ".doc{opacity:0}")
    styles.append(keyframes("storeflash", P, windows(P, [(2.0, 2.3)], "opacity:0", "opacity:1", .08)) + anim("storeflash", "storeflash", P))

    # Speech bubbles
    q_text = "Tell me about our guest 'Nikola Tesla'"
    q_w = t.width(q_text, 11, "mono") + t.width("HUMAN ", 11, "monobold") + 24
    question = (f'<g class="q"><rect x="34" y="196" width="{q_w:.1f}" height="24" rx="12" fill="{PANEL}" stroke="{LINE2}"/>'
                + t.text("HUMAN", 46, 212, 11, "monobold", A)
                + t.text(q_text, 46 + t.width("HUMAN ", 11, "monobold"), 212, 11, "mono", MUTED) + "</g>")
    bubble_x, bubble_y, bubble_w = 344, 72, 222
    answer = (f'<g class="ans"><rect x="{bubble_x}" y="{bubble_y}" width="{bubble_w}" height="54" rx="12" fill="{PANEL}" stroke="{A}" stroke-opacity=".6"/>'
              f'<path d="M{generate[0] - 8} {bubble_y + 54}l8 9 8-9" fill="{PANEL}" stroke="{A}" stroke-opacity=".6"/>'
              f'<path d="M{generate[0] - 7} {bubble_y + 53.5}h14" stroke="{PANEL}" stroke-width="2"/>'
              f'<g mask="url(#type1)">{t.text("«Nikola Tesla, bienvenido:", bubble_x + 14, bubble_y + 22, 11.5, "mono", TEXT)}</g>'
              f'<g mask="url(#type2)">{t.text(" la gala ya tiene corriente.»", bubble_x + 14, bubble_y + 40, 11.5, "mono", TEXT)}</g></g>')
    styles.append(keyframes("q", P, [(0, "opacity:0"), (.2, "opacity:0"), (.5, "opacity:1"), (7.3, "opacity:1"), (7.7, "opacity:0"), (P, "opacity:0")]) + anim("q", "q", P))
    styles.append(keyframes("ans", P, [(0, "opacity:0;transform:translateY(4px)"), (4.25, "opacity:0;transform:translateY(4px)"), (4.5, "opacity:1;transform:translateY(0)"),
                                       (7.3, "opacity:1;transform:translateY(0)"), (7.7, "opacity:0;transform:translateY(0)"), (P, "opacity:0")]) + anim("ans", "ans", P))
    for k, (a, b) in ((1, (4.5, 5.4)), (2, (5.4, 6.3))):
        styles.append(keyframes(f"type{k}", P, [(0, "transform:scaleX(0)"), (a, "transform:scaleX(0)"), (b, "transform:scaleX(1)"), (P, "transform:scaleX(1)")])
                      + f".type{k}{{transform-origin:{bubble_x + 10}px 0;animation:type{k} {P}s steps(26,end) infinite}}")

    end_ring = (f'<circle cx="{end[0]}" cy="{end[1]}" r="9" fill="{BG}" stroke="{MUTED}" stroke-width="1.4"/>'
                f'<circle cx="{end[0]}" cy="{end[1]}" r="4.5" fill="{MUTED}"/>'
                f'<circle class="g_end" cx="{end[0]}" cy="{end[1]}" r="9" stroke="{A}" stroke-width="2" style="opacity:0"/>')
    styles.append(keyframes("g_end", P, [(0, "opacity:0;transform:scale(1)"), (5.1, "opacity:0;transform:scale(1)"), (5.15, "opacity:1;transform:scale(1)"),
                                         (5.9, "opacity:0;transform:scale(2.6)"), (P, "opacity:0;transform:scale(1)")])
                  + f".g_end{{transform-box:fill-box;transform-origin:center;animation:g_end {P}s ease-out infinite}}")

    visual = f"""
{edge_svg}{hot}
<circle cx="{start[0]}" cy="{start[1]}" r="8" fill="{BG}" stroke="{MUTED}" stroke-width="1.4"/><circle cx="{start[0]}" cy="{start[1]}" r="3" fill="{MUTED}"/>
{t.text("START", start[0], 142, 10, "mono", DIM, tracking=0.12, anchor="middle")}
{t.text("END", end[0], 142, 10, "mono", DIM, tracking=0.12, anchor="middle")}
{end_ring}
{node(*agent, 106, 42, "agent", "gemini-2.0-flash", "g_agent")}
{node(*retrieve, 112, 38, "retrieve", None, "g_retrieve")}
{node(*generate, 120, 42, "generate", "respuesta final", "g_generate")}
{t.text("tools", 156, 131, 10, "mono", DIM, anchor="end")}
{t.text("tools_condition", 291, 154, 10, "mono", DIM, anchor="middle")}
<g>{store}<g class="storeflash" style="opacity:0"><rect x="{store_x + 10}" y="88" width="34" height="26" rx="3" stroke="{A}" stroke-width="1.5"/></g></g>
{doc}
{"".join(packets)}
{question}
{answer}
"""
    style = "".join(styles)
    defs = "".join(
        f'<mask id="type{k}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="type{k}" x="{bubble_x + 10}" y="{bubble_y + 8 + (k - 1) * 18}" width="{bubble_w - 16}" height="20" fill="#fff"/></mask>'
        for k in (1, 2))
    aria = ("Tarjeta animada del grafo de LangGraph: un token viaja de START a agent, consulta la herramienta retrieve "
            "(BM25), vuelve al agente, pasa a generate y termina en END mientras aparece la respuesta.")
    return shell(t, 3, "AGENTIC RAG", "Agentic RAG",
                 "Un agente que decide cuándo buscar contexto y cuándo responder.",
                 ["Python", "LangGraph", "Gemini", "BM25"], VIOLET, visual, style, defs, aria)


# EXP. 004 — API Gateway -----------------------------------------------------------
def gateway():
    t, P = Type("a"), 9.0
    A = CYAN
    styles = []
    services = ["/miembros", "/equipos", "/entrenadores", "/clases"]
    sy = [92, 126, 160, 194]
    gw = (216, 98, 300, 204)  # x0 y0 x1 y1
    lane = 151
    fan = [cubic((gw[2], lane), (360, lane), (362, y), (420, y), 16) for y in sy]

    def request(name, colour, svc, t0, size=1.0):
        legs = [([(98, lane), (138, lane)], t0, t0 + .3),
                ([(138, lane), (178, lane)], t0 + .5, t0 + .62),
                ([(178, lane), (gw[0], lane), (gw[2], lane)], t0 + .62, t0 + 1.0),
                (fan[svc], t0 + 1.0, t0 + 1.45)]
        styles.append(keyframes(name, P, route(P, legs)))
        return packet(name, P, colour, size)

    flows = {"m": (0, 0.3), "c": (3, 1.6), "e": (1, 4.1)}
    pkts = "".join(request(f"rq{k}", A, svc, t0) for k, (svc, t0) in flows.items())
    hits = {i: [] for i in range(4)}
    for svc, t0 in flows.values():
        hits[svc].append((t0 + 1.45, t0 + 1.9))
    jwt_ok = [(t0 + .3, t0 + .62) for _, t0 in flows.values()]

    # 401: token missing, bounced at the shield
    styles.append(keyframes("rq401", P, route(P, [([(98, lane), (136, lane)], 2.75, 3.05), ([(136, lane), (104, lane)], 3.2, 3.55)])))
    pkts += packet("rq401", P, ROSE)
    jwt_bad = [(3.05, 3.7)]

    # Aggregated request: one in, four out, four back, one out
    T = 5.2
    styles.append(keyframes("agg", P, route(P, [([(98, lane), (138, lane)], T, T + .3), ([(138, lane), (178, lane)], T + .5, T + .62),
                                                ([(178, lane), (gw[0], lane), (gw[2], lane)], T + .62, T + 1.0)])))
    pkts += packet("agg", P, VIOLET, 1.25)
    jwt_ok.append((T + .3, T + .62))
    for i in range(4):
        styles.append(keyframes(f"agg{i}", P, route(P, [(fan[i], T + 1.05, T + 1.5), (fan[i][::-1], T + 1.75, T + 2.2)])))
        pkts += packet(f"agg{i}", P, VIOLET, .8)
        hits[i].append((T + 1.5, T + 1.8))
    styles.append(keyframes("aggback", P, route(P, [([(gw[2], lane), (gw[0], lane), (98, lane)], T + 2.25, T + 2.85)])))
    pkts += packet("aggback", P, VIOLET, 1.25)

    for i, spans in hits.items():
        styles.append(keyframes(f"svc{i}", P, windows(P, spans, "opacity:0", "opacity:1", .1)) + anim(f"svc{i}", f"svc{i}", P))
    styles.append(keyframes("jok", P, windows(P, jwt_ok, "opacity:0", "opacity:1", .08)) + anim("jok", "jok", P))
    styles.append(keyframes("jbad", P, windows(P, jwt_bad, "opacity:0", "opacity:1", .08)) + anim("jbad", "jbad", P))
    styles.append(keyframes("aggrow", P, windows(P, [(T + .95, T + 2.3)], "opacity:0", "opacity:1", .1)) + anim("aggrow", "aggrow", P))
    styles.append(".beat{transform-box:fill-box;transform-origin:center;animation:beat 1.5s ease-out infinite}"
                  "@keyframes beat{0%{opacity:.9;transform:scale(1)}100%{opacity:0;transform:scale(2.6)}}")

    # Request log (bottom-left)
    log = [("GET /miembros", "200", GREEN, (.3, 2.0)), ("GET /clases", "200", GREEN, (1.6, 3.3)),
           ("GET /equipos  sin token", "401", ROSE, (2.75, 4.2)), ("GET /equipos", "200", GREEN, (4.1, 5.6)),
           ("GET /aggregated-info", "200", VIOLET, (5.2, 8.6))]
    log_svg = []
    for k, (req, code, colour, (a, b)) in enumerate(log):
        log_svg.append(f'<g class="log{k}" style="opacity:0">{t.text(req, 36, 219, 11, "mono", MUTED)}'
                       f'{t.text(code, 36 + t.width(req + "  ", 11, "mono"), 219, 11, "monobold", colour)}</g>')
        styles.append(keyframes(f"log{k}", P, [(0, "opacity:0"), (a, "opacity:0"), (a + .15, "opacity:1"), (b - .15, "opacity:1"), (b, "opacity:0"), (P, "opacity:0")])
                      + anim(f"log{k}", f"log{k}", P))

    svc_svg = []
    for i, (name, y) in enumerate(zip(services, sy)):
        svc_svg.append(
            f'<rect x="420" y="{y - 13}" width="146" height="26" rx="7" fill="{PANEL}" stroke="{LINE2}"/>'
            f'<g class="svc{i}" style="opacity:0"><rect x="420" y="{y - 13}" width="146" height="26" rx="7" fill="{A}" fill-opacity=".12" stroke="{A}"/></g>'
            + t.text(name, 431, y + 4.5, 12, "mono", TEXT)
            + f'<circle cx="554" cy="{y}" r="3" fill="{GREEN}"/><circle class="beat" cx="554" cy="{y}" r="3" stroke="{GREEN}" style="animation-delay:{-i * .37:.2f}s"/>')
    fan_svg = "".join(f'<path d="M{p[0][0]} {p[0][1]}C360 {lane} 362 {y} 418 {y}" stroke="{LINE2}" stroke-width="1.3"/>{arrow(420, y, 0, MUTED, 4.5)}'
                      for p, y in zip(fan, sy))

    shield = "M156 133l14 5v10c0 9-6 15-14 18c-8-3-14-9-14-18v-10z"
    visual = f"""
<rect x="36" y="137" width="62" height="28" rx="8" fill="{PANEL}" stroke="{LINE2}"/>
{t.text("CLIENTE", 67, 155, 10.5, "mono", TEXT, tracking=0.08, anchor="middle")}
<path d="M98 {lane}H142M170 {lane}H{gw[0]}" stroke="{LINE2}" stroke-width="1.3"/>
<path d="{shield}" fill="{PANEL}" stroke="{MUTED}" stroke-width="1.4"/>
<g class="jok" style="opacity:0"><path d="{shield}" fill="{GREEN}" fill-opacity=".15" stroke="{GREEN}" stroke-width="1.6"/><path d="M150 150l4.5 4.5 8-9" stroke="{GREEN}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>
<g class="jbad" style="opacity:0"><path d="{shield}" fill="{ROSE}" fill-opacity=".18" stroke="{ROSE}" stroke-width="1.6"/><path d="M151 145l10 10M161 145l-10 10" stroke="{ROSE}" stroke-width="2" stroke-linecap="round"/>{t.text("401", 156, 124, 11, "monobold", ROSE, anchor="middle")}</g>
{t.text("JWT", 156, 186, 10.5, "monobold", MUTED, tracking=0.12, anchor="middle")}
{t.text("keycloak", 156, 199, 10, "mono", DIM, anchor="middle")}
<rect x="{gw[0]}" y="{gw[1]}" width="{gw[2] - gw[0]}" height="{gw[3] - gw[1]}" rx="12" fill="{PANEL}" stroke="{A}" stroke-opacity=".5"/>
{t.text("GATEWAY", 258, 118, 11, "monobold", TEXT, tracking=0.12, anchor="middle")}
{t.text(":8089", 258, 132, 10, "mono", DIM, anchor="middle")}
<path d="M226 140H290" stroke="{LINE}"/>
{t.text("auth", 228, 168, 10, "mono", MUTED)}<path d="M259 164.5l2.5 2.5 5-5.5" stroke="{GREEN}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
{t.text("routes 4", 228, 182, 10, "mono", MUTED)}
<g class="aggrow" style="opacity:0"><rect x="222" y="186" width="72" height="14" rx="3" fill="{VIOLET}" fill-opacity=".2"/></g>
{t.text("aggregate", 228, 196, 10, "mono", MUTED)}
<rect x="222" y="70" width="72" height="18" rx="9" fill="{PANEL}" stroke="{LINE2}"/>
{t.text("EUREKA", 263, 83, 10, "monobold", MUTED, tracking=0.12, anchor="middle")}
<circle cx="233" cy="79" r="2.6" fill="{GREEN}"/><circle class="beat" cx="233" cy="79" r="2.6" stroke="{GREEN}"/>
<path d="M258 88V98" stroke="{DIM}" stroke-dasharray="2 2"/>
{t.text("lb://", 352, 108, 10, "mono", DIM, anchor="middle")}
{fan_svg}
{"".join(svc_svg)}
{pkts}
{"".join(log_svg)}
"""
    aria = ("Tarjeta animada: peticiones salen del cliente, pasan la validación JWT (una sin token recibe 401) y el "
            "gateway las enruta por Eureka a /miembros, /equipos, /entrenadores y /clases; una petición agregada se divide en cuatro y vuelve unida.")
    return shell(t, 4, "API GATEWAY", "API Gateway",
                 "Una sola puerta: valida JWT, descubre servicios y enruta.",
                 ["Java", "Spring Cloud Gateway", "Eureka", "Keycloak"], CYAN, visual, "".join(styles), "", aria)


# EXP. 005 — Multi-database App ------------------------------------------------------
def multidb():
    t, P = Type("d"), 9.0
    styles = []
    core = (300, 152)
    ring_r = 44

    # Postgres panel
    pg_x, pg_y = 38, 76
    rows = []
    rng = random.Random(3)
    for r in range(6):
        y = pg_y + 34 + r * 16
        header = r == 0
        for c, (cx, cw) in enumerate(((50, 22), (80, 58), (146, 38))):
            w = cw if header else cw * rng.uniform(.45, .95)
            rows.append(f'<rect x="{cx}" y="{y}" width="{w:.1f}" height="{5 if header else 4}" rx="2" fill="{BLUE if header else DIM}" fill-opacity="{.7 if header else .55}"/>')
    pg = (f'<rect x="{pg_x}" y="{pg_y}" width="158" height="140" rx="10" fill="{PANEL}" stroke="{LINE2}"/>'
          + t.text("POSTGRESQL", pg_x + 12, pg_y + 20, 10.5, "monobold", BLUE, tracking=0.12)
          + f'<path d="M{pg_x} {pg_y + 28}H{pg_x + 158}" stroke="{LINE}"/>'
          + "".join(rows)
          + f'<rect class="scan" x="{pg_x + 6}" y="{pg_y + 44}" width="146" height="12" rx="3" fill="{BLUE}" fill-opacity=".22" stroke="{BLUE}" stroke-opacity=".7" style="opacity:0"/>')
    styles.append(keyframes("scan", P, [(0, "opacity:0;transform:translateY(0)"), (1.5, "opacity:0;transform:translateY(0)"), (1.55, "opacity:1;transform:translateY(0)"),
                                        (2.3, "opacity:1;transform:translateY(64px)"), (2.35, "opacity:1;transform:translateY(32px)"),
                                        (2.75, "opacity:1;transform:translateY(32px)"), (2.95, "opacity:0;transform:translateY(32px)"), (P, "opacity:0")])
                  + anim("scan", "scan", P))

    # Mongo panel
    mg_x, mg_y = 404, 76
    doc_lines = [("{", MUTED), ("  _id: ObjectId(…),", MUTED), ('  name: "Alice",', TEXT), ('  curso: "SID",', TEXT), ("  activo: true", TEXT), ("}", MUTED)]
    mg = (f'<rect x="{mg_x}" y="{mg_y}" width="158" height="140" rx="10" fill="{PANEL}" stroke="{LINE2}"/>'
          + t.text("MONGODB", mg_x + 12, mg_y + 20, 10.5, "monobold", GREEN, tracking=0.12)
          + t.text("students", mg_x + 146, mg_y + 20, 10, "mono", DIM, anchor="end")
          + f'<path d="M{mg_x} {mg_y + 28}H{mg_x + 158}" stroke="{LINE}"/>')
    masks = []
    for k, (line, colour) in enumerate(doc_lines):
        y = mg_y + 46 + k * 15
        mg += t.text(line, mg_x + 12, y, 10.5, "mono", DIM, attrs='opacity=".45"')
        mg += f'<g mask="url(#ml{k})">{t.text(line, mg_x + 12, y, 10.5, "mono", colour)}</g>'
        masks.append(f'<mask id="ml{k}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect class="ml{k}" x="{mg_x + 8}" y="{y - 11}" width="146" height="15" fill="#fff"/></mask>')
        a = 6.55 + k * .17
        styles.append(keyframes(f"ml{k}", P, [(0, "transform:scaleX(0);opacity:1"), (a, "transform:scaleX(0);opacity:1"),
                                             (a + .16, "transform:scaleX(1);opacity:1"), (8.35, "transform:scaleX(1);opacity:1"), (8.8, "transform:scaleX(1);opacity:0"), (P, "transform:scaleX(1);opacity:0")])
                      + f".ml{k}{{transform-origin:{mg_x + 8}px 0;animation:ml{k} {P}s linear infinite}}")
    mg += f'<rect class="mgflash" x="{mg_x}" y="{mg_y}" width="158" height="140" rx="10" stroke="{GREEN}" stroke-width="1.5" style="opacity:0"/>'
    styles.append(keyframes("mgflash", P, windows(P, [(6.45, 6.8)], "opacity:0", "opacity:1", .1)) + anim("mgflash", "mgflash", P))

    # Core + Redis ring
    hexagon = " ".join(f"{core[0] + 27 * math.cos(math.radians(60 * i + 30)):.1f},{core[1] + 27 * math.sin(math.radians(60 * i + 30)):.1f}" for i in range(6))
    keys = "".join(f'<circle cx="{core[0] + ring_r * math.cos(math.radians(a)):.1f}" cy="{core[1] + ring_r * math.sin(math.radians(a)):.1f}" r="2.6" fill="{ROSE}"/>' for a in (20, 140, 260))
    newkey = f'<circle class="newkey" cx="{core[0] + ring_r * math.cos(math.radians(-60)):.1f}" cy="{core[1] + ring_r * math.sin(math.radians(-60)):.1f}" r="3.6" fill="#fff" stroke="{ROSE}" stroke-width="2"/>'
    styles.append(keyframes("newkey", P, [(0, "opacity:0"), (3.15, "opacity:0"), (3.3, "opacity:1"), (8.4, "opacity:1"), (8.8, "opacity:0"), (P, "opacity:0")]) + anim("newkey", "newkey", P))
    styles.append(f".orbit{{transform-origin:{core[0]}px {core[1]}px;animation:orbit 14s linear infinite}}@keyframes orbit{{to{{transform:rotate(360deg)}}}}")
    for k, spans, colour in (("ringmiss", [(.85, 1.25)], ROSE), ("ringset", [(3.05, 3.4)], ROSE), ("ringhit", [(4.95, 5.35)], GREEN)):
        styles.append(keyframes(k, P, windows(P, spans, "opacity:0", "opacity:1", .08)) + anim(k, k, P))

    # Labels that pop
    pops = [("MISS", ROSE, (.9, 2.0), 352, 112, "monobold"), ("HIT", GREEN, (5.0, 6.1), 352, 112, "monobold"),
            ("SET students · TTL 30s", ROSE, (3.1, 4.3), 300, 222, "mono"),
            ("200 · 1000 ms", MUTED, (3.8, 4.7), 364, 86, "mono"), ("200 · 2 ms", GREEN, (5.2, 6.4), 364, 86, "mono"),
            ("~1000 ms", BLUE, (1.6, 2.9), pg_x + 146, pg_y + 132, "mono")]
    pop_svg = []
    for k, (word, colour, (a, b), x, y, font) in enumerate(pops):
        anchor = "middle" if x == 300 else ("end" if x == pg_x + 146 else "start")
        pop_svg.append(f'<g class="pop{k}" style="opacity:0">{t.text(word, x, y, 11, font, colour, tracking=0.06, anchor=anchor)}</g>')
        styles.append(keyframes(f"pop{k}", P, [(0, "opacity:0;transform:translateY(4px)"), (a, "opacity:0;transform:translateY(4px)"), (a + .18, "opacity:1;transform:translateY(0)"),
                                              (b, "opacity:1;transform:translateY(0)"), (b + .2, "opacity:0;transform:translateY(0)"), (P, "opacity:0")])
                      + anim(f"pop{k}", f"pop{k}", P, "ease-out"))

    # Packets
    top, ring_top = (300, 92), (300, core[1] - ring_r)
    left_in, left_out = (core[0] - ring_r, core[1]), (pg_x + 158, core[1])
    right_in, right_out = (core[0] + ring_r, core[1]), (mg_x, core[1])
    flows = [
        ("q1", BLUE, [([top, ring_top], .4, .8)]),
        ("q2", BLUE, [([left_in, left_out], 1.05, 1.5)]),
        ("q3", BLUE, [([left_out, left_in], 2.55, 3.0)]),
        ("q4", BLUE, [([ring_top, top], 3.4, 3.8)]),
        ("h1", GREEN, [([top, ring_top], 4.75, 4.95), ([ring_top, top], 5.0, 5.2)]),
        ("w1", GREEN, [([right_in, right_out], 6.0, 6.45)]),
    ]
    pkts = ""
    for name, colour, legs in flows:
        styles.append(keyframes(name, P, route(P, legs, fade=.05)))
        pkts += packet(name, P, colour)
    styles.append(keyframes("chip", P, windows(P, [(.25, .55), (4.6, 4.85)], "opacity:0", "opacity:1", .1)) + anim("chip", "chip", P))

    chip_w = t.width("GET /students", 11, "mono") + 22
    visual = f"""
{pg}{mg}
<path d="M{pg_x + 158} {core[1]}H{core[0] - ring_r}M{core[0] + ring_r} {core[1]}H{mg_x}M300 92V{core[1] - ring_r}" stroke="{LINE2}" stroke-width="1.3" stroke-dasharray="3 3"/>
<rect x="{300 - chip_w / 2:.1f}" y="72" width="{chip_w:.1f}" height="20" rx="10" fill="{PANEL}" stroke="{LINE2}"/>
<rect class="chip" x="{300 - chip_w / 2:.1f}" y="72" width="{chip_w:.1f}" height="20" rx="10" stroke="{BLUE}" stroke-width="1.5" style="opacity:0"/>
{t.text("GET /students", 300, 86, 11, "mono", TEXT, anchor="middle")}
<circle cx="{core[0]}" cy="{core[1]}" r="{ring_r}" stroke="{ROSE}" stroke-opacity=".45" stroke-dasharray="2 5"/>
<g class="orbit">{keys}{newkey}</g>
<circle class="ringmiss" cx="{core[0]}" cy="{core[1]}" r="{ring_r}" stroke="{ROSE}" stroke-width="3" filter="url(#glow)" style="opacity:0"/>
<circle class="ringset" cx="{core[0]}" cy="{core[1]}" r="{ring_r}" stroke="{ROSE}" stroke-width="2" style="opacity:0"/>
<circle class="ringhit" cx="{core[0]}" cy="{core[1]}" r="{ring_r}" stroke="{GREEN}" stroke-width="3" filter="url(#glow)" style="opacity:0"/>
<polygon points="{hexagon}" fill="{PANEL}" stroke="{BLUE}" stroke-width="1.5"/>
{t.text("NestJS", core[0], core[1] + 4, 11.5, "monobold", TEXT, anchor="middle")}
{t.text("REDIS", core[0], 210, 10.5, "monobold", ROSE, tracking=0.14, anchor="middle")}
{pkts}
{"".join(pop_svg)}
"""
    aria = ("Tarjeta animada: GET /students falla en la caché Redis (MISS), consulta PostgreSQL en ~1000 ms, guarda la "
            "clave con TTL de 30 s; la siguiente petición es un HIT de 2 ms; luego un documento se escribe en MongoDB.")
    return shell(t, 5, "MULTI-DATABASE", "Multi-database App",
                 "PostgreSQL, MongoDB y Redis conviviendo en una sola app.",
                 ["TypeScript", "NestJS", "PostgreSQL", "MongoDB", "Redis"], BLUE, visual, "".join(styles), "".join(masks), aria)


def build():
    return {"exp-stock.svg": stock(), "exp-rag.svg": rag(), "exp-gateway.svg": gateway(), "exp-multidb.svg": multidb()}
