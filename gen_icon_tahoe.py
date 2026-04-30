#!/usr/bin/env python3
"""
gen_icon_tahoe.py — generate Apple `.icon` (Tahoe layered) bundles for the
Jenner logo design system.

Output format
-------------
A `.icon` bundle is a directory package consumed by Xcode 26 / macOS 26
Tahoe. Layout::

    Foo.icon/
      icon.json     (manifest — see schema notes below)
      Assets/
        <layer>.svg (or .png)

The bundle is compiled by `actool` into an `Assets.car` (used by Tahoe and
later) and a backwards-compatible `.icns` (used by older macOS releases).

icon.json schema (verified against real Apple-Icon-Composer-generated
samples and the Xcode 26.4.1 IconComposerFoundation.framework string table;
see `temp/icon-samples/` for primary sources):

    {
      "fill" | "fill-specializations": ...,   // canvas background
      "groups": [
        {
          "blend-mode"?: "normal" | "overlay" | "soft-light" | ...,
          "blur-material"?: number | null,
          "lighting"?: "individual" | "combined",
          "shadow": {"kind": "neutral"|"layer-color"|"none", "opacity": float},
          "specular"?: bool,
          "translucency": {"enabled": bool, "value": float},
          "position"?: {"scale": float, "translation-in-points": [x, y]},
          "name"?: str,
          "hidden"?: bool,
          "layers": [
            {
              "image-name": "filename in Assets/",
              "name"?: str,
              "fill"?: ...,           // tints the layer image
              "glass"?: bool,         // apply Liquid-Glass material
              "hidden"?: bool,
              "opacity"?: float,
              "position"?: {...},
              "blend-mode"?: str
            }
          ]
        }
      ],
      "supported-platforms": {"squares": ["macOS"|"iOS"|...]|"shared",
                              "circles": ["watchOS"]}
    }

Color literal grammar (used inside fills):
    "srgb:R,G,B,A"           — sRGB
    "display-p3:R,G,B,A"     — Display P3 (preferred for wide-gamut colors)
    "extended-srgb:R,G,B,A"  — sRGB extended-range
    "gray:V,A"               — gamma-2.2 gray
    "extended-gray:V,A"      — extended-range gray

Fill values:
    "automatic"                                   — defers to the canvas
    "system-light" | "system-dark"                — semantic fills
    {"solid": "color"}
    {"automatic-gradient": "color"}               — auto darken to gradient
    {"linear-gradient": ["color1", "color2"],
     "orientation"?: {"start":{x,y}, "stop":{x,y}}}

Tahoe Liquid-Glass design considerations
----------------------------------------
- All Tahoe icons are rounded-square. The OS applies the corner-radius mask
  itself; do NOT bake in your own rounded-rect mask.
- The dot grid is the brand mark; we map it to a single foreground "dots"
  layer over a solid canvas fill (the dark tile colour for `original-amber`,
  white for `mono-on-white`, etc.). One layer with `glass: true` gets the
  Liquid-Glass refraction; setting it false yields a flat Aqua-style icon.
- Specular highlights and translucency are surface effects of the *group*
  the layers live in, not of individual layers.
- `actool` produces both `Assets.car` (Tahoe, iOS 26+) and a backward-
  compatible `.icns` automatically — consumers get a single bundle to ship.

Usage
-----
    python3 gen_icon_tahoe.py                       # default: amber-on-dark, all 7 variants
    python3 gen_icon_tahoe.py --variant full-9
    python3 gen_icon_tahoe.py --color-scheme mono-on-black
    python3 gen_icon_tahoe.py --compile             # also run actool to verify

The script is dependency-free: pure Python 3.8+ stdlib.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

# -----------------------------------------------------------------------------
# Repository paths
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
ICON_OUT = REPO_ROOT / "assets" / "icon-tahoe"
SVG_DIR = REPO_ROOT / "assets" / "svg"  # for reference, not used directly

# -----------------------------------------------------------------------------
# Canonical variant matrices (per jenner-logo-spec.md §4)
# -----------------------------------------------------------------------------

VARIANT_MATRICES: Dict[str, List[List[int]]] = {
    "hook-6":  [[0, 0, 1], [1, 0, 1], [1, 1, 1]],
    "stair-6": [[0, 0, 1], [0, 1, 1], [1, 1, 1]],
    "L-5":     [[0, 0, 1], [0, 0, 1], [1, 1, 1]],
    "right-5": [[0, 0, 1], [0, 1, 1], [0, 1, 1]],
    "heavy-7": [[0, 0, 1], [1, 1, 1], [1, 1, 1]],
    "loop-8":  [[1, 1, 1], [1, 0, 1], [1, 1, 1]],
    "full-9":  [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
}

VARIANTS: Tuple[str, ...] = tuple(VARIANT_MATRICES.keys())

# Per spec §6, "trail" weights — the canonical brand presentation that gives
# the J-shape its directional emphasis. This matches assets/svg/logo-original.svg.
W_TRAIL: List[List[float]] = [
    [0.40, 0.30, 1.30],
    [0.55, 0.30, 1.15],
    [0.70, 0.85, 1.00],
]
W_UNIFORM: List[List[float]] = [[1.0] * 3 for _ in range(3)]

# Default canvas size for SVG layers (actool rasterises as needed).
SVG_SIZE = 1024
DOT_RATIO = 0.6

# -----------------------------------------------------------------------------
# Color schemes
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ColorScheme:
    name: str
    bg_hex: str        # canvas fill (the tile colour)
    dot_hex: str       # dot fill
    glass: bool        # apply Liquid-Glass material to the dots layer
    specular: bool     # apply specular highlight to the group
    translucency: float  # 0..1, glass refraction strength
    use_p3_for_dots: bool  # use display-p3 colour-space for richer amber
    shadow_opacity: float = 0.5  # 0..1, drop-shadow strength on the group

# original-amber is the priority brand presentation: dark tile + amber dots
#
# Brand-locked defaults for original-amber as of 2026-04-30. Do not change
# without a fresh visual A/B and brand-owner approval. The locked parameters
# are: single foreground layer (no midground), glass=True on the dots layer,
# specular=True on the group, dot colour in display-p3, neutral fill in sRGB,
# shadow.opacity=0.3, translucency.value=0.3. The 0.3 values supersede the
# original 0.5 median-of-samples guesses after visual review of side-by-side
# renders (see temp/comparisons/index.html — gitignored decision provenance).
#
# Other color schemes (mono-on-black, mono-on-white, dark-transparent) are
# NOT yet locked — keep their defaults provisional until they go through the
# same visual review. See README "Locked defaults" subsection.
COLOR_SCHEMES: Dict[str, ColorScheme] = {
    "original-amber": ColorScheme(
        name="original-amber",
        bg_hex="#1c1c1e",
        dot_hex="#e8a435",
        glass=True,
        specular=True,
        translucency=0.3,  # LOCKED 2026-04-30 (was 0.5)
        use_p3_for_dots=True,
        shadow_opacity=0.3,  # LOCKED 2026-04-30 (was 0.5)
    ),
    "mono-on-black": ColorScheme(
        name="mono-on-black",
        bg_hex="#000000",
        dot_hex="#f0efe8",
        glass=True,
        specular=True,
        translucency=0.4,
        use_p3_for_dots=False,
    ),
    "mono-on-white": ColorScheme(
        name="mono-on-white",
        bg_hex="#ffffff",
        dot_hex="#1c1c1e",
        glass=False,
        specular=False,
        translucency=0.3,
        use_p3_for_dots=False,
    ),
    "dark-transparent": ColorScheme(
        # near-transparent canvas, dark dots — for chrome-on-light contexts
        name="dark-transparent",
        bg_hex="#1c1c1e",
        dot_hex="#1c1c1e",
        glass=True,
        specular=True,
        translucency=0.6,
        use_p3_for_dots=False,
    ),
}

# -----------------------------------------------------------------------------
# Geometry — same math as prototype.html and gen_mono_transparent_anim.py
# -----------------------------------------------------------------------------

def dot_centers(size: int) -> List[List[Tuple[float, float]]]:
    """Return cell-center coordinates for a 3x3 grid on a `size` square."""
    cell = size / 3.0
    return [
        [(cell * c + cell / 2.0, cell * r + cell / 2.0) for c in range(3)]
        for r in range(3)
    ]


def dot_radius(weight: float, size: int) -> float:
    """Per spec §9: rho_base = (cellSize * d) / 2, then scaled by weight."""
    cell = size / 3.0
    base_r = cell * DOT_RATIO / 2.0
    return base_r * weight

# -----------------------------------------------------------------------------
# Color literal serialisation (per Icon Composer color grammar)
# -----------------------------------------------------------------------------

def hex_to_rgba(hex_str: str) -> Tuple[float, float, float, float]:
    s = hex_str.lstrip("#")
    if len(s) == 6:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
        a = 1.0
    elif len(s) == 8:
        r = int(s[0:2], 16) / 255.0
        g = int(s[2:4], 16) / 255.0
        b = int(s[4:6], 16) / 255.0
        a = int(s[6:8], 16) / 255.0
    else:
        raise ValueError(f"invalid hex color: {hex_str}")
    return r, g, b, a


def color_literal(hex_str: str, color_space: str = "srgb") -> str:
    """Encode a colour as an Icon Composer literal: "srgb:R,G,B,A" etc."""
    r, g, b, a = hex_to_rgba(hex_str)
    return f"{color_space}:{r:.5f},{g:.5f},{b:.5f},{a:.5f}"


# -----------------------------------------------------------------------------
# SVG generation — produces the foreground "dots" layer
# -----------------------------------------------------------------------------

def dots_svg(matrix: List[List[int]], weights: List[List[float]],
             dot_hex: str, size: int = SVG_SIZE) -> str:
    """Return an SVG string with just the dots — no background tile, since
    Icon Composer paints the canvas via the top-level fill and applies the
    rounded-square mask itself."""
    centers = dot_centers(size)
    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
    ]
    for r in range(3):
        for c in range(3):
            if not matrix[r][c]:
                continue
            cx, cy = centers[r][c]
            rad = dot_radius(weights[r][c], size)
            parts.append(
                f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" '
                f'r="{rad:.2f}" fill="{dot_hex}"/>'
            )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# -----------------------------------------------------------------------------
# Manifest construction
# -----------------------------------------------------------------------------

def build_icon_json(scheme: ColorScheme, dots_filename: str = "dots.svg") -> dict:
    """Return the icon.json structure for a single-foreground-layer Jenner mark.

    Single-group / single-layer model is justified by the canonical brand
    presentation: a flat tile with a foreground dot pattern. The Liquid-Glass
    material on the dots layer + specular highlight on the group give the
    Tahoe-native depth treatment without needing midground layers.
    """
    dot_space = "display-p3" if scheme.use_p3_for_dots else "srgb"
    bg_color = color_literal(scheme.bg_hex, "srgb")

    layer = {
        "image-name": dots_filename,
        "name": "dots",
        # tint the layer with the dot colour so it composites consistently
        # under tinted/dark/clear appearances; without an explicit fill the
        # layer would render the SVG's own colours flat.
        "fill": {"solid": color_literal(scheme.dot_hex, dot_space)},
    }
    if scheme.glass:
        layer["glass"] = True

    group = {
        "layers": [layer],
        "shadow": {"kind": "neutral", "opacity": float(scheme.shadow_opacity)},
        "translucency": {
            "enabled": bool(scheme.translucency > 0),
            "value": float(scheme.translucency),
        },
    }
    if scheme.specular:
        group["specular"] = True

    return {
        "fill": {"solid": bg_color},
        "groups": [group],
        "supported-platforms": {"squares": ["macOS"]},
    }


# -----------------------------------------------------------------------------
# Bundle writer
# -----------------------------------------------------------------------------

def write_bundle(out_dir: Path, variant: str, scheme: ColorScheme) -> Path:
    """Write a `<variant>.icon/` bundle into `out_dir`. Returns the path."""
    bundle = out_dir / f"{variant}.icon"
    assets = bundle / "Assets"
    assets.mkdir(parents=True, exist_ok=True)

    # 1. dots.svg — the foreground layer, sized to 1024 (Tahoe master size)
    matrix = VARIANT_MATRICES[variant]
    # We use the trail weight matrix as the canonical brand presentation.
    # Note: when fill-tinting the layer, the SVG dot colour is irrelevant
    # (it gets replaced) — but we keep it as the dot colour so the Asset is
    # also useful as a standalone SVG.
    svg = dots_svg(matrix, W_TRAIL, scheme.dot_hex, size=SVG_SIZE)
    (assets / "dots.svg").write_text(svg)

    # 2. icon.json
    manifest = build_icon_json(scheme, dots_filename="dots.svg")
    (bundle / "icon.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    return bundle


# -----------------------------------------------------------------------------
# Optional: actool compile validation
# -----------------------------------------------------------------------------

def actool_compile(bundle: Path, app_icon_name: str = None,
                   target_version: str = "26.0") -> Tuple[int, str]:
    """Compile the bundle with actool into a temp out-dir; return (rc, log)."""
    if shutil.which("xcrun") is None:
        return 127, "xcrun not in PATH (Xcode not installed?)"
    name = app_icon_name or bundle.stem
    out_dir = bundle.parent / f"{bundle.stem}.compiled"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "xcrun", "actool", str(bundle),
        "--compile", str(out_dir),
        "--platform", "macosx",
        "--minimum-deployment-target", target_version,
        "--app-icon", name,
        "--include-all-app-icons",
        "--output-format", "human-readable-text",
        "--output-partial-info-plist", str(out_dir / "partial.plist"),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log = proc.stdout + proc.stderr
    return proc.returncode, log


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--variant", "-v", action="append", choices=VARIANTS + ("all",),
                   help="Variant(s) to generate (default: all 7).")
    p.add_argument("--color-scheme", "-c", action="append",
                   choices=tuple(COLOR_SCHEMES) + ("all",),
                   help="Color scheme(s) (default: original-amber).")
    p.add_argument("--out-dir", "-o", default=str(ICON_OUT),
                   help=f"Output root (default: {ICON_OUT}).")
    p.add_argument("--compile", action="store_true",
                   help="Run xcrun actool on each bundle to verify.")
    p.add_argument("--clean", action="store_true",
                   help="Remove existing bundles in the output dir first.")
    args = p.parse_args()

    variants = args.variant or ["all"]
    if "all" in variants:
        variants = list(VARIANTS)
    schemes = args.color_scheme or ["original-amber"]
    if "all" in schemes:
        schemes = list(COLOR_SCHEMES.keys())

    out_root = Path(args.out_dir).resolve()

    print(f"Output root: {out_root}")
    print(f"Variants:    {', '.join(variants)}")
    print(f"Schemes:     {', '.join(schemes)}")
    print(f"Compile:     {args.compile}")
    print()

    failures: List[str] = []
    bundles: List[Path] = []

    for scheme_name in schemes:
        scheme = COLOR_SCHEMES[scheme_name]
        scheme_dir = out_root / scheme_name
        if args.clean and scheme_dir.exists():
            shutil.rmtree(scheme_dir)
        scheme_dir.mkdir(parents=True, exist_ok=True)

        for variant in variants:
            bundle = write_bundle(scheme_dir, variant, scheme)
            bundles.append(bundle)
            print(f"  wrote {bundle.relative_to(out_root.parent)}")

            if args.compile:
                rc, log = actool_compile(bundle)
                tag = "OK" if rc == 0 else "FAIL"
                print(f"    actool {tag} (exit {rc})")
                if rc != 0:
                    failures.append(f"{bundle}: rc={rc}\n{log}")
                # leave .compiled/ next to the bundle for inspection

    print()
    print(f"Done. {len(bundles)} bundle(s) written.")
    if failures:
        print()
        print("Compile failures:")
        for f in failures:
            print(f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
