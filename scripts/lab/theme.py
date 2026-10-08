"""Shared palette, texture and document shell for every lab asset."""

BG = "#05070d"
PANEL = "#0a0e1a"
LINE = "#171e35"
LINE2 = "#252e50"
TEXT = "#eef2ff"
MUTED = "#8a96b4"
DIM = "#525c7a"
CYAN = "#65f4dc"
VIOLET = "#b49aff"
AMBER = "#f7c177"
ROSE = "#ff7a95"
BLUE = "#7d97df"
GREEN = "#7cf29c"

BASE_STYLE = """
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
"""


def mix(a, b, t):
    """Linear blend of two #rrggbb colours."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def grain(fid="grain", opacity=0.05):
    """Static film grain: premium texture for flat dark surfaces."""
    return (f'<filter id="{fid}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 {opacity} 0"/></filter>')


def card(width, height, radius=26, grain_id="grain", fill=BG, stroke=LINE2):
    """Background card: fill, dotted lattice, vignette, grain, hairline border."""
    return f'''<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="{fill}"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="url(#lattice)"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="url(#vignette)"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{radius}" filter="url(#{grain_id})"/>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="none" stroke="{stroke}"/>'''


def card_defs(width, height, grain_id="grain", lattice=24):
    return f'''{grain(grain_id)}
<pattern id="lattice" width="{lattice}" height="{lattice}" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="#8b9cce" fill-opacity=".11"/></pattern>
<radialGradient id="vignette" cx=".5" cy=".42" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>'''


def corners(x0, y0, x1, y1, size=10, color=DIM, width=1.2):
    """Registration marks: the instrument feel."""
    s = size
    return (f'<path d="M{x0} {y0 + s}V{y0}H{x0 + s}M{x1 - s} {y0}H{x1}V{y0 + s}'
            f'M{x1} {y1 - s}V{y1}H{x1 - s}M{x0 + s} {y1}H{x0}V{y1 - s}" fill="none" '
            f'stroke="{color}" stroke-width="{width}"/>')


def document(width, height, title, desc, body, style="", defs="", type_=None):
    glyphs = type_.defs() if type_ else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t d">'
            f'<title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<style>{style}{BASE_STYLE}</style>'
            f'<defs>{glyphs}{defs}</defs>{body}</svg>\n')
