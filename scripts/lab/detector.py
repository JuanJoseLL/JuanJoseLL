"""Live detector: a year of GitHub activity drawn as a particle-physics event display.

Every day is a calorimeter tower around the ring (length = contributions).
The most intense days fire curved tracks from the collision vertex.
A GitHub Action re-runs this every day, so the README is never the same twice.
"""

import datetime as dt
import json
import math
import os
import subprocess
import urllib.request
from pathlib import Path

from .theme import (AMBER, CYAN, DIM, LINE, LINE2, MUTED, PANEL, ROSE, TEXT, VIOLET,
                    card, card_defs, corners, document, mix)
from .type import Type

USER = os.environ.get("PROFILE_USER", "JuanJoseLL")
W, H = 1200, 640
CX, CY = 322, 352
R_BASE, R_MAX, R_LABEL = 150, 238, 262
MONTHS = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
WEEKDAYS = ["L", "M", "X", "J", "V", "S", "D"]
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


# Data -----------------------------------------------------------------------------
def _token():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("Set GITHUB_TOKEN (or log in with gh) to measure the detector")


def fetch(login=USER):
    snapshot = os.environ.get("DETECTOR_SNAPSHOT")
    if snapshot:
        payload = json.loads(Path(snapshot).read_text())
    else:
        request = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
            headers={"Authorization": f"bearer {_token()}", "User-Agent": "jj-lab-detector"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    if payload.get("errors"):
        raise SystemExit(f"GitHub API: {payload['errors']}")
    calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [(dt.date.fromisoformat(d["date"]), d["contributionCount"])
            for week in calendar["weeks"] for d in week["contributionDays"]]
    return calendar["totalContributions"], days


def stats(days):
    counts = [n for _, n in days]
    longest = run = 0
    for n in counts:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts  # today may still be empty
    for n in reversed(tail):
        if not n:
            break
        current += 1
    peak = max(range(len(days)), key=lambda i: counts[i])
    weekdays = [0] * 7
    for day, n in days:
        weekdays[day.weekday()] += n
    nonzero = sorted(n for n in counts if n)
    quart = [nonzero[int(len(nonzero) * p)] for p in (.25, .5, .75)] if nonzero else [1, 2, 3]
    return {
        "active": len(nonzero), "longest": longest, "current": current,
        "peak": days[peak], "weekdays": weekdays, "quartiles": quart,
    }


# Drawing --------------------------------------------------------------------------
def polar(r, angle):
    a = math.radians(angle - 90)
    return CX + r * math.cos(a), CY + r * math.sin(a)


def level(n, quart):
    if n == 0:
        return 0
    return 1 + sum(n > q for q in quart)


COLOURS = {0: DIM, 1: "#3f8f8c", 2: CYAN, 3: VIOLET, 4: AMBER}


def fmt(n):
    return f"{n:,}".replace(",", " ")


def build(data=None):
    total, days = data or fetch()
    s = stats(days)
    t = Type("d")
    count = len(days)
    peak_n = s["peak"][1] or 1
    step = 360 / count

    # Towers --------------------------------------------------------------------
    towers, zero_ticks = [], []
    for i, (day, n) in enumerate(days):
        angle = i * step + step / 2
        x0, y0 = polar(R_BASE + 4, angle)
        if n == 0:
            x1, y1 = polar(R_BASE + 8, angle)
            zero_ticks.append(f"M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}")
            continue
        length = 10 + (R_MAX - R_BASE - 14) * math.sqrt(n / peak_n)
        x1, y1 = polar(R_BASE + 4 + length, angle)
        lv = level(n, s["quartiles"])
        colour = "#ffffff" if (day, n) == s["peak"] else COLOURS[lv]
        towers.append(
            f'<path class="tw" d="M{x0:.1f} {y0:.1f}L{x1:.1f} {y1:.1f}" stroke="{colour}" '
            f'style="--l:{length:.0f};animation-delay:{.3 + i / count * 1.8:.2f}s,{-12 + i / count * 12:.2f}s"/>')

    # Month ring ----------------------------------------------------------------
    month_marks, month_labels = [], []
    for i, (day, _) in enumerate(days):
        if day.day == 1:
            angle = i * step
            xa, ya = polar(R_BASE - 6, angle)
            xb, yb = polar(R_LABEL - 12, angle)
            month_marks.append(f"M{xa:.1f} {ya:.1f}L{xb:.1f} {yb:.1f}")
            lx, ly = polar(R_LABEL + 6, angle + 3.5)
            label = MONTHS[day.month - 1] + (f" {day.year % 100:02d}" if day.month == 1 else "")
            month_labels.append(t.text(label, lx, ly + 4, 11, "mono", MUTED, tracking=.12, anchor="middle"))

    # Tracks from the vertex to the most intense days --------------------------
    ranked = sorted(range(count), key=lambda i: -days[i][1])[:22]
    tracks = []
    for k, i in enumerate(sorted(ranked)):
        angle = i * step + step / 2
        ex, ey = polar(R_BASE - 12, angle)
        bend = (1 if k % 2 else -1) * (18 + (k * 7) % 26)
        mx, my = polar((R_BASE - 12) / 2, angle + bend)
        colour = CYAN if k % 2 else VIOLET
        tracks.append(
            f'<path class="trk" d="M{CX} {CY}Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke="{colour}" '
            f'style="animation-delay:{2 + (k * 0.53) % 6:.2f}s"/>')

    # Today marker ---------------------------------------------------------------
    today_angle = (count - 1) * step + step / 2
    tx, ty = polar(R_LABEL - 20, today_angle)
    hx, hy = polar(R_MAX + 2, today_angle)

    # Scan wedge -------------------------------------------------------------------
    wa, wb = polar(R_MAX + 6, -9), polar(R_MAX + 6, 0)
    wedge = f"M{CX} {CY}L{wa[0]:.1f} {wa[1]:.1f}A{R_MAX + 6} {R_MAX + 6} 0 0 1 {wb[0]:.1f} {wb[1]:.1f}Z"

    # Right panel --------------------------------------------------------------------
    px = 650
    big = fmt(total)
    big_d = t.outline(big, px - 4, 236, 124, "display", tracking=-0.04)
    big_w = t.width(big, 124, "display", -0.04)
    peak_day, peak_count = s["peak"]
    cells = [
        ("DÍAS ACTIVOS", str(s["active"]), f"de {count}"),
        ("RACHA MÁXIMA", str(s["longest"]), "días seguidos"),
        ("RACHA ACTUAL", str(s["current"]), "días" if s["current"] != 1 else "día"),
        ("DÍA PICO", str(peak_count), f"{peak_day.day:02d} {MONTHS[peak_day.month - 1]} {peak_day.year}"),
    ]
    grid = []
    for k, (label, value, unit) in enumerate(cells):
        gx, gy = px + (k % 2) * 256, 330 + (k // 2) * 84
        vw = t.width(value, 38, "display", -0.02)
        grid.append(
            f'<g class="rise" style="animation-delay:{1 + k * .12:.2f}s">'
            + t.text(label, gx, gy, 11, "mono", DIM, tracking=.16)
            + t.text(value, gx - 1, gy + 44, 38, "display", TEXT, tracking=-0.02)
            + t.text(unit, gx + vw + 10, gy + 44, 12, "mono", MUTED, tracking=.06)
            + "</g>")

    wmax = max(s["weekdays"]) or 1
    spectrum = []
    sx, sy, bar_w, gap, bar_h = px, 590, 44, 20, 62
    for k, value in enumerate(s["weekdays"]):
        h = max(3, value / wmax * bar_h)
        x = sx + k * (bar_w + gap)
        colour = mix(CYAN, VIOLET, k / 6)
        spectrum.append(
            f'<rect class="bar" x="{x}" y="{sy - h:.1f}" width="{bar_w}" height="{h:.1f}" rx="3" fill="{colour}" '
            f'fill-opacity="{.35 + .65 * value / wmax:.2f}" style="animation-delay:{1.4 + k * .08:.2f}s"/>'
            + t.text(WEEKDAYS[k], x + bar_w / 2, sy + 20, 11, "mono", MUTED, anchor="middle"))
    busiest = WEEKDAYS[s["weekdays"].index(wmax)]
    busiest_name = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADOS", "DOMINGOS"][s["weekdays"].index(wmax)]

    legend = []
    lx = px + 256
    for k, (lv, text) in enumerate([(1, "BAJA"), (2, "MEDIA"), (3, "ALTA"), (4, "MÁX")]):
        legend.append(f'<path d="M{lx + k * 62} 268h14" stroke="{COLOURS[lv]}" stroke-width="3" stroke-linecap="round"/>'
                      + t.text(text, lx + k * 62 + 20, 272, 10, "mono", DIM, tracking=.1))

    measured = days[-1][0]
    header = (t.text("JJ—LAB", 48, 47, 14, "monobold", TEXT, tracking=.16)
              + t.text("/  DETECTOR DE ACTIVIDAD  ·  ÚLTIMO AÑO", 48 + t.width("JJ—LAB", 14, "monobold", .16) + 14, 47, 14, "mono", MUTED, tracking=.16)
              + t.text(f"ÚLTIMA MEDICIÓN  {measured.isoformat()}", 1152, 47, 14, "mono", MUTED, tracking=.16, anchor="end"))
    live_x = 1152 - t.width(f"ÚLTIMA MEDICIÓN  {measured.isoformat()}", 14, "mono", .16) - 14

    style = f"""
.tw{{stroke-width:1.9;stroke-linecap:round;stroke-dasharray:var(--l) 400;animation:grow .9s cubic-bezier(.2,.8,.2,1) both,pass 12s linear infinite}}
@keyframes grow{{from{{stroke-dasharray:0 400}}}}
@keyframes pass{{0%{{opacity:1}}4%{{opacity:.55}}100%{{opacity:1}}}}
.zero{{animation:fade 1s ease .3s both}}
.trk{{fill:none;stroke-width:1.3;stroke-dasharray:240;stroke-dashoffset:240;opacity:0;animation:track 6.4s cubic-bezier(.3,.6,.2,1) infinite}}
@keyframes track{{0%{{stroke-dashoffset:240;opacity:0}}3%{{opacity:.95}}14%{{stroke-dashoffset:0;opacity:.8}}34%{{stroke-dashoffset:0;opacity:0}}100%{{stroke-dashoffset:0;opacity:0}}}}
.sweep{{transform-origin:{CX}px {CY}px;animation:spin 12s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.vertex{{transform-box:fill-box;transform-origin:center;animation:vertex 3.2s ease-out infinite}}
@keyframes vertex{{0%{{transform:scale(.6);opacity:1}}60%,100%{{transform:scale(2.6);opacity:0}}}}
.today{{animation:today 1.6s ease-in-out infinite}}
@keyframes today{{50%{{opacity:.25}}}}
.blink{{animation:blink 1.6s steps(2,end) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.rise{{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(14px)}}}}
.fade{{animation:fade 1s ease both}}
@keyframes fade{{from{{opacity:0}}}}
.bar{{transform-box:fill-box;transform-origin:bottom;animation:bar .8s cubic-bezier(.2,.8,.2,1) both}}
@keyframes bar{{from{{transform:scaleY(0)}}}}
.orbit{{transform-origin:{CX}px {CY}px;animation:spin 40s linear infinite}}
.orbit2{{transform-origin:{CX}px {CY}px;animation:spin 28s linear infinite reverse}}
"""

    defs = f"""{card_defs(W, H)}
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{px}" x2="{px + big_w}"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#cdd5f7"/></linearGradient>
<linearGradient id="underline" x2="1"><stop stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="wedge" gradientUnits="userSpaceOnUse" x1="{wa[0]:.0f}" y1="{wa[1]:.0f}" x2="{wb[0]:.0f}" y2="{wb[1]:.0f}"><stop stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".22"/></linearGradient>
<radialGradient id="core"><stop stop-color="#fff"/><stop offset=".25" stop-color="{CYAN}" stop-opacity=".8"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="halo"><stop stop-color="{VIOLET}" stop-opacity=".14"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>"""

    ring_ticks = "".join(
        f"M{polar(R_BASE - 2, a)[0]:.1f} {polar(R_BASE - 2, a)[1]:.1f}L{polar(R_BASE - (6 if a % 30 == 0 else 3), a)[0]:.1f} {polar(R_BASE - (6 if a % 30 == 0 else 3), a)[1]:.1f}"
        for a in range(0, 360, 5))

    body = f"""{card(W, H)}
<circle cx="{CX}" cy="{CY}" r="300" fill="url(#halo)"/>
<g class="fade">{header}</g>
<circle class="blink" cx="{live_x:.1f}" cy="42.5" r="4" fill="{CYAN}"/>
<path d="M48 76H1152" stroke="{LINE}"/>

<g class="fade">
  <circle cx="{CX}" cy="{CY}" r="{R_LABEL - 12}" stroke="{LINE}" fill="none"/>
  <circle cx="{CX}" cy="{CY}" r="{R_BASE}" stroke="{LINE2}" fill="none"/>
  <circle cx="{CX}" cy="{CY}" r="{R_BASE - 34}" stroke="{LINE}" fill="none" stroke-dasharray="2 6"/>
  <circle cx="{CX}" cy="{CY}" r="{R_BASE - 76}" stroke="{LINE}" fill="none" stroke-dasharray="2 6"/>
  <circle cx="{CX}" cy="{CY}" r="20" stroke="{LINE2}" fill="{PANEL}"/>
  <path d="{ring_ticks}" stroke="{DIM}"/>
  <path d="{"".join(month_marks)}" stroke="{LINE2}"/>
  {"".join(month_labels)}
</g>
<g class="orbit"><circle cx="{CX + R_BASE - 34}" cy="{CY}" r="2" fill="{VIOLET}"/></g>
<g class="orbit2"><circle cx="{CX - R_BASE + 76}" cy="{CY}" r="2" fill="{CYAN}"/></g>
<path class="sweep" d="{wedge}" fill="url(#wedge)"/>
<path class="zero" d="{"".join(zero_ticks)}" stroke="{DIM}" stroke-opacity=".6" stroke-width="1.2"/>
<g>{"".join(towers)}</g>
<g>{"".join(tracks)}</g>
<circle class="vertex" cx="{CX}" cy="{CY}" r="16" fill="url(#core)"/>
<circle cx="{CX}" cy="{CY}" r="4" fill="#fff"/>
<g class="today"><path d="M{tx:.1f} {ty:.1f}L{hx:.1f} {hy:.1f}" stroke="{ROSE}" stroke-width="1.5"/><circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.5" fill="{ROSE}"/></g>
{t.text("HOY", tx + 9, ty + 4, 10, "monobold", ROSE, tracking=.12)}
{corners(CX - 270, CY - 268, CX + 270, CY + 270, size=12)}

<path d="M{px - 26} 104V604" stroke="{LINE}"/>
<g class="rise" style="animation-delay:.5s">
  {t.text("CONTRIBUCIONES  ·  ÚLTIMO AÑO", px, 118, 12, "mono", DIM, tracking=.16)}
  <path d="{big_d}" fill="url(#ink)"/>
  <rect x="{px}" y="252" width="{big_w:.0f}" height="3" rx="1.5" fill="url(#underline)"/>
  {"".join(legend)}
</g>
<g class="rise" style="animation-delay:.8s">{t.text("Cada línea es un día; cada partícula, una idea que llegó a un repo.", px, 302, 21, "serif", MUTED)}</g>
{"".join(grid)}
<g class="fade" style="animation-delay:1.3s">{t.text("ESPECTRO SEMANAL", px, 504, 11, "mono", DIM, tracking=.16)}{t.text(f"MÁS ACTIVO: {busiest_name}", 1152, 504, 11, "mono", CYAN, tracking=.12, anchor="end")}</g>
{"".join(spectrum)}
"""
    title = f"Detector de actividad — {fmt(total)} contribuciones en el último año"
    desc = (f"Visualización tipo detector de partículas generada a diario desde GitHub: cada día del "
            f"último año es una torre alrededor del anillo. {s['active']} días activos, racha máxima de "
            f"{s['longest']} días, día pico con {peak_count} contribuciones. Última medición {measured.isoformat()}.")
    return {"detector.svg": document(W, H, title, desc, body, style, defs, t)}
