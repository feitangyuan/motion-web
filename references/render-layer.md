# Render Layer — 用什么画，比画什么先决定

Every other doc here assumes the page is DOM + CSS. That assumption is the
ceiling this skill kept hitting: seven cases shipped, all DOM, all system fonts,
none reaching the references. Pick the layer **before** the mechanic
(`SKILL.md` freeform step 5), because the layer decides what motion is even
expressible.

---

## 1. Choosing the layer

| Layer | Reach for it when | Motion cost | Tell that you chose wrong |
|---|---|---|---|
| **DOM + CSS** | Text is the content. Reading order matters. State is discrete (open/closed, page N). | Compositor-only: `transform`/`opacity` free, everything else reflows. | You are animating 60+ elements, or writing rAF to move divs. |
| **Inline SVG** | Geometry the reader is meant to *read* — a dial, a chart, a path, a hand-drawn frame. Needs to scale and stay crisp. | Cheap under ~2k nodes. Per-frame `d` rewrites are fine at low element counts. | Node count climbs past a few thousand, or you want per-pixel effects. |
| **Canvas 2D** | Many cheap marks (particles, trails, ink strokes) with no hit-testing and no accessibility need. | One draw call budget per frame; you own the clear. | You need depth, occlusion between marks, or lighting. |
| **WebGL / Three** | Depth, occlusion, instancing past ~1k bodies, or any per-pixel pass (edge detect, grain, displacement). | Real: a build step, a render loop, a reduced-motion path, and a still frame that must survive without it. | You used it for a hero image that a single `<img>` would carry. |

**The layer is a declaration.** Write it at the top of the case README and let
`verify_case.py --layer` check the page actually uses it. A case that claims
`webgl` and ships divs is the failure this rule exists to catch.

**Hybrid is normal, and the split is usually the same one:** the world in
WebGL, the chrome in SVG, the text in DOM. `ink-crowd` runs exactly this —
one WebGL2 canvas, 15 inline SVGs for the hand-drawn UI, real DOM text on top.
Depth belongs to the canvas; anything the reader must select, read, or tab to
belongs to the DOM.

---

## 2. Fonts are part of the layer

Measured across the reference set:

| Site | `@font-face` count | preload |
|---|---|---|
| CO'WATCH (`focus.itshassco.com`) | 69 | 7 |
| overheardhq.com/partnership | 8 | 14 |
| ibuongiorno.com | 4 | 0 |
| ink-crowd.vercel.app | 0 (draws its own type) | 0 |
| **every case in this skill** | **0** | **0** |

A system font stack (`Didot`, `Helvetica Neue`, `ui-monospace`) is a reliable
generated-page tell and no gate in `design-slop.md` catches it — A6 checks the
size *ratio*, never the face. Ship a real face, or draw the type yourself as
`ink-crowd` does. Falling back to the system stack is a decision to be argued
for in the README, not a default.

---

## 3. Ink render — measured from `ink-crowd.vercel.app`

A complete, transferable recipe for "hand-drawn 3D". Every number below came
out of the shipped bundle, not from taste.

### 3.1 The bodies are primitives you never see as primitives

Ten capsules per figure, `CapsuleGeometry(radius, length, 7, 18)`, one
`InstancedMesh` per part type:

| part | count | radius | length |
|---|---|---|---|
| head | 1 | .145 | .16 |
| torso | 1 | .19 | .38 |
| upperArm | 2 | .075 | .30 |
| foreArm | 2 | .068 | .24 |
| thigh | 2 | .082 | .42 |
| shin | 2 | .076 | .42 |

Other rig offsets: `ankleY .078`, `hipX .085`, `shoulderY .32`,
`shoulderX .155`, `headGap .21`. Figure ≈ 1.75 world units tall.

This is the exception to "code primitives can't do human figures". It works
**because the capsules are never shaded** — only their silhouette survives the
post pass, so the reader gets a contour, never a stack of pills. Shade them and
the trick dies immediately.

### 3.2 Two noises, and only one of them moves

```glsl
// Static lumpiness keyed to the figure: every body reads as its own drawing.
// Kept low frequency so it bends the contour rather than roughening it.
float warp = vnoise(p * 1.7 + vec3(seed * 11.7)) - 0.5;
// Per-redraw wobble.
float boil = vnoise(p * uFreq + vec3(seed * 7.3)
                    + vec3(uStep * 3.77, uStep * 2.11, uStep * 5.31)) - 0.5;
p += n * (warp * uWarp + boil * uBoil);
```

The seeded `warp` is what stops 88 instances reading as 88 copies — it is
per-figure and *static*. The `boil` is the only animated term. Splitting
"variety" from "liveliness" into two separate noises is the whole idea.

| material | color | boil | freq | warp |
|---|---|---|---|---|
| body | `#ffffff` | .011 | 2.2 | .013 |
| shadow | `#0a0a0a` | .07 | 2.6 | — |

The shadow boils **6× harder** than the body. Ground contact is where the hand
shows.

### 3.3 The boil clock is 11 Hz against a 60 fps render

```js
kn.uStep.value = Math.floor(clock.elapsedTime * 11);   // jm = 11
```

Motion stays at 60 fps; the *line* is redrawn 11 times a second. That is
traditional animation shot on fives, and it is the single number that makes it
read as drawn rather than rendered. Frame-differencing the video cannot
recover it — the displacement is sub-pixel and buried under camera motion
(measured: 95% of frames differ, autocorrelation flat, no periodic peak). Read
the source for numbers like this; a pixel trace will not give them to you.

### 3.4 The outline is depth-discontinuity only

Three render targets (color, depth, normal) → fullscreen quad:

| uniform | value | meaning |
|---|---|---|
| `uWidth` | 2.7 | line weight in px |
| `uT0` / `uT1` | .14 / .32 | depth-edge smoothstep band |
| `uNormalEdge` | **0** | normal-based creases **off** |
| `uGrain` | .012 | paper tooth |
| `uNear` / `uFar` | 1 / 100 | depth linearization |

`uNormalEdge: 0` is the design decision, not an oversight — with creases off a
body has no interior line at all, so it reads as a hollow white shape and the
only lines in the frame are silhouettes and overlaps. **Depth is carried
entirely by occlusion.** (`design-slop.md` B6 says this in words; this is the
same claim with a number on it.)

### 3.5 Line weight breathes in blocks, not per pixel

```glsl
// blocks rather than per pixel: a pen bearing down
// and easing off, instead of static on the edge.
float j = hash21(floor(gl_FragCoord.xy / 22.0) + uStep * 13.0) - 0.5;
float w = uWidth * (1.0 + j * 0.22);
```

22 px blocks, ±22%, resampled on the boil clock. Per-pixel jitter reads as
noise; block jitter reads as pressure.

### 3.6 The shadow and the void are the same primitive

A 28-segment disc with a per-vertex `aEdge` (0 at centre, 1 at rim) so only the
rim wobbles, and noise sampled **on a circle** so there is no seam:

```glsl
// noise on a circle keeps the wobble seamless at the seam.
float a = atan(p.z, p.x);
float w = vnoise(vec3(cos(a), sin(a), 0.0) * uFreq + vec3(uStep * 3.31 + seed * 9.13)) - 0.5;
p.xz += (p.xz / r) * w * uBoil * aEdge;
```

Per-instance `aTint` fades a shadow toward white and `discard`s above .995, so
a figure's shadow dissolves as it falls. The hole in the ground is the same
ellipse, hard-edged and scaled up — **one primitive doing two jobs** (ground
contact, and the thing that swallows you). That economy is the design, and it
costs one geometry.

### 3.7 The palette is binary

Measured off the reference frames: near-white `#fefefe`/`#fdfdfd`/`#ffffff`
≈ 79%, pure black `#000000` ≈ 16.5%. Mid greys peak at **n=89 pixels** — they
exist only as stroke antialiasing. No greys, no colour, no shadow ramp. Every
case in this skill instead runs an off-white ground plus `#171717` plus a
spread of greys; that spread is what makes them look designed-by-default.

### 3.8 The hand-drawn chrome is SVG, and it is parameterised

`fi(el, kind, {radius, jitter, width})` redraws a wobbly `path` on
`ResizeObserver`, `stroke-linecap`/`linejoin: round`:

| element | kind | radius | jitter | stroke-width |
|---|---|---|---|---|
| stat rule | line | — | 2.2 | 2.6 |
| card frame | box | 16 | 2.6 | 2.8 |
| keycap | box | 7 | 1.1 | 1.7 |
| panel | box | 12 | 2.0 | 2.2 |

Jitter scales with the element: a keycap wobbles at 1.1, a card at 2.6. A
single global jitter would make the small parts look broken.

---

## 4. Two opposite motion contracts, both correct

| | `overheardhq.com` | `ink-crowd.vercel.app` |
|---|---|---|
| frames that differ | 60/504 (**88% still**) | 3402/3581 (**95% moving**) |
| arrival | 167 ms grid, no entrance animation | continuous 60 fps |
| what carries it | accumulation; stillness is the spec | the drawn line itself |

Do not carry one page's motion contract to the next brief. Measure the
reference and state which contract the case is under, in the README, before
building. A case was built and then thrown away because that step was skipped.
### Shipping type into a single file

A case is one HTML file with no network, so the only way to ship a real face is
to subset it and inline it. `scripts/subset_fonts.py` does both:

```bash
python3 scripts/subset_fonts.py list          # open-licensed faces on this machine
python3 scripts/subset_fonts.py pack --out /tmp/faces.css \
    Grot=Inter-Variable Ital=InstrumentSerif-Italic Mono=IBMPlexMono-Regular
```

It emits `@font-face` blocks with the woff2 base64-inlined; paste them at the
top of the `<style>`, before `:root`. Measured on `cases/press-stack`: three
faces, an ASCII-plus-punctuation subset, **43 KB raw**. That is the whole cost
of not looking generated.

Two rules the tool enforces for you:

- **Only OFL and Apache faces are searchable.** The macOS system serifs and
  grotesques — Didot, Bodoni, Georgia, Futura, Helvetica — are licensed for
  system use and must never be embedded in a file you hand to anyone. They are
  deliberately absent from the listing.
- **`--text-from` on a built page is a trap when the copy lives in JS.** Script
  tags are stripped before the charset is taken, so a page that builds its
  headlines in JavaScript subsets to almost nothing and renders tofu. The tool
  warns below 60 characters; take the default set instead.

