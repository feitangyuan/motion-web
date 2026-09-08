# Image Asset Pipeline — 图片资产怎么造出来

`image-plane-3d.md` starts at "each asset ships with measured `w/h/cx/baseline`". **This file is the
step before that**: turning generated / sourced plates into cutouts that a camera can trust, and the
budgets that decide whether an asset is usable at all.

One rule governs the whole file: **every number in the runtime comes out of a script, never out of a
hand-edit.** `elements.json` is a build artifact. If you find yourself nudging a `baseline` to make
something sit right, the bug is upstream.

> Documented case (2026-08, heritage-ruins scroll scene): 19 source plates → 20 cutouts → ~52 placed scene objects,
> one perspective camera. `scripts/make-element-alpha.py`, `scripts/make-lineart-alpha.py`,
> `scripts/measure-scale.mjs` in that project are the working reference implementations.

---

## §1 Keying: distance from *this image's own* background, not luminance, not white

Plates come off an image model as **opaque RGB on near-white paper** (measured 252–253). Two instincts
both fail:

- **Luminance keying eats the pale washes.** A thin wet-in-wet wash is bright; threshold it and the
  subject loses its own edges.
- **Hardcoding "paper = white ≥ 249" fails the moment one plate came from an earlier batch.** In the
  case project `lark.png` was on warm paper `#F8EEDD`, saturation 0.11 — above any fixed saturation
  dead zone. The whole image was kept as pigment: **coverage 100%**.

Estimate the background **per image, from its own border**, then key on distance:

```python
edge = np.concatenate([rgb[:8].reshape(-1,3), rgb[-8:].reshape(-1,3),
                       rgb[:,:8].reshape(-1,3), rgb[:,-8:].reshape(-1,3)])
bg   = np.median(edge, axis=0)            # median: unaffected by a stroke that runs off the edge
dist = np.linalg.norm(rgb - bg, axis=2)
alpha = np.clip((dist - DEAD) / SPAN, 0, 1)   # DEAD = 7.0, SPAN = 42.0
alpha = np.where(alpha < 0.035, 0.0, alpha)   # kill paper grain
alpha = ndimage.median_filter(alpha, size=3)  # kill isolated specks
```

`DEAD` is the dead zone the paper's own grain lives in; `SPAN` is how far past it counts as fully
opaque. White paper and warm paper pass through the same two constants.

**`coverage` is the gate, and it must be printed.** Store it alongside `w/h/cx/baseline`:

| coverage | verdict |
|---|---|
| ~100% | keying failed — background was kept (wrong `bg`, or `DEAD` too small) |
| ~0% | keying failed — subject was thrown away (`DEAD` too big, or the plate is nearly empty) |
| 20–60% | normal for an object plate |

A silent keying failure looks fine in the file browser and only shows up in the scene as a giant
translucent rectangle. Print the number every run.

---

### §1b The near-white studio plate: two signals, then un-premultiply

§1 keys against the plate's *own* background because most plates aren't on pure white. When a plate
genuinely is a white-studio render, a threshold cut leaves a halo and an ML matte is overkill. Two
independent signals added together do it analytically:

```python
WHITE_FLOOR, WHITE_CEIL = 235, 250      # luminance ramp: 250+ is background, <235 is subject
FEATHER_SAT = 12                        # RGB max-min; protects bright *coloured* pixels
```

1. **Luminance ramp** — alpha falls from 1 to 0 across `WHITE_FLOOR → WHITE_CEIL` instead of switching at
   one value, which is where the hard edge comes from.
2. **Saturation guard** — a pixel can be bright *and* be the subject: gilt, vermilion, a lit highlight.
   Gate the ramp on `max(rgb) - min(rgb) < FEATHER_SAT` so anything with real colour keeps its alpha.
   Skipping this is how gold leaf and red lacquer get eaten out of an otherwise perfect cutout.
3. **Un-premultiply** the survivors — `rgb = (rgb - 255 * (1 - alpha)) / alpha` — or every semi-transparent
   edge pixel carries a share of the white backdrop and the cutout glows against a dark scene.

Gate the result on the same printed `coverage` number as §1. The formula is cheap enough to run on a
whole batch, and its failures are legible (too much coverage = the ramp is too low; halo = you skipped
step 3).

## §2 Crop to the alpha bbox — the empty margin *is* the 「贴上去的」 look

Plates carry huge empty margins. A draw rect that is mostly empty reads as a pasted rectangle even when
the alpha is perfect, because the eye picks up the *frame*, not the paint. Crop to `alpha > 0.06`'s
bounding box plus a small margin (4 px).

**Exception — band elements.** Ground bands and distant ridges are *bands*: they must bleed off the top
and bottom of their own frame and be soft-collected by the shader, not hard-cut to a bbox. Keep an
explicit exempt list:

```python
BANDS = {"ground-band", "ridge"}     # crop x only; keep full y
```

---

## §3 Line art is a different asset: alpha = ink, RGB = one flat ink colour

Line art arrives as dark strokes on opaque paper. Do **not** ship it that way and blend it with
`multiply` — **canvas 2D's `multiply` degrades to plain drawing over a transparent destination**, so
the white paper gets painted as a ~52% white wash over half the frame. (In three.js the equivalent trap
is `image-plane-3d` §5 / the project's FINDINGS 二/三.)

Fix at the asset:

```python
alpha = np.clip((PAPER - lum) / PAPER, 0, 1)   # PAPER = 250.0; linear ramp keeps pencil-weight variation
rgba[..., :3] = INK                            # (62, 52, 40) — one flat colour, matches the type layer
rgba[..., 3]  = alpha * 255
```

A **linear ramp, not a hard threshold** — hard-thresholding throws away the hatching weight that makes
it read as drawn rather than traced.

---

## §4 Measure the placement metadata in the same pass

Never a second script, never by eye. From the cropped alpha:

```python
col = a.sum(axis=0)
cx  = (col * np.arange(w)).sum() / col.sum() / w        # painted centroid, not bbox centre
row = a.sum(axis=1)
nz  = np.nonzero(row > row.max() * 0.02)[0]
baseline = nz.max() / h                                  # ground line: lowest row carrying real paint
```

Then `elements.json` is `{w, h, cx, baseline, coverage}` per asset — see `image-plane-3d.md` §2 for how
the runtime consumes them.

### The field that is missing until it bites you: the crown

`baseline` says where the thing *stands*. Nothing says where it *ends*. And `makeElement` derives the
plate from `planeH = realH / baseline`, which silently assumes **the paint reaches the top of the frame**.

> **`realH` is how tall the thing should be, not where it paints to.**

Documented failure: a dust layer was hung at `moundH = 21.5`, and floated **4.5 m above the mound's
summit in open sky** — `mound.png`'s first row with `alpha > 90` is at 0.168, i.e. 17% of the plate is
empty air. Anything you attach to an element (dust, flags, birds, annotations, callout anchors) must be
positioned from **the plate's real position + a measured anchor in the texture**, never from the height
constant you typed at placement time. Measure and ship a `crown` (and any other anchor you hang things
from) the same way you ship `baseline`.

---

## §5 Sprite atlases: same batch, same sun

A 4-up sheet beats four files — same batch means same scale and same light direction, which is exactly
what `image-plane-3d.md` §7 spends a uniform correcting for. Rewrite the UVs into atlas space rather
than slicing images (`uv.setX(i, (uv.getX(i) + q) / cols)`); `hit.uv` then comes back already in atlas
space, so alpha-precise hit testing keeps working for free.

---

## §6 Resolution budget is **per element**, and the tightest one governs

There is no global "don't dolly more than X". Each element has its own source width, its own distance
and its own on-screen size. Measure them all at the tightest camera position and read the worst row.

```
ratio = source_px_width / on-screen_px_width(dpr 2)      # >1 = headroom, <1 = being enlarged
```

Documented table at the closest camera position (1440×810, dpr 2):

| element | plate px | on-screen px | ratio |
|---|---|---|---|
| ridge | 2653 | 4728 | 0.56× ← enlarging, but it's a background wash, fine |
| **outline-tower** | 878 | 1054 | **0.83×** ← **the one the user is asked to interact with** |
| wall-intact | 2426 | 2496 | 0.97× |
| pagoda-intact | 1840 | 1265 | 1.45× |
| mound | 2254 | 1071 | 2.10× |

Two lessons, both expensive:

- **Rank by role, not by ratio.** The blurriest asset in the scene was the one the whole act asks the
  user to erase. Background washes are *allowed* to enlarge; the hero of an interaction is not.
- **Measuring planes means multiplying by `scale`.** A first version read `geometry.parameters.width`
  as world width and missed `scale.x`. Walls are one plate stretched across several segments, so the
  tightest element was reported as the loosest — a 5× error in the wrong direction.

Re-run after **any** change to assets, camera path, or fov. Never copy an old table.

---

## §7 A texture's density is a function of the distance it serves

The most reusable finding about reuse. A dust plate that reads as *atmosphere* across 280 m reads as
**nothing at all** when reused for an 8 m gust — measured mean 0.936, only **3.0% of pixels below 0.8**.
Under pure multiply, `mix(1, 0.936, 1.0)` darkens by 6.4%: on cream paper that is a dozen levels. The
gain knob was run to the ceiling (uK = 1.0, the maximum multiply allows) and the frame still didn't move.

> **Reuse a texture's *structure* (grain shape, direction, spacing), never its *concentration*.**

Split the two: give the near instance a body of its own and let the texture only carve density inside it.

```glsl
mix(0.45, 1.0, smoothstep(0.99, 0.86, grain))   // 0.45 body + texture as a density field
```

Three corollaries — a near layer never inherits a far layer's settings:

- **Tiling must grow with the plane.** A plane expanding 7 m → 39 m with fixed tiling stretches one
  clump of grain 5× and reads as a smudge. Multiply the uv by the growth factor.
- **Fade the edge radially, not as a rectangle.** At close range a feathered rectangle reads as a
  sticker instantly. A gust has no edge.
- **Don't use neutral grey.** What's being kicked up is earth, not smoke; neutral grey over cream paper
  reads as overcast.

---

## §8 Provenance

Artefacts, murals, and historical scenes must come from **real sources**. AI generation of that class of
material is forgery — not a style choice, and not negotiable by deadline. Keep the licence and the URL
next to the file (`reference/LINKS.md` pattern).

Everything else — mood plates, textures, paper, grain, ornamental elements — is fair game to generate.
Keep the two piles physically separate in the repo so nobody has to remember which is which.

And keep the asset inventory a *statement of what exists*, not a *prohibition*: an inventory written as
"these are the only assets" gets read by the next session as a constraint, and it will build around a
missing asset instead of asking for it.

---

## §9 Cheap wins at the asset layer — 一张白图喂十五层

Four choices from *The Boat* (SBS, 2015; measured off the shipped files) that remove work from the
runtime entirely. All four still apply.

**Palette PNGs, not 32-bit.** Every asset ships as PNG-8 (`mode = P`) with palette alpha. Ink art has a
handful of distinct values, so an indexed palette is free quality-wise and roughly halves the bytes.
Check what your export is actually writing — a 32-bit PNG of a monochrome wash is pure waste.

**RGB constant, information in alpha.** Measured over painted pixels:

| asset | px | RGB | alpha distribution |
|---|---|---|---|
| `bg.png` | 2602×1695 | pure black | **never reaches 255** — 36% under 64, 45% mid, 19% near-opaque |
| `waves-pot.png` | 2048×256 | **pure white** | 29% under 64, 53% near-opaque |
| `fog-pot.png` | 4096×1024 | pure white | entirely 1–190 |
| `rain-02-black-pot.png` | 1024×1024 | pure black | 70% under 64 |
| `boat-01.png` | 1104×555 | ink (52,52,52) | **50.6% fully transparent, 15.4% fully opaque** — a real cutout |

Atmosphere layers carry **no colour at all**: they are one constant (white to lift, black to darken) plus
a density map in alpha. This is the same construction as line art in §3, and it is what makes the next
trick possible.

**One white master, tinted per instance.** *The Boat*'s fifteen wave layers all sample the same white
`waves-pot.png`; each layer differs only by `new Color(0.015·i, 0.015·i, 0.015·i)` on its
`MeshBasicMaterial`. Fifteen depths of aerial perspective, one file, no shader, no fog.

> This is §7 solved at the asset layer: author the **structure** once as white-on-alpha, and let material
> colour supply the concentration each instance needs.

**`-pot` in the filename is a constraint, not a note.** Every tiling texture is power-of-two
(512×256, 1024×1024, 2048×256, 4096×1024) because WebGL1 will not `RepeatWrapping` an NPOT texture. Put
the constraint in the filename so nobody has to remember it. Non-tiling plates stay whatever size the
art is.

**Ship a second, smaller asset set rather than capping the camera.** `Image.rewriteTabletURL()` swaps
`images/` → `images-tablet/` on tablet and mobile. Measured: `013-021/01.png` is 1389×450 desktop and
**1056×342** tablet — a flat 0.76×. Combined with `setPixelRatio(min(devicePixelRatio, 1.75))`, that is
the entire resolution strategy, and it costs nothing at runtime.

Also worth copying: `texture.minFilter = LinearFilter` (no mipmaps — keeps ink edges crisp and sidesteps
NPOT mip rules), and a URL-keyed texture cache with an explicit `dispose()` that drops geometry,
material and texture together (`scene-streaming.md` §4).

---

## §10 Checklist

- [ ] Background estimated per image from its own border median — no hardcoded paper colour
- [ ] `coverage` printed for every asset; nothing at ~0% or ~100% ships
- [ ] Cropped to the alpha bbox + margin; band elements exempted from vertical crop
- [ ] Line art shipped as alpha=ink / RGB=flat ink, never as opaque-on-paper
- [ ] `w/h/cx/baseline/coverage` written by the script, never hand-edited
- [ ] Every anchor you hang something from is **measured** (crown, not `realH`)
- [ ] Per-element magnification table re-run after any asset / camera / fov change; planes multiplied by `scale`
- [ ] The hero of each interaction checked for headroom specifically
- [ ] Reused textures re-authored for their new serving distance (body + density field), not just re-gained
- [ ] Provenance-restricted material physically separated from generated material
- [ ] Export format checked — palette PNG for limited-value art, not 32-bit by default (§9)
- [ ] Atmosphere layers authored as one constant colour + density in alpha, tinted per instance (§9)
- [ ] Tiling textures power-of-two, and named so (§9)
- [ ] A second smaller asset set for tablet/mobile, plus a DPR cap (§9)
