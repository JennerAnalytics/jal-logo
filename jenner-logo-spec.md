# Jenner Logo — Mathematical Specification

## 1. Grid System

The logo is a **3×3 cell grid**. Each cell is addressed by row $r \in \{0,1,2\}$ (top to bottom) and column $c \in \{0,1,2\}$ (left to right).

A **dot matrix** $M$ is a $3 \times 3$ binary matrix where $M_{r,c} = 1$ means "draw a dot in cell $(r,c)$" and $M_{r,c} = 0$ means "empty".

$$
M = \begin{pmatrix} M_{0,0} & M_{0,1} & M_{0,2} \\ M_{1,0} & M_{1,1} & M_{1,2} \\ M_{2,0} & M_{2,1} & M_{2,2} \end{pmatrix}, \quad M_{r,c} \in \{0, 1\}
$$

The pixel center of cell $(r,c)$ in a canvas of side length $S$ is:

$$
\text{cx} = \frac{S}{3} \cdot c + \frac{S}{6}, \qquad \text{cy} = \frac{S}{3} \cdot r + \frac{S}{6}
$$

---

## 2. 90° Clockwise Rotation

The rotation operator $R$ maps a 3×3 matrix to its 90° clockwise rotation:

$$
R(M)_{i,j} = M_{2-j,\, i}
$$

Equivalently, as a coordinate permutation: each cell $(r, c)$ maps to $(c, 2-r)$.

**Explicit expansion** for 3×3:

$$
R\!\begin{pmatrix} a & b & c \\ d & e & f \\ g & h & k \end{pmatrix} = \begin{pmatrix} g & d & a \\ h & e & b \\ k & f & c \end{pmatrix}
$$

The center cell $(1,1)$ is a fixed point: $R(M)_{1,1} = M_{1,1}$.

---

## 3. Cyclic Group $C_4$

The four rotations form the cyclic group $C_4 = \{R^0, R^1, R^2, R^3\}$ with the identity $R^0 = I$.

**Theorem.** $R^4 = I$.

*Proof.* Apply the index formula four times:

$$
R^4(M)_{i,j} = R^3(M)_{2-j,i} = R^2(M)_{2-i, 2-j} = R^1(M)_{j, 2-i} = M_{i,j} \qquad \square
$$

The four rotations at the element level:

| $k$ | Formula | Angle |
|-----|---------|-------|
| 0 | $R^0(M)_{i,j} = M_{i,j}$ | 0° |
| 1 | $R^1(M)_{i,j} = M_{2-j,\,i}$ | 90° CW |
| 2 | $R^2(M)_{i,j} = M_{2-i,\,2-j}$ | 180° |
| 3 | $R^3(M)_{i,j} = M_{j,\,2-i}$ | 270° CW |

---

## 4. Variant Definitions

Each variant defines a **canonical matrix** $M^{(0)}$ (the J-letterform at 0° orientation) and a **build-up sequence** $B_0 \ldots B_4$.

### hook-6 (6 dots)
$$
M^{(0)} = \begin{pmatrix} 0 & 0 & 1 \\ 1 & 0 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

### stair-6 (6 dots)
$$
M^{(0)} = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 1 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

### L-5 (5 dots)
$$
M^{(0)} = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 0 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

### right-5 (5 dots)
$$
M^{(0)} = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 1 & 1 \\ 0 & 1 & 1 \end{pmatrix}
$$

### heavy-7 (7 dots)
$$
M^{(0)} = \begin{pmatrix} 0 & 0 & 1 \\ 1 & 1 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

### loop-8 (8 dots, center empty)
$$
M^{(0)} = \begin{pmatrix} 1 & 1 & 1 \\ 1 & 0 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

### full-9 (9 dots, rotation-invariant)
$$
M^{(0)} = \begin{pmatrix} 1 & 1 & 1 \\ 1 & 1 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

**Note:** full-9 satisfies $R(M^{(0)}) = M^{(0)}$; the J-letterform is expressed purely through dot sizing (§6–7), not presence/absence.

---

## 5. Frame Sequence

The animation has two phases:

### Phase 1: Build-up ($F_0 \ldots F_4$)

Five frames that progressively reveal the J-letterform. All variants share the same starting point:

$$
B_0 = \begin{pmatrix} 0 & 0 & 1 \\ 0 & 0 & 0 \\ 0 & 0 & 0 \end{pmatrix}
$$

Each subsequent $B_k$ adds one or more dots until $B_4 = M^{(0)}$.

Default build-up timings: $(120, 120, 120, 140, 180)$ ms.

### Phase 2: Rotation loop ($F_5 \ldots F_{4+N}$)

After build-up, the pattern rotates through $N$ periods. The rotation frame sequence for $N$ periods is:

$$
F_{4+k} = R^{k \bmod 4}(M^{(0)}), \quad k = 1, \ldots, N
$$

The loop restarts at $F_4$ (the canonical orientation). With $N = 4$, the sequence is $M^{(0)}, R^1, R^2, R^3$ and repeats. With $N = 8$ (the default for center-pulse variants), the cycle repeats twice.

**8-period extension:** When `skipBuild = true`, all 8 frames are rotation frames $F_0 \ldots F_7$, with $F_k = R^{k \bmod 4}(M^{(0)})$.

---

## 6. Weight Matrices

A **weight matrix** $W$ is a $3 \times 3$ real matrix that scales each dot's radius. If $M_{r,c} = 1$, the dot's radius is:

$$
\rho_{r,c} = \rho_{\text{base}} \cdot W_{r,c}
$$

where $\rho_{\text{base}} = \frac{S}{6} \cdot d$ and $d$ is the base dot ratio (default $d = 0.6$).

### Predefined sizing modes

**Uniform:**
$$
W_{\text{uniform}} = \begin{pmatrix} 1 & 1 & 1 \\ 1 & 1 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

**Wave** (rotates with pattern):
$$
W_{\text{wave}} = \begin{pmatrix} 1.3 & 1.3 & 1.3 \\ 1.0 & 1.0 & 1.0 \\ 0.7 & 0.7 & 0.7 \end{pmatrix}
$$

**Corner** (rotation-invariant):
$$
W_{\text{corner}} = \begin{pmatrix} 1.25 & 0.85 & 1.25 \\ 0.85 & 1.10 & 0.85 \\ 1.25 & 0.85 & 1.25 \end{pmatrix}
$$

**Trail** (directional gradient, rotates with pattern):
$$
W_{\text{trail}} = \begin{pmatrix} 0.40 & 0.30 & 1.30 \\ 0.55 & 0.30 & 1.15 \\ 0.70 & 0.85 & 1.00 \end{pmatrix}
$$

### Rotation rule for weights

For sizing modes that rotate with the pattern (wave, trail), the weight matrix for period $k$ is:

$$
W_k = R^{k \bmod 4}(W_0)
$$

where $R$ applies the same index permutation as for dot matrices. For rotation-invariant modes (uniform, corner), $W_k = W_0$ for all $k$.

### Per-period override (custom weights)

In the editor, each of the 8 rotation periods can have an independently defined weight matrix $W_0, W_1, \ldots, W_7$. These are stored directly and do not follow the rotation rule.

---

## 7. Center Profile

An optional **center profile** array $\mathbf{p} = (p_0, p_1, \ldots, p_{N-1})$ overrides the center cell weight:

$$
W_k[1][1] = p_k
$$

This creates a "breathing" effect where the center dot is smallest when the J-letterform is most visible (canonical orientation) and largest during intermediate rotation positions.

**Example** (pulse-da-trail):
$$
\mathbf{p} = (0.20, 0.45, 0.65, 0.45, 0.20, 0.45, 0.65, 0.45)
$$

This is a symmetric profile with period 4 embedded in an 8-frame loop: smallest at 0° and 360° (frames 0, 4), largest at 180° (frames 2, 6).

---

## 8. Smooth Interpolation

When smooth rotation is enabled, the renderer cross-fades between consecutive frames.

### Smoothstep easing

Given normalized progress $t \in [0, 1]$ within a frame:

$$
s(t) = t^2(3 - 2t)
$$

Properties:
- $s(0) = 0$, $s(1) = 1$, $s(0.5) = 0.5$
- $s'(0) = 0$, $s'(1) = 0$ (zero velocity at endpoints)
- Monotonically increasing on $[0, 1]$

### Cross-fade blending

For two consecutive frames with matrices $M_A, M_B$ and weights $W_A, W_B$, the interpolated dot radius at cell $(r, c)$ is:

$$
\rho_{r,c}(t) = \rho_{\text{base}} \cdot \begin{cases}
W_A[r][c] \cdot (1 - s(t)) + W_B[r][c] \cdot s(t) & \text{if } M_A[r][c] = 1 \text{ and } M_B[r][c] = 1 \\
W_A[r][c] \cdot (1 - s(t)) & \text{if } M_A[r][c] = 1 \text{ and } M_B[r][c] = 0 \\
W_B[r][c] \cdot s(t) & \text{if } M_A[r][c] = 0 \text{ and } M_B[r][c] = 1 \\
0 & \text{otherwise}
\end{cases}
$$

Dots with $\rho_{r,c} < 0.01 \cdot \rho_{\text{base}}$ are culled.

---

## 9. Dot Geometry

### Cell size and base radius

$$
\text{cellSize} = \frac{S}{3}, \qquad \rho_{\text{base}} = \frac{\text{cellSize} \cdot d}{2}
$$

where $S$ is the canvas side length and $d$ is the base dot ratio (default 0.6).

### Circle dots

A circle centered at $(\text{cx}, \text{cy})$ with radius $\rho_{r,c}$.

### Squircle dots (rounded rectangle)

A square of side $2\rho_{r,c}$, centered at $(\text{cx}, \text{cy})$, with corner radius:

$$
r_{\text{corner}} = 0.35 \cdot \rho_{r,c}
$$

### Background tile

A rounded rectangle filling the full canvas with corner radius:

$$
r_{\text{tile}} = 0.12 \cdot S
$$

---

## 10. Export Variations

Static exports render a single frame (typically the canonical orientation) at multiple sizes.

### Background variations

| Variation | Background | Dot color | Notes |
|-----------|-----------|-----------|-------|
| `original` | Config bg | Config dot | As designed |
| `transparent` | None (α=0) | Config dot | PNG only; no background rect in SVG |
| `on-white` | `#ffffff` | Config dot (or `#1c1c1e` if dot too light) | Luminance fallback at threshold 0.6 |
| `on-black` | `#000000` | Config dot (or `#f0efe8` if dot too dark) | Luminance fallback at threshold 0.4 |
| `mono-on-white` | `#ffffff` | `#1c1c1e` | Monochrome light |
| `mono-on-black` | `#000000` | `#f0efe8` | Monochrome dark |

### Luminance test for fallback

$$
L = 0.299R + 0.587G + 0.114B
$$

where $R, G, B \in [0, 1]$. For `on-white`, if $L_{\text{dot}} \geq 0.6$ the dot color falls back to `#1c1c1e`. For `on-black`, if $L_{\text{dot}} \leq 0.4$ the dot color falls back to `#f0efe8`.

### Platform sizes

| Platform | Sizes (px) |
|----------|-----------|
| favicon | 16, 32, 48, 64, 96, 128, 256 |
| web | 180 (apple-touch), 192 (PWA), 512 (PWA), 1200 (OG) |
| macOS | 16, 32, 64, 128, 256, 512, 1024 |
| Windows | 16, 24, 32, 48, 64, 128, 256 |
| Linux | 16, 22, 24, 32, 48, 64, 96, 128, 256, 512 |
| Marketing | 1024, 2048, 4096 |

### SVG export

One SVG per variation at 512×512 with the same dot geometry, using `<circle>` for circle dots and `<rect rx ry>` for squircle dots.

---

## Appendix: Worked Example — full-9 with trail weights

**Setup:** variant = full-9, sizing = trail, 8-period rotation, `skipBuild = true`.

### Canonical matrix (all frames identical for full-9)

$$
M^{(0)} = M^{(1)} = \cdots = M^{(7)} = \begin{pmatrix} 1 & 1 & 1 \\ 1 & 1 & 1 \\ 1 & 1 & 1 \end{pmatrix}
$$

Since full-9 is rotation-invariant, $R^k(M^{(0)}) = M^{(0)}$ for all $k$.

### Weight matrices

Base weight $W_0 = W_{\text{trail}}$:

$$
W_0 = \begin{pmatrix} 0.40 & 0.30 & 1.30 \\ 0.55 & 0.30 & 1.15 \\ 0.70 & 0.85 & 1.00 \end{pmatrix}
$$

$$
W_1 = R(W_0) = \begin{pmatrix} 0.70 & 0.55 & 0.40 \\ 0.85 & 0.30 & 0.30 \\ 1.00 & 1.15 & 1.30 \end{pmatrix}
$$

$$
W_2 = R^2(W_0) = \begin{pmatrix} 1.00 & 0.85 & 0.70 \\ 1.15 & 0.30 & 0.55 \\ 1.30 & 0.30 & 0.40 \end{pmatrix}
$$

$$
W_3 = R^3(W_0) = \begin{pmatrix} 1.30 & 1.15 & 1.00 \\ 0.30 & 0.30 & 0.85 \\ 0.40 & 0.55 & 0.70 \end{pmatrix}
$$

$W_4 = W_0$, $W_5 = W_1$, $W_6 = W_2$, $W_7 = W_3$ (period-4 repetition).

### Center profile override

With center profile $\mathbf{p} = (0.20, 0.45, 0.65, 0.45, 0.20, 0.45, 0.65, 0.45)$:

$$
W_0[1][1] \leftarrow 0.20, \quad W_1[1][1] \leftarrow 0.45, \quad W_2[1][1] \leftarrow 0.65, \quad \ldots
$$

### Interpolation at $t = 0.5$ between frames 0 and 1

Smoothstep: $s(0.5) = 0.5$.

For cell $(0, 2)$: both frames have the dot, so:

$$
\rho_{0,2} = \rho_{\text{base}} \cdot (1.30 \cdot 0.5 + 0.40 \cdot 0.5) = \rho_{\text{base}} \cdot 0.85
$$

For cell $(1, 1)$ with center profile:

$$
\rho_{1,1} = \rho_{\text{base}} \cdot (0.20 \cdot 0.5 + 0.45 \cdot 0.5) = \rho_{\text{base}} \cdot 0.325
$$

### Dot radius at 512px canvas, $d = 0.6$

$$
\text{cellSize} = \frac{512}{3} \approx 170.67, \quad \rho_{\text{base}} = \frac{170.67 \times 0.6}{2} = 51.20
$$

For cell $(0, 2)$ at frame 0: $\rho = 51.20 \times 1.30 = 66.56$ px.

For center at frame 0: $\rho = 51.20 \times 0.20 = 10.24$ px.
