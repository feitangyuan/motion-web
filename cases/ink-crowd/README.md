# Case · ink-crowd

**Declared render layer: `webgl`.** Verified by
`python3 scripts/verify_case.py cases/ink-crowd/index.html --layer webgl`.

A page about how hand-drawn 3D is actually made, drawn with the technique it
describes. Hand-written WebGL2 — no framework, no CDN — so the case verifies
offline and the pipeline is readable end to end.

Reference: `https://ink-crowd.vercel.app/` (a browser game by @pallavmac,
posted at `https://x.com/pallavmac/...`, clip `refs/3-into-the-void.mp4`,
59.7 s at 60 fps). It is the only reference in this skill's set whose render
layer DOM cannot reach: WebGL2, four shader programs, 161 DOM nodes, zero
images, zero web fonts.

Full recipe with every measured number: `references/render-layer.md` §3.

---

## 0 · Why this case exists

Seven cases shipped before it, all DOM + CSS, all on the system font stack.
None of the references are built that way. The gap was never a missing
technique — it was that nothing in the skill *asked* what a page is drawn
with, so every brief silently resolved to divs. This case is the first one
authored under `render-layer.md`, and `verify_case.py --layer` now checks the
claim instead of trusting the README.

---

## 1 · Where the numbers came from

| Value | Source |
|---|---|
| capsule rig (10 parts, radii, lengths) | reference bundle, `hi` / `oi` / `rt` tables |
| `boil .011 · freq 2.2 · warp .013` (body) | reference bundle, body material |
| `boil .07 · freq 2.6 · #0a0a0a` (shadow) | reference bundle, shadow material |
| boil clock 11 Hz | reference bundle, `uStep = floor(elapsedTime * 11)` |
| `uWidth 2.7 · uT0 .14 · uT1 .32 · uGrain .012` | reference bundle, post-pass uniforms |
| `uNormalEdge 0` | reference bundle — creases deliberately off |
| 22 px blocks, ±22 % | reference bundle, line-weight jitter |
| binary palette (79 % white / 16.5 % black) | `measure_frames.py palette` on the clip |
| 95 % of frames differ, no periodic hold | `measure_frames.py` + a frame-diff pass |

The last row matters as a negative result: frame-differencing **cannot** find
the 11 Hz boil, because the displacement is sub-pixel and buried under camera
motion. Autocorrelation over the calm windows is a smooth decay with no peak.
The number only exists in the source. A pixel trace would have produced a
confident, wrong answer.

---

## 2 · Pipeline

```
pass 1   instanced capsules  ─┬─ COLOR_ATTACHMENT0  flat white / #0a0a0a
                              ├─ COLOR_ATTACHMENT1  view normal (unused, kept
                              │                     so uNormalEdge can be raised)
                              └─ DEPTH_COMPONENT24  sampled by pass 2
pass 2   fullscreen triangle  ── depth discontinuity → line, block jitter, grain
```

620 instances (62 figures × 10 capsules), one draw call. One unit capsule mesh
is rebuilt per instance in the vertex shader from `(radius, halfLength)`, so
six part types cost one VAO rather than six.

Shadows are drawn **first, with depth writes off**, so they never create a
depth discontinuity and the outline pass leaves them uncontoured — which is
what makes them read as shadow rather than as another drawn object.

---

## 3 · What the still frame owes

Motion off (`prefers-reduced-motion`), the page must still be the page: the
boil clock pins at `uStep = 0`, the crowd holds a pose, nothing is hidden.
Verified — `reduced-motion: {hidden: 0, total: 18}`.

The palette is binary on purpose: `#ffffff` paper, `#000000` ink, one grey
(`#0a0a0a`) that exists only inside the render. No CSS greys, no radius, no
shadow. The reference measures 79 % white / 16.5 % black with mid-greys
peaking at 89 pixels — they are stroke antialiasing, not a palette.

Type is Inter Variable, subset to Latin and inlined as a 31 KB woff2. The
system stack was the tell `design-slop.md` never caught; `--layer` now fails a
case that ships on it.

---

## 4 · Graveyard — four bugs, and what each one actually was

**The whole scene rendered upside down.** `lookAt` built `right` as
`(f.z, 0, -f.x)`, which is the negation of `cross(up, backward)`. Negating
`right` also negates `up = cross(right, forward)`, so the scene came out
rotated 180° about the view axis. Symptom read as "the heads are black blobs",
which sent me looking at the capsule mesh. The debug pass found it in one
shot: the raw colour buffer showed shadows floating above the figures, which
only happens if the ground is at the top.

**Lesson:** a screenshot said "geometry is broken"; the buffer said "the camera
is upside down". `__probe.pass(n)` — raw colour, linear depth, edge magnitude —
now ships in the case, and belongs in anything with a post-process pass.

**The head lived inside the torso.** Placing the head at
`pelvis + shoulderY + headGap` puts it below the torso capsule's top
(`pelvis + len + radius`). The rig numbers are right; the assembly was wrong.
Head now sits at `pelvis + torso.len + torso.r × 0.86`.

**Arms were invisible.** `shoulderX .155` is *inside* `torso.r .19`, so hanging
arms never break the silhouette. They now splay to `torso.r + upperArm.r × .72`.
The measured value was not wrong — a reference figure's arms are hidden at rest
too, and only appear as it walks — but a crowd of mostly idle figures needs
them.

**Shadow rim wobble was 6× too strong.** I multiplied by an extra 6.0 that is
not in the reference. The reference displaces by `uBoil` of the *local unit
disc*, i.e. ±3.5 % of the radius. Mine was ±70 % and read as lumpy, not drawn.

**Pointing at a figure did nothing.** The pointer ray was intersected with the
ground plane `y = 0`, but a figure is 1.75 units tall: aiming at a body sends
the ray *through* it and onto the ground far behind. Measured — aiming at the
crowd in the upper right produced a target 11.2 units past them and **zero**
followers, while the screen centre gave 27. Near the horizon the ray goes
almost parallel and the hit point runs away entirely. Fixed by intersecting at
torso height (`AIM_Y 0.95`) with a horizon guard, and by widening the reach
from 6.2 to 16 so no part of the visible ground is deaf.

**Lesson:** the counter said "27 following" and I read that as working. It was
working *in one band*. The assertion has to be positional — the crowd centroid
must close on the aim from **every** corner of the canvas — which is now
`verify_case.py --follow`. A user found this before the oracle did.

---

## 5 · Instruments this case changed

- `measure_structure.py` now records `render_layer` (canvas contexts, SVG shape
  count, libraries, DPR). It could see none of this before, which is why four
  captured references sat in the bank with no note of what drew them.
- `verify_case.py --layer <dom|svg|canvas2d|webgl>` asserts the declared layer
  and gates web fonts (`--draws-own-type` for a page that draws its own
  letterforms).
- `verify_case.py`'s real-input smoke test now includes body text in its
  signature and accepts `canvas` as a hover target. A canvas-only hover and a
  changed readout both used to report "nothing happened".
