# Jenner Logo Ideation Tool

A browser-based design tool for exploring, editing, and exporting variations of the Jenner "J" logo — a 3×3 dot grid that animates through build-up and rotation sequences.

## Installation

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, or Edge)
- No server, build tools, or dependencies required — the tool runs entirely client-side

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/JennerAnalytics/jal-logo.git
   cd jal-logo
   ```

2. Open `prototype.html` in your browser:

   ```bash
   # macOS
   open prototype.html

   # Linux
   xdg-open prototype.html

   # Windows
   start prototype.html
   ```

   Or drag the file into any browser window.

That's it — no `npm install`, no build step.

---

## Quick Start

When the page loads you see a grid of animated logo cards. Each card is a unique combination of **variant**, **dot shape**, **color scheme**, and **sizing mode**.

1. **Browse** the grid to see all combinations animate
2. **Click** a card to pause/resume its animation
3. **Double-click** a card to open the editor
4. **Export** a complete asset pack from the editor

---

## User Guide

### Grid View

The main screen displays all logo variations as animated cards.

#### Filters

Use the filter bar at the top to narrow down the grid:

| Filter | Options | Description |
|--------|---------|-------------|
| **J Variant** | hook-6, stair-6, L-5, right-5, heavy-7, loop-8, full-9 | The J-letterform shape |
| **Dot Shape** | circle, squircle | Round dots or rounded squares |
| **Color Scheme** | dark/light, light/dark, dark/amber | Background and dot colors |
| **Sizing** | uniform, wave, corner, trail | How dot sizes vary across the grid |

Click a filter button to toggle it on/off. Active filters are highlighted. The filter summary at the bottom shows the current selection — click it to copy.

#### Speed & Display Controls

- **Speed** slider: Adjust animation speed (0.1× to 3×)
- **Smooth** toggle: Enable/disable smoothstep interpolation between rotation frames
- **Favicon size** toggle: Preview cards at 32×32px to check small-size legibility

#### Special Variation Sections

Below the standard grid, three sections show curated variations:

- **Smooth Trail** — full-9 with 8-step interpolated trail weights for fluid rotation
- **Center-Pulse** — full-9 with a breathing center dot that pulses with the rotation cycle
- **AA Variations** — heavy-7 with anti-aliased J via fine-tuned dot sizing

These have stable IDs (ST1, CP1, AA1, etc.) that don't change when cards are added.

---

### Editor View

Double-click any card to open the full editor.

#### Preview Panel (left)

- Large 300×300 animated preview
- **Play / Pause / Step** controls for frame-by-frame inspection
- **Speed** slider independent of the grid speed

#### Controls Panel (right)

##### Playback Mode

- **Skip build-up**: Toggle to skip the 5-frame build-up sequence and loop only the rotation frames

##### Weight Matrix (3×3 dot sizes)

Each cell controls the relative size of the dot at that grid position. Values range from 0.10 to 2.00.

- **Period selector** (1–8): Switch between the 8 rotation periods to edit weights independently per frame
- The currently animating period is highlighted with a green border
- Editing a weight immediately updates the preview

##### Dot Shape

Toggle between **Circle** and **Squircle** (rounded square with `r = 0.35 × dotRadius`).

##### Color Scheme

- **Presets**: Click dark/light, light/dark, or dark/amber for quick changes
- **Custom**: Use the color pickers or type hex values for background and dot colors

##### Base Dot Size Ratio

Slider from 0.20 to 0.95 — controls the ratio of dot diameter to cell size (default: 0.60).

##### Animation Timing

- **Build 1–5**: Duration of each build-up frame (40–500ms)
- **Rotation**: Duration of each rotation frame (40–500ms, applies to all 8 periods)

##### Exported Config

A read-only text field showing the current configuration in `JENNER_EDIT:` format. Click **Copy config** in the header to copy it to your clipboard. This format can be pasted back into the source code to recreate the variation.

**Config format example:**
```
JENNER_EDIT:
  variant=full-9 shape=circle bg=#1c1c1e dot=#e8a435 baseSize=0.60
  skipBuild=true rotMs=140
  P1=[[0.40,0.30,1.30],[0.55,0.20,1.15],[0.70,0.85,1.00]]
  P2=[[0.55,0.43,0.85],[0.70,0.33,0.73],[0.85,1.00,1.15]]
  ...
```

---

### Exporting Assets

From the editor view:

1. Choose a **Frame** to export:
   - **Canonical (J visible)** — the first rotation frame (0° orientation)
   - **Current frame** — whatever frame is currently displayed

2. Click **Download Asset Pack (.zip)**

3. A progress bar shows rendering status. When complete, a ZIP file downloads automatically.

#### ZIP Contents

The export produces a ZIP with this structure:

```
jenner-logo-export/
├── original/           # Your configured colors
│   ├── favicon/        # 16, 32, 48, 64, 96, 128, 256px
│   ├── web/            # apple-touch-icon-180, pwa-192, pwa-512, og-1200
│   ├── macos/          # 16–1024px
│   ├── windows/        # 16–256px
│   ├── linux/          # 16–512px
│   └── marketing/      # 1024, 2048, 4096px
├── transparent/        # Same sizes, no background
├── on-white/           # White bg, auto-adjusted dot color
├── on-black/           # Black bg, auto-adjusted dot color
├── mono-on-white/      # White bg, dark dots (#1c1c1e)
├── mono-on-black/      # Black bg, light dots (#f0efe8)
└── svg/
    ├── logo-original.svg
    ├── logo-transparent.svg
    ├── logo-on-white.svg
    ├── logo-on-black.svg
    ├── logo-mono-on-white.svg
    └── logo-mono-on-black.svg
```

**6 background variations × 6 platform size sets + 6 SVGs** — everything needed for web, desktop, mobile, and marketing use.

---

## Validation Tests

Open `test-export.html` in your browser to run automated validation:

1. Open the file
2. Click **Run All Tests**
3. Tests verify:
   - PNG canvas dimensions and blob validity
   - Background color correctness (transparent, white, black, original, mono)
   - SVG DOM structure (element counts, fill attributes, viewBox)
   - ZIP file completeness (all expected paths present)
   - Rotation math (R⁴=I, dot count preservation, formula correctness, smoothstep)

All tests should pass with green checkmarks. Click a category header to expand details.

---

## Mathematical Specification

See [`jenner-logo-spec.md`](jenner-logo-spec.md) for the formal mathematical specification covering:

- Grid coordinate system
- 90° CW rotation operator and C₄ group proof
- All 7 variant canonical matrices
- Frame sequence (build-up + rotation loop)
- Weight matrices and per-period overrides
- Center profile breathing effect
- Smoothstep interpolation formula
- Dot geometry (circle, squircle, tile radius)
- Export variation rules with luminance fallback

---

## File Reference

| File | Purpose |
|------|---------|
| `prototype.html` | Main ideation tool — grid explorer, editor, and export |
| `test-export.html` | Automated export validation tests (38 tests) |
| `jenner-logo-spec.md` | Mathematical specification with LaTeX notation |
| `README.md` | This documentation |

---

## Browser Compatibility

Tested in:
- Chrome 120+
- Firefox 120+
- Safari 17+
- Edge 120+

Requires `canvas.roundRect()` support (available in all modern browsers since 2023). No polyfills needed.

## License

Proprietary — Jenner Analytics Ltd.
