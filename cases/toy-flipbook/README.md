# Case · toy-flipbook

A studio hero whose centrepiece is a handheld console you **turn with the mouse**. It is not a 3D
model and not a video: four pre-rendered yaw poses, hard-cut like a flipbook, on a deliberate
stop-motion jitter clock. Spin it fast and the toys on the desk get kicked off the table.

`index.html` — single file, rAF, no framework. Four frames and five toys as WebP in `img/`.
Ladder **rung 3** (vanilla rAF + springs; the "3D" is entirely pre-rendered).

Origin: ported from **`inflatable-chrome-toystudio`** ("TOYBOX"), a Vite + React page built with
this skill — its source comments cite `handfeel.md` directly. React was only
the wrapper: the loop already ran on refs and wrote `element.style` sixty times a second. The port
found and fixed one real bug, recorded in §5.

This is the worked example for **rotation in depth without a renderer**, and for a pair of
assertions where each one is satisfied by the other's failure mode.

---

## 1 · 设计系统

### Tokens

| Role | Value | Where |
|---|---|---|
| ground | `#f3efe8` → `#e9e3d8` | a `120% 70%` radial from above, so the top is lit |
| paper | `#e7e2d6` | the pills behind three headline words |
| accent | `#dcc8ef` | one lilac pill — **one word**, "Studio" |
| depth | `#cde6d4` | the mint blob, the only thing on the deepest parallax layer |
| ink | `#17150f` | type, logo chip |
| mark | `#ffe94d` | the footer tag, and nothing else |

Two accents, each used exactly once. The lilac says which word matters; the yellow says where the
studio's name is. Everything else is paper.

### Type

| | Size | Face |
|---|---|---|
| headline words | `clamp(34px, 5.6vw, 64px)` | Space Grotesk 500 |
| "The" | `clamp(28px, 4.4vw, 50px)` | **Gochi Hand** — the one handwritten word |

All three faces are SIL OFL 1.1, subset to the characters this page renders and inlined, so the case
makes no network requests.
| nav | 11px, 1.6px tracking, 700 | Space Grotesk |
| footer | 10px, 1.4px tracking | Space Grotesk |

Measured ratio **4.6×**. The headline is set as individual pills rather than a line of text, which
is what lets each word take its own entrance delay (`0.35s + 0.12s × index`) and its own hover
rotation. A single text node could do neither.

### Section shapes

**One.** Single-screen hero, verified with `--min-shapes 1`. This exemption is for a hero demo, not for a page.

---

## 2 · 动效系统

### Rung and what would force a climb

Rung 3, and this case is the cleanest argument in the skill for **not** climbing to rung 6. The
object visibly rotates in depth, which is normally the one requirement that forces a real renderer.
It does not here, because the rotation is bounded: the turnaround only ever swings between
three-quarter poses. Four bitmaps cover the whole range a user can reach. A glTF model, a scene
graph and a render loop would buy the ability to face head-on — which the art direction explicitly
does not want, because the head-on frame breaks the illusion.

### The flipbook

```
FRAME_SEQ = [0, 5, 6, 7]     // yaw ≈ -40°, +25°, +40°, +55°
```

The sheet has eight frames; four of them are near-duplicates of their neighbours. Scrubbing through
all eight makes the middle of the sweep feel stuck, because two frames apart is no visible yaw step.
**Curate the sequence to frames with a real step between them** — the frame count is a motion
decision, not an export setting.

Two rules make it read as stop-motion rather than as an image swap:

1. **The cut is hard.** `Math.round(p)` picks one frame; it gets `opacity: 1` and every other gets
   `0`. There is deliberately no `transition` on `.tb-frame`. A crossfade here turns the whole thing
   into a dissolve and the claymation read collapses.
2. **The jitter is held.** A position/rotation offset is re-rolled at **11 Hz** and held in between,
   against a 60fps render. Continuous per-frame noise reads as a vibration; a held low-rate re-roll
   reads as a hand physically re-placing the object between exposures.

The scrub itself is a spring (stiffness 55, damping 0.9), so the flipbook has momentum: flick it and
it carries past a frame and comes back.

### Everything else moves off `centered`

One number — `p / (FRAME_COUNT - 1) - 0.5`, the turnaround's position in the range −0.5…0.5 — drives
the whole scene, each layer at its own depth:

| Layer | Gain on `centered` |
|---|---|
| mint blob (deepest) | `-260px`, counter-moving |
| headline line 1 | `170 × -0.55` |
| headline line 2 | `170 × 0.8` |
| console | `150px`, `13°`, scale up to 1.08 |
| desk toys | `110px × depth`, depth 0.6–1.15 |
| nav / footer | `-34px` / `+44px` |

Lines 1 and 2 have **opposite** depth signs, so the headline shears as the console turns. That is
the cheapest possible 2.5D cue and it costs one minus sign.

### Desk toys

Each toy owns a gravity-driven hop spring. A fast spin (`|scrub velocity| > 2.2`) gives each toy a
6% chance per frame of being kicked upward at 120–180 px/s. Gravity is 900 px/s². On contact the toy
bounces at 35% of its impact speed and squashes proportionally, with the squash decaying over about
ten frames. `transform-origin: 50% 100%` puts the squash at the contact point, which is the
difference between a body landing and a sprite scaling.

### Reduced motion

Only the entrances are on a clock, so only they are cut. The turnaround waits for the pointer.

---

## 3 · 判据

```bash
python3 scripts/verify_case.py cases/toy-flipbook/index.html --min-shapes 1 --flipbook
```

| Leg | Asserts | Measured here |
|---|---|---|
| 1 · **hard cut** | across a real 60-sample pointer sweep, every sample has exactly one frame at opacity 1 and nothing in between | **0/60** soft |
| 2 · **continuous scrub** | that same sweep visits every frame, in order, skipping none | 4/4 visited, 0 skipped |
| 3 · held jitter | the jitter re-rolls between 4 and 25 Hz | **10.0 Hz** over 108 samples |
| 4 · toys are kicked | a wheel spin past the threshold lifts toys off the table **and** squashes them on landing | peak \|v\| 5.7, 3/5 airborne, 2/5 squashed |

Legs 1 and 2 are the pair. A crossfade satisfies continuity and fails the cut. A control that snaps
straight to the end pose satisfies the cut and fails continuity. Only a real flipbook passes both.

**Proved by breaking it:**

| Broken copy | Result |
|---|---|
| `transition: opacity 250ms` on `.tb-frame` | FAIL — "19/60 samples had a frame part-way lit" |
| `JITTER_FPS = 240` | FAIL — "re-rolls at 60.0 Hz — per-frame noise" |

---

## 4 · 可以照搬 / 不许照搬

### 可以照搬（机制层）

- **The whole flipbook rig.** Stacked absolute-fill images at opacity 0, one set to 1 by
  `Math.round` of a spring, no transition. This is the general answer to "it has to rotate in depth
  but I do not want a renderer".
- **Curating the frame sequence.** Ship the frames with a real step between them, not everything
  the exporter produced.
- **The held-jitter clock.** Re-roll at 8–12 Hz, hold in between. This is what separates stop-motion
  from vibration, and it is three lines.
- **One driver, many gains.** Derive a single normalised position and give every layer its own
  multiplier, including negative ones. Opposite signs on two lines of the same headline is the
  cheapest depth cue available.
- **Hop springs with contact-point origin.** Gravity, a bounce coefficient, an impact value that
  decays over ~10 frames, and `transform-origin: 50% 100%`.
- **Reading `getComputedStyle` in a probe** when the thing under test is whether something is
  animating. See §5 #2.

### 不许照搬（皮层）— the reasoning transfers, the values do not

- **The cream/lilac/yellow palette.** What transfers: a near-neutral paper ground with **two**
  accents used exactly once each, one to mark the important word and one to mark the studio name.
  The hues are this studio's.
- **One handwritten word in a geometric headline.** What transfers: a single face change is a
  stronger emphasis than any weight or colour change, and it works because it is *one* word.
  Gochi Hand is a choice.
- **The console, the cartridge, the donut.** Someone's art direction and someone's renders.
- **`FRAME_SEQ = [0,5,6,7]`.** Correct for this turnaround sheet. Yours will differ.
- **Copy, nav labels, "Press J for ?".** Brand.

---

## 5 · 踩过的坑

1. **A bounce that could never fire, for two years, in shipped code.** The landing branch read
   `s.v = s.v < -30 ? -s.v * 0.35 : 0`. But `s.v` is *positive* on the way down — the toy is
   falling — so the condition was never true and every toy stopped dead on contact. The comment
   above it said "bounce, then rest" and the code did only the second half. Nobody noticed because
   a toy that lands and stops still *looks* fine; you only miss the bounce if you know it was
   supposed to be there. `--flipbook` leg 4 is what found it, by asserting the squash rather than
   the movement. Fixed to `s.v > 30`, plus an `impact` value that decays over ~10 frames, because
   **a squash that lasts one frame of contact is the same as no squash** — it is real in the
   numbers and invisible on screen.

2. **The first version of leg 1 was vacuous, and a broken copy proved it.** It read
   `el.style.opacity` — the *inline* value, which is what the loop writes. A `transition` on opacity
   interpolates between inline values, so the inline read jumps straight to the target and reports a
   perfect hard cut for a 250ms dissolve. The deliberately-broken crossfade copy passed. Reading
   `getComputedStyle(el).opacity` catches it: 19 of 60 samples land mid-transition. **A probe that
   reads what the code wrote cannot test whether the screen agrees.** This is the same species as
   the probe-only lesson in `AUTHORING.md`, one layer down.

3. **A low-probability effect needs a driver that overshoots the threshold, or the assertion is
   untested.** The toy kick needs `|scrub velocity| > 2.2` *and* wins a 6% per-frame roll. A pointer
   sweep across the stage peaks at about 2.2 — right on the boundary — so the first version of leg 4
   reported 0/5 and could not distinguish "the mechanism is broken" from "the test never triggered
   it". The wheel adds straight to the scrub velocity and reaches 5.7. The oracle now **prints the
   peak and fails if it never cleared the threshold**, so a leg that did not run says so instead of
   silently passing or silently failing.

4. **Only four of the eight exported frames are in the repo.** The other four are near-duplicates
   the sequence never visits. 4.3 MB of PNG became 317 KB of WebP: half from dropping frames nobody
   sees, half from the encoder.
