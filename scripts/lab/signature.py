"""Closing pieces: the footer transmission, the Schrödinger easter egg and the
two contact buttons used under the hero."""

import math

from .theme import (AMBER, CYAN, DIM, LINE, LINE2, MUTED, PANEL, ROSE, TEXT, VIOLET,
                    card, card_defs, corners, document)
from .type import Type


def check(x, y, size=1.0, colour=CYAN, width=2.6):
    s = size
    return (f'<path d="M{x} {y - 7 * s:.1f}l{6 * s:.1f} {6 * s:.1f}l{11 * s:.1f} {-13 * s:.1f}" stroke="{colour}" '
            f'stroke-width="{width}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def cross(x, y, size=1.0, colour=ROSE, width=2.6):
    s = size
    return (f'<path d="M{x} {y - 14 * s:.1f}l{13 * s:.1f} {13 * s:.1f}M{x + 13 * s:.1f} {y - 14 * s:.1f}l{-13 * s:.1f} {13 * s:.1f}" '
            f'stroke="{colour}" stroke-width="{width}" fill="none" stroke-linecap="round"/>')


def subpaths(d):
    parts, current = [], ""
    for chunk in d.split("M")[1:]:
        current = "M" + chunk
        parts.append(current)
    return parts


# FOOTER -------------------------------------------------------------------------
def footer():
    W, H = 1200, 240
    t = Type("f")
    cx, cy, half = 812, 128, 262

    def packet(phase, amp, sigma, k):
        pts = []
        for i in range(0, 2 * half + 1, 4):
            x = cx - half + i
            u = (x - cx) / sigma
            y = cy + amp * math.exp(-u * u) * math.sin(k * (x - cx) - phase)
            pts.append(f"{x} {y:.1f}")
        return "M" + "L".join(pts)

    def animated(amp, sigma, k, dur, stroke, width, opacity, reverse=False):
        frames = [packet((-1 if reverse else 1) * 2 * math.pi * f / 12, amp, sigma, k) for f in range(13)]
        return (f'<path d="{frames[0]}" stroke="{stroke}" stroke-width="{width}" stroke-opacity="{opacity}" fill="none" '
                f'stroke-linejoin="round"><animate attributeName="d" dur="{dur}s" repeatCount="indefinite" '
                f'values="{";".join(frames)}"/></path>')

    waves = (animated(40, 120, .14, 1.4, CYAN, 2, .95)
             + animated(30, 140, .11, 1.9, VIOLET, 1.6, .7, reverse=True)
             + animated(18, 90, .2, 1.1, "#ffffff", 1, .35))

    sig = t.outline_glyphs("Juan José", 54, 168, 86, "serif")
    fills, traces = [], []
    for i, (d, _, _) in enumerate(sig):
        delay = .3 + i * .17
        fills.append(f'<path class="sigfill" style="animation-delay:{delay + 1.05:.2f}s" d="{d}"/>')
        traces.extend(f'<path class="trace" style="animation-delay:{delay:.2f}s" d="{p}" pathLength="1000"/>' for p in subpaths(d))

    ticks = "".join(f"M{cx - half + i * half / 8:.0f} {cy + 58}v{6 if i % 4 == 0 else 3}" for i in range(17))
    tagline = "LA CURIOSIDAD SIGUE EN LÍNEA"
    tag_w = t.width(tagline, 13, "mono", .2)
    body = f"""{card(W, H)}
{t.text("FIN DE LA TRANSMISIÓN", 48, 46, 14, "monobold", TEXT, tracking=.2)}
{t.text("JJ—LAB  ·  2026", 1152, 46, 14, "mono", DIM, tracking=.16, anchor="end")}
<path d="M48 72H1152" stroke="{LINE}"/>
<ellipse cx="{cx}" cy="{cy}" rx="300" ry="90" fill="url(#aura)"/>
<path d="M{cx - half} {cy + 58}H{cx + half}{ticks}" stroke="{LINE2}"/>
{t.text("ψ(x, t)", cx - half - 14, cy + 4, 12, "mono", DIM, anchor="end")}
{t.text("|ψ|² → δ(x)", cx + half + 14, cy + 4, 12, "mono", DIM)}
<g class="packet"><g class="squeeze">{waves}</g></g>
<g class="ripple-set">
  <circle class="ripple" cx="{cx}" cy="{cy}" r="6" stroke="{CYAN}"/>
  <circle class="ripple" cx="{cx}" cy="{cy}" r="6" stroke="{VIOLET}" style="animation-delay:1.3s"/>
</g>
<g class="point">
  <rect x="{cx - half}" y="{cy - .75}" width="{2 * half}" height="1.5" fill="url(#flare)"/>
  <circle cx="{cx}" cy="{cy}" r="30" fill="url(#pointglow)" class="breathe"/>
  <circle cx="{cx}" cy="{cy}" r="4.5" fill="#fff"/>
</g>
<circle class="blink" cx="{cx - tag_w / 2 - 14:.1f}" cy="{H - 33}" r="4" fill="{CYAN}"/>
{t.text(tagline, cx, H - 28, 13, "mono", MUTED, tracking=.2, anchor="middle")}
<g fill="url(#sigink)">{"".join(fills)}</g>
<g fill="none" stroke="{CYAN}" stroke-width="1.1" stroke-linejoin="round">{"".join(traces)}</g>
{t.text("SOFTWARE DEVELOPER  ·  QUANTUM / HUMAN", 58, H - 28, 12, "mono", DIM, tracking=.14)}
"""
    style = """
.trace{stroke-dasharray:1000;stroke-opacity:0;animation:trace 1.7s cubic-bezier(.5,0,.3,1) both}
@keyframes trace{0%{stroke-dashoffset:1000;stroke-opacity:1}70%{stroke-dashoffset:0;stroke-opacity:1}100%{stroke-dashoffset:0;stroke-opacity:0}}
.sigfill{animation:sigfill .9s ease both}
@keyframes sigfill{from{fill-opacity:0}}
.packet{opacity:0;animation:packet 11s ease infinite}
@keyframes packet{0%{opacity:0}6%,52%{opacity:1}60%,100%{opacity:0}}
.squeeze{transform-box:fill-box;transform-origin:center;animation:squeeze 11s cubic-bezier(.7,0,.3,1) infinite}
@keyframes squeeze{0%,48%{transform:scale(1,1)}60%,100%{transform:scale(.015,1.7)}}
.point{animation:point 11s ease infinite}
@keyframes point{0%,56%{opacity:0;transform:scale(1)}60%{opacity:1}94%{opacity:1}100%{opacity:0}}
.ripple-set{animation:point 11s ease infinite}
.ripple{fill:none;stroke-width:1;transform-box:fill-box;transform-origin:center;opacity:0;animation:ripple 2.6s ease-out infinite}
@keyframes ripple{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(9)}}
.breathe{transform-box:fill-box;transform-origin:center;animation:breathe 2.6s ease-in-out infinite}
@keyframes breathe{50%{transform:scale(1.35);opacity:.6}}
.blink{animation:blink 1.6s steps(2,end) infinite}
@keyframes blink{50%{opacity:0}}
"""
    defs = f"""{card_defs(W, H)}
<radialGradient id="aura"><stop stop-color="{VIOLET}" stop-opacity=".14"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<radialGradient id="pointglow"><stop stop-color="#fff" stop-opacity=".9"/><stop offset=".25" stop-color="{CYAN}" stop-opacity=".55"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<linearGradient id="flare"><stop stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN}" stop-opacity=".7"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
<linearGradient id="sigink" gradientUnits="userSpaceOnUse" x1="54" x2="420" y1="0" y2="0"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#d9d2ff"/></linearGradient>"""
    title = "Fin de la transmisión — la curiosidad sigue en línea"
    desc = ("Una firma de Juan José que se traza a mano y un paquete de ondas que colapsa en un solo "
            "punto de luz que sigue latiendo.")
    return document(W, H, title, desc, body, style, defs, t)


# SCHRÖDINGER --------------------------------------------------------------------
def collapse():
    W, H = 1200, 420
    t = Type("x")
    bx0, by0, bx1, by1 = 48, 112, 588, 380

    header = (
        t.text("JJ—LAB", 48, 46, 14, "monobold", TEXT, tracking=.16)
        + t.text("/  EXP. ∞  ·  LA CAJA DE SCHRÖDINGER", 48 + t.width("JJ—LAB", 14, "monobold", .16) + 14, 46, 14, "mono", MUTED, tracking=.16)
        + t.text("NO ABRIR EN PRODUCCIÓN", 1152, 46, 14, "mono", ROSE, tracking=.16, anchor="end")
    )
    warn_x = 1152 - t.width("NO ABRIR EN PRODUCCIÓN", 14, "mono", .16) - 14

    passing = check(78, 246, 1.25) + t.text("TESTS PASSING", 112, 248, 30, "monobold", CYAN, tracking=.02)
    failing = cross(80, 248, 1.15) + t.text("TESTS FAILING", 112, 248, 30, "monobold", ROSE, tracking=.02)
    done = (check(78, 246, 1.25) + t.text("42 passing", 112, 248, 30, "monobold", CYAN, tracking=.02)
            + t.text("(1.3s)", 112 + t.width("42 passing", 30, "monobold", .02) + 14, 248, 15, "mono", DIM))
    cat_x, cat_y = 512, by0
    cat = f"""<g class="cat">
  <path d="M{cat_x - 22} {cat_y + 12}C{cat_x - 24} {cat_y - 4} {cat_x - 20} {cat_y - 14} {cat_x - 16} {cat_y - 18}L{cat_x - 14} {cat_y - 34}L{cat_x - 4} {cat_y - 22}
    C{cat_x} {cat_y - 23} {cat_x + 4} {cat_y - 23} {cat_x + 8} {cat_y - 22}L{cat_x + 18} {cat_y - 34}L{cat_x + 20} {cat_y - 18}
    C{cat_x + 24} {cat_y - 14} {cat_x + 28} {cat_y - 4} {cat_x + 26} {cat_y + 12}Z" fill="#0c1120" stroke="{MUTED}" stroke-width="1.4" stroke-linejoin="round"/>
  <g class="eyes" fill="{CYAN}"><ellipse cx="{cat_x - 7}" cy="{cat_y - 8}" rx="2.6" ry="3.4"/><ellipse cx="{cat_x + 11}" cy="{cat_y - 8}" rx="2.6" ry="3.4"/></g>
  <path d="M{cat_x + 1} {cat_y - 2}l1.5 1.5l1.5 -1.5" stroke="{MUTED}" stroke-width="1.2" fill="none" stroke-linecap="round"/>
  <path d="M{cat_x - 14} {cat_y - 1}h-12M{cat_x - 14} {cat_y + 3}l-11 3M{cat_x + 18} {cat_y - 1}h12M{cat_x + 18} {cat_y + 3}l11 3" stroke="{DIM}" stroke-width="1"/>
</g>"""

    rx = 640
    f1, f2, f3, f4 = "|código⟩ = ", "α|funciona⟩", " + ", "β|no funciona⟩"
    xs = [rx]
    for part in (f1, f2, f3):
        xs.append(xs[-1] + t.width(part, 18, "mono"))
    formula = (t.text(f1, xs[0], 194, 18, "mono", TEXT) + t.text(f2, xs[1], 194, 18, "mono", CYAN)
               + t.text(f3, xs[2], 194, 18, "mono", TEXT) + t.text(f4, xs[3], 194, 18, "mono", ROSE))
    lines = ["Mi código estaba funcionando", "y roto a la vez… hasta que", "alguien corrió los tests."]
    quote = "".join(t.text(line, rx, 252 + i * 38, 33, "serif", TEXT) for i, line in enumerate(lines))
    bar_x, bar_w = 790, 250

    def bar(y, label, colour, cls):
        return (t.text(label, rx, y + 5, 12, "mono", DIM, tracking=.1)
                + f'<rect x="{bar_x}" y="{y - 3}" width="{bar_w}" height="6" rx="3" fill="{LINE2}"/>'
                + f'<rect class="{cls}" x="{bar_x}" y="{y - 3}" width="{bar_w}" height="6" rx="3" fill="{colour}"/>')

    probability = (bar(358, "P(funciona)", CYAN, "pa") + bar(384, "P(se rompe)", ROSE, "pb")
                   + f'<g class="sup">{t.text("≈ 50%", bar_x + bar_w + 16, 363, 12, "mono", AMBER)}{t.text("≈ 50%", bar_x + bar_w + 16, 389, 12, "mono", AMBER)}</g>'
                   + f'<g class="col">{t.text("100%", bar_x + bar_w + 16, 363, 12, "mono", CYAN)}{t.text("0%", bar_x + bar_w + 16, 389, 12, "mono", DIM)}</g>')

    chip_w = 92
    chip = lambda text, colour: (f'<rect x="{bx1 - chip_w - 14}" y="{by0 + 9}" width="{chip_w}" height="22" rx="11" fill="none" stroke="{colour}" stroke-opacity=".6"/>'
                                 + t.text(text, bx1 - 14 - chip_w / 2, by0 + 24, 11, "monobold", colour, tracking=.14, anchor="middle"))
    body = f"""{card(W, H)}
{header}
<circle class="blink" cx="{warn_x:.1f}" cy="41.5" r="4" fill="{ROSE}"/>
<path d="M48 72H1152" stroke="{LINE}"/>
{cat}
<rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" rx="14" fill="{PANEL}" stroke="{LINE2}"/>
<path d="M{bx0} {by0 + 40}H{bx1}" stroke="{LINE}"/>
<circle cx="{bx0 + 22}" cy="{by0 + 20}" r="4.5" fill="{ROSE}" fill-opacity=".8"/><circle cx="{bx0 + 38}" cy="{by0 + 20}" r="4.5" fill="{AMBER}" fill-opacity=".8"/><circle cx="{bx0 + 54}" cy="{by0 + 20}" r="4.5" fill="{CYAN}" fill-opacity=".8"/>
{t.text("caja.test.ts", (bx0 + bx1) / 2, by0 + 25, 13, "mono", DIM, anchor="middle")}
<g class="sup">{chip("SELLADA", AMBER)}</g><g class="col">{chip("ABIERTA", CYAN)}</g>
{t.text("$", 76, 192, 16, "monobold", CYAN)}{t.text("npm test -- --observe", 96, 192, 16, "mono", TEXT)}
<g class="sup">
  <g class="flipA">{passing}</g>
  <g class="flipB">{failing}</g>
  {t.text("estado: superposición  |ψ⟩", 78, 290, 15, "mono", AMBER)}
</g>
<g class="col">
  {done}
  {t.text("0 failing  ·  estado: colapsado", 78, 290, 15, "mono", MUTED)}
</g>
{t.text("$", 76, 344, 16, "monobold", CYAN)}<rect class="cursor" x="96" y="330" width="10" height="18" fill="{CYAN}"/>
<g class="scan">
  <rect x="{bx0 + 1}" y="{by0 + 41}" width="{bx1 - bx0 - 2}" height="26" fill="url(#scanfade)"/>
  <path d="M{bx0 + 1} {by0 + 67}H{bx1 - 1}" stroke="{CYAN}" stroke-width="1.5"/>
</g>
{corners(rx - 16, 112, 1168, 404, size=8, color=LINE2)}
{t.text("FUNCIÓN DE ONDA DEL CÓDIGO", rx, 150, 12, "mono", DIM, tracking=.16)}
{formula}
{quote}
{probability}
"""
    style = f"""
.sup{{opacity:0;animation:sup 10s ease infinite}}
@keyframes sup{{0%{{opacity:0}}3%,34%{{opacity:1}}37%,100%{{opacity:0}}}}
.col{{animation:col 10s cubic-bezier(.2,.8,.2,1) infinite}}
@keyframes col{{0%,41%{{opacity:0;transform:translateY(8px)}}46%,90%{{opacity:1;transform:none}}96%,100%{{opacity:0}}}}
.flipA{{animation:flipA 1.3s step-end infinite}}
@keyframes flipA{{0%{{opacity:1;transform:none}}22%{{opacity:0}}31%{{opacity:.8;transform:translate(-4px,1px)}}36%{{opacity:1;transform:none}}58%{{opacity:0}}80%{{opacity:1;transform:translateX(3px)}}86%{{transform:none}}}}
.flipB{{opacity:0;animation:flipB 1.3s step-end infinite}}
@keyframes flipB{{0%{{opacity:0}}22%{{opacity:1;transform:none}}31%{{opacity:.75;transform:translate(5px,-1px)}}36%{{opacity:0}}58%{{opacity:1;transform:translateX(-3px)}}64%{{transform:none}}80%{{opacity:0}}}}
.scan{{opacity:0;animation:scan 10s cubic-bezier(.6,0,.4,1) infinite}}
@keyframes scan{{0%,33%{{opacity:0;transform:translateY(0)}}34%{{opacity:1;transform:translateY(0)}}43%{{opacity:1;transform:translateY({by1 - by0 - 70}px)}}45%,100%{{opacity:0;transform:translateY({by1 - by0 - 70}px)}}}}
.cat{{animation:cat 10s cubic-bezier(.3,1.4,.5,1) infinite}}
@keyframes cat{{0%,49%{{transform:translateY(40px)}}55%,86%{{transform:none}}92%,100%{{transform:translateY(40px)}}}}
.eyes{{transform-box:fill-box;transform-origin:center;animation:eyes 3.2s ease infinite}}
@keyframes eyes{{0%,90%,100%{{transform:scaleY(1)}}94%{{transform:scaleY(.1)}}}}
.pa{{transform-box:fill-box;transform-origin:left;animation:pa 10s ease-in-out infinite}}
@keyframes pa{{0%{{transform:scaleX(.5)}}9%{{transform:scaleX(.63)}}17%{{transform:scaleX(.4)}}26%{{transform:scaleX(.58)}}34%{{transform:scaleX(.5)}}44%,90%{{transform:scaleX(1)}}100%{{transform:scaleX(.5)}}}}
.pb{{transform:scaleX(0);transform-box:fill-box;transform-origin:left;animation:pb 10s ease-in-out infinite}}
@keyframes pb{{0%{{transform:scaleX(.5)}}9%{{transform:scaleX(.37)}}17%{{transform:scaleX(.6)}}26%{{transform:scaleX(.42)}}34%{{transform:scaleX(.5)}}44%,90%{{transform:scaleX(0)}}100%{{transform:scaleX(.5)}}}}
.cursor{{animation:blink 1.1s steps(2,end) infinite}}
.blink{{animation:blink 1.6s steps(2,end) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
"""
    defs = f"""{card_defs(W, H)}
<linearGradient id="scanfade" x1="0" x2="0" y1="0" y2="1"><stop stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".22"/></linearGradient>"""
    title = "La caja de Schrödinger del código"
    desc = ("Easter egg: una terminal en superposición muestra a la vez TESTS PASSING y TESTS FAILING; "
            "al observarla colapsa en 42 passing y un gato se asoma. Mi código estaba funcionando y "
            "roto a la vez… hasta que alguien corrió los tests.")
    return document(W, H, title, desc, body, style, defs, t)


# BUTTONS ------------------------------------------------------------------------
def button(word, voice, icon, prefix, accent):
    W, H = 340, 64
    t = Type(prefix)
    pill = "M32 1H308A31 31 0 0 1 308 63H32A31 31 0 0 1 32 1Z"
    word_w = t.width(word, 21, "display", -.005)
    assert 60 + word_w + 8 + t.width(voice, 23, "serif") < 286, word
    body = f"""<path d="{pill}" fill="url(#pillbg)"/>
<path d="{pill}" stroke="#2c3658"/>
<path class="comet" d="{pill}" pathLength="100" stroke="url(#comet)" stroke-width="1.6" stroke-linecap="round"/>
<path class="comet late" d="{pill}" pathLength="100" stroke="url(#comet)" stroke-width="1.2" stroke-linecap="round" opacity=".45"/>
<circle cx="34" cy="32" r="16" fill="#0d1324" stroke="{LINE2}"/>
{icon}
{t.text(word, 60, 39.5, 21, "display", TEXT, tracking=-.005)}
{t.text(voice, 60 + word_w + 8, 40, 23, "serif", MUTED)}
<circle cx="306" cy="32" r="17" fill="#0d1324" stroke="{LINE2}"/>
<path class="nudge" d="M300 38L311.5 26.5M303.5 26H312V34.5" stroke="{TEXT}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>"""
    style = f"""
.comet{{stroke-dasharray:14 86;animation:comet 6s linear infinite}}
.comet.late{{animation-delay:-3s}}
@keyframes comet{{to{{stroke-dashoffset:-100}}}}
.nudge{{animation:nudge 2.4s ease-in-out infinite}}
@keyframes nudge{{50%{{transform:translate(1.5px,-1.5px)}}}}
.ring{{fill:none;transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out infinite}}
@keyframes ring{{0%{{opacity:.9;transform:scale(1)}}100%{{opacity:0;transform:scale(3.2)}}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite}}
@keyframes pulse{{50%{{opacity:.45}}}}
"""
    defs = f"""<linearGradient id="pillbg" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#141b30"/><stop offset="1" stop-color="#0a0e1a"/></linearGradient>
<linearGradient id="comet" gradientUnits="userSpaceOnUse" x1="0" x2="{W}"><stop stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>"""
    return document(W, H, f"{word} {voice}", f"Botón: {word} — {voice}", body, style, defs, t)


def build():
    linkedin_icon = (f'<circle class="ring" cx="34" cy="32" r="4.5" stroke="{CYAN}"/>'
                     f'<circle class="pulse" cx="34" cy="32" r="4.5" fill="{CYAN}"/>')
    repos_icon = (f'<path d="M29 24.5V39.5M29 34C29 29 39 32 39 27" stroke="{VIOLET}" stroke-width="1.7" fill="none" stroke-linecap="round"/>'
                  f'<circle cx="29" cy="24.5" r="2.6" fill="{VIOLET}"/><circle cx="29" cy="39.5" r="2.6" fill="{VIOLET}"/>'
                  f'<circle class="pulse" cx="39" cy="26" r="2.6" fill="{CYAN}"/>')
    return {
        "footer.svg": footer(),
        "collapse.svg": collapse(),
        "btn-linkedin.svg": button("LinkedIn", "hablemos", linkedin_icon, "l", CYAN),
        "btn-repos.svg": button("Repositorios", "explora", repos_icon, "r", VIOLET),
    }
