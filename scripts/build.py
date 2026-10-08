#!/usr/bin/env python3
"""Builds every image of the profile.

  python3 scripts/build.py           # all assets (needs rsvg-convert + Pillow for the hero)
  python3 scripts/build.py live      # only the live detector (what the daily Action runs)
  python3 scripts/build.py hero ...  # any subset by name

Dependencies: pip install -r scripts/requirements.txt
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"


def write(name, svg):
    path = ASSETS / name
    path.write_text(svg, encoding="utf-8")
    print(f"  {path.relative_to(ROOT)}  {len(svg.encode()) / 1024:.0f} KiB")


def hero():
    from lab import hero as module
    svg, hits = module.build()
    write("hero.svg", svg)
    print(f"    {hits} impactos")


def live():
    from lab import detector
    for name, svg in detector.build().items():
        write(name, svg)


def arsenal():
    from lab import arsenal as module
    for name, svg in module.build().items():
        write(name, svg)


def experiments():
    from lab import experiments as module
    for name, svg in module.build().items():
        write(name, svg)


def cinema():
    from lab import cinema as module
    for name, svg in module.build().items():
        write(name, svg)


def signature():
    from lab import signature as module
    for name, svg in module.build().items():
        write(name, svg)


TARGETS = {"hero": hero, "arsenal": arsenal, "experiments": experiments,
           "cinema": cinema, "signature": signature, "live": live}

if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    for target in sys.argv[1:] or TARGETS:
        print(f"[{target}]")
        TARGETS[target]()
