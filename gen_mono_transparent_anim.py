#!/usr/bin/env python3
"""
Generate mono-transparent animation files for the Jenner logo.

Produces:
  animation/logo-mono-transparent.gif       (256px animated GIF)
  animation/logo-mono-transparent-512.gif   (512px animated GIF)
  animation/logo-mono-transparent.apng      (256px animated PNG)
  animation/sprite-mono-transparent.png     (12288x256 sprite sheet)
  animation/sprite-mono-transparent.css     (CSS for sprite animation)

Spec: full-9 variant, trail weights, 8-period rotation, skipBuild=true,
center profile = (0.20, 0.45, 0.65, 0.45, 0.20, 0.45, 0.65, 0.45),
6 sub-frames per period = 48 frames total, 23cs per frame.
"""

import math
import os
import shutil
import subprocess
import textwrap
from PIL import Image

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOT_COLOR = "#ffffff"
DOT_RATIO = 0.6      # d — base dot ratio
N_PERIODS = 8
N_SUBFRAMES = 6
N_FRAMES = N_PERIODS * N_SUBFRAMES  # 48
FRAME_DELAY_CS = 23  # centiseconds (matches existing variants)
ANIM_DURATION_S = N_FRAMES * FRAME_DELAY_CS / 100  # 11.04s

CANVAS_SM = 256
CANVAS_LG = 512

REPO = "/home/lwsinclair/git-local/jal-logo"
OUTPUT_DIR = os.path.join(REPO, "assets", "animation")
TEMP_DIR = "/tmp/jenner-mono-transparent-anim"

# ---------------------------------------------------------------------------
# Spec: trail weight matrix and rotation
# ---------------------------------------------------------------------------

W_TRAIL_BASE = [
    [0.40, 0.30, 1.30],
    [0.55, 0.30, 1.15],
    [0.70, 0.85, 1.00],
]

CENTER_PROFILE = [0.20, 0.45, 0.65, 0.45, 0.20, 0.45, 0.65, 0.45]


def rotate_cw(M):
    """90° clockwise rotation: R(M)[i][j] = M[2-j][i]"""
    return [[M[2 - j][i] for j in range(3)] for i in range(3)]


def get_weights(period_k):
    """Effective weight matrix for period k with center profile applied."""
    W = W_TRAIL_BASE
    for _ in range(period_k % 4):
        W = rotate_cw(W)
    W = [row[:] for row in W]   # deep copy
    W[1][1] = CENTER_PROFILE[period_k % 8]
    return W


# ---------------------------------------------------------------------------
# Frame geometry
# ---------------------------------------------------------------------------

def smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def frame_svg(frame_idx, size):
    """Return SVG string for a given frame at the given canvas size."""
    period = frame_idx // N_SUBFRAMES
    subframe = frame_idx % N_SUBFRAMES

    W_cur = get_weights(period)
    W_next = get_weights((period + 1) % N_PERIODS)

    t = subframe / N_SUBFRAMES
    s = smoothstep(t)

    cell = size / 3.0
    base_r = cell * DOT_RATIO / 2.0

    circles = []
    for r in range(3):
        for c in range(3):
            w = W_cur[r][c] * (1.0 - s) + W_next[r][c] * s
            radius = base_r * w
            cx = cell * c + cell / 2.0
            cy = cell * r + cell / 2.0
            circles.append(
                f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" '
                f'r="{radius:.2f}" fill="{DOT_COLOR}"/>'
            )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}">\n'
        + "\n".join(circles)
        + "\n</svg>\n"
    )


# ---------------------------------------------------------------------------
# Frame rendering
# ---------------------------------------------------------------------------

def render_frames(size, label):
    """Render all 48 frames to PNG at the given size. Returns list of paths."""
    size_dir = os.path.join(TEMP_DIR, f"frames_{size}")
    os.makedirs(size_dir, exist_ok=True)
    paths = []
    for i in range(N_FRAMES):
        svg_path = os.path.join(size_dir, f"frame_{i:02d}.svg")
        png_path = os.path.join(size_dir, f"frame_{i:02d}.png")
        with open(svg_path, "w") as f:
            f.write(frame_svg(i, size))
        subprocess.run(
            ["convert", "-background", "none", "-colorspace", "sRGB",
             "-type", "TrueColorAlpha", svg_path, png_path],
            check=True, capture_output=True,
        )
        paths.append(png_path)
    print(f"  {N_FRAMES} {label} frames rendered at {size}px")
    return paths


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def make_gif(frame_paths, out_path):
    cmd = (
        ["convert", "-loop", "0", "-delay", str(FRAME_DELAY_CS),
         "-dispose", "Background"]
        + frame_paths
        + [out_path]
    )
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  GIF  → {os.path.basename(out_path)}")


def make_apng(frame_paths, out_path):
    frame_duration_ms = int(FRAME_DELAY_CS * 10)
    frames = [Image.open(p).convert("RGBA") for p in frame_paths]
    frames[0].save(
        out_path,
        format="PNG",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=frame_duration_ms,
    )
    print(f"  APNG → {os.path.basename(out_path)}")


def make_sprite_png(frame_paths, out_path):
    subprocess.run(
        ["convert", "+append"] + frame_paths + [out_path],
        check=True, capture_output=True,
    )
    print(f"  PNG  → {os.path.basename(out_path)}")


def make_sprite_css(out_path):
    total_width = CANVAS_SM * N_FRAMES  # 12288
    lines = [
        "/* Jenner Logo Sprite Animation */",
        ".jenner-logo {",
        f"  width: {CANVAS_SM}px;",
        f"  height: {CANVAS_SM}px;",
        f"  background-size: {total_width}px {CANVAS_SM}px;",
        f"  animation: jenner-rotate {ANIM_DURATION_S:.2f}s steps(1) infinite;",
        "}",
        "",
        "@keyframes jenner-rotate {",
    ]
    for i in range(N_FRAMES):
        pct = i / N_FRAMES * 100.0
        x = i * CANVAS_SM
        lines.append(f"  {pct:.2f}% {{ background-position: -{x}px 0; }}")
    lines += ["  100% { background-position: 0 0; }", "}", ""]
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  CSS  → {os.path.basename(out_path)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Rendering frames...")
    frames_sm = render_frames(CANVAS_SM, "small")
    frames_lg = render_frames(CANVAS_LG, "large")

    print("Assembling animation files...")
    make_gif(frames_sm, os.path.join(OUTPUT_DIR, "logo-mono-transparent.gif"))
    make_gif(frames_lg, os.path.join(OUTPUT_DIR, "logo-mono-transparent-512.gif"))
    make_apng(frames_sm, os.path.join(OUTPUT_DIR, "logo-mono-transparent.apng"))
    make_sprite_png(frames_sm, os.path.join(OUTPUT_DIR, "sprite-mono-transparent.png"))
    make_sprite_css(os.path.join(OUTPUT_DIR, "sprite-mono-transparent.css"))

    shutil.rmtree(TEMP_DIR)
    print("Done.")


if __name__ == "__main__":
    main()
