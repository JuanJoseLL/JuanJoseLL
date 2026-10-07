#!/usr/bin/env python3
"""Render the profile's original looping GIF. Requires rsvg-convert and ffmpeg.

Usage: python3 scripts/render-signal.py
All frames are drawn from vectors. No network, packages or downloaded artwork.
"""

import math
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1000, 300
FRAMES, FPS = 80, 20
TAU = math.tau
CYAN, PURPLE = "#65f4dc", "#b49aff"


def frame_svg(index):
    phase = index / FRAMES * TAU
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
      <defs>
        <radialGradient id="halo"><stop stop-color="#7960e8" stop-opacity=".24"/><stop offset="1" stop-color="#7960e8" stop-opacity="0"/></radialGradient>
        <linearGradient id="ink"><stop stop-color="{CYAN}"/><stop offset="1" stop-color="{PURPLE}"/></linearGradient>
      </defs>
      <style>text{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',monospace}}</style>
      <rect x="1" y="1" width="998" height="298" rx="16" fill="#090d18" stroke="#2a3048"/>
      <circle cx="807" cy="150" r="145" fill="url(#halo)"/>
      <text x="32" y="35" fill="#8f9cba" font-size="11" letter-spacing="2">THOUGHT → SIGNAL → SOMETHING REAL</text>
      <text x="32" y="270" fill="#8f9cba" font-size="11" letter-spacing="2">PERSONAL LAB / IDEA VISUALIZER</text>
      <text x="942" y="270" text-anchor="end" fill="#8f9cba" font-size="11" letter-spacing="2">LOOP / ∞</text>
      <path d="M32 52H968M32 247H968" stroke="#262c43"/>
      <text x="40" y="102" fill="{CYAN}" font-size="13" letter-spacing="2">CURIOSIDAD</text>
      <text x="40" y="209" fill="{PURPLE}" font-size="13" letter-spacing="2">CÓDIGO</text>''']

    # Two traveling waveforms feed the orbital core. Every phase is periodic.
    for row, color, direction in [(135, CYAN, 1), (165, PURPLE, -1)]:
        points = []
        for x in range(40, 650, 3):
            envelope = math.sin((x - 40) / 610 * math.pi) ** 2
            y = row + math.sin((x - 40) / 610 * TAU * 3 - phase * direction) * 15 * envelope
            points.append(f"{x},{y:.2f}")
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="1.6" opacity=".8"/>')
        for offset in range(3):
            progress = (index / FRAMES + offset / 3) % 1
            x = 40 + progress * 608
            envelope = math.sin((x - 40) / 610 * math.pi) ** 2
            y = row + math.sin((x - 40) / 610 * TAU * 3 - phase * direction) * 15 * envelope
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"/>')
    parts.append('<path d="M650 135L687 150L650 165" fill="none" stroke="#586484"/>')

    # A projected spherical lattice with three tilted elliptical orbits.
    cx, cy = 807, 150
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="91" fill="none" stroke="#343657" stroke-dasharray="2 7"/>')
    particles = []
    for orbit, (angle, color) in enumerate([(-35, CYAN), (35, PURPLE), (90, "#7d97df")]):
        parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="113" ry="39" transform="rotate({angle} {cx} {cy})" fill="none" stroke="{color}" stroke-opacity=".4"/>')
        rotation = math.radians(angle)
        for offset in range(2):
            theta = phase * (1 if orbit != 1 else -1) + orbit * 1.7 + offset * math.pi
            u, v = 113 * math.cos(theta), 39 * math.sin(theta)
            x = cx + u * math.cos(rotation) - v * math.sin(rotation)
            y = cy + u * math.sin(rotation) + v * math.cos(rotation)
            particles.append((math.sin(theta), x, y, color))
    for depth, x, y, color in sorted(particles):
        radius = 3 + (depth + 1)
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius + 4:.2f}" fill="{color}" opacity=".12"/>')
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{color}"/>')
    pulse = 22 + math.sin(phase) * 2
    parts.append(f'''<circle cx="{cx}" cy="{cy}" r="{pulse + 12:.2f}" fill="{CYAN}" opacity=".06"/>
      <circle cx="{cx}" cy="{cy}" r="{pulse:.2f}" fill="#121c2c" stroke="{CYAN}" stroke-opacity=".7"/>
      <text x="{cx}" y="159" font-size="28" text-anchor="middle" fill="#e5fff9">ψ</text>
      </svg>''')
    return "\n".join(parts)


def main():
    for executable in ("rsvg-convert", "ffmpeg"):
        if not shutil.which(executable):
            raise SystemExit(f"Missing {executable}. On macOS: brew install librsvg ffmpeg")
    output = ROOT / "assets" / "quantum-signal.gif"
    with tempfile.TemporaryDirectory(prefix="jj-signal-") as temporary:
        directory = Path(temporary)
        for index in range(FRAMES):
            subprocess.run(
                ["rsvg-convert", "--output", str(directory / f"frame-{index:03d}.png")],
                input=frame_svg(index).encode(), check=True,
            )
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-framerate", str(FPS), "-i", str(directory / "frame-%03d.png"),
            "-filter_complex",
            "[0:v]split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=3",
            "-loop", "0", str(output),
        ], check=True)
    print(f"Rendered {output.relative_to(ROOT)}: {FRAMES} frames, {FRAMES / FPS:g}s seamless loop, {output.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
