# Timeline Orchestration — 多轨滚动时间轴

`choreography-arc.md` picks the arc. This file is about what goes wrong once a page has **many tracks
sharing one scroll axis** — art, copy, camera, interactability, atmosphere — and each one is individually
reasonable.

Every failure below was found by measuring "how much did the frame change per wheel notch" across the
whole timeline and looking at the flat stretches.

> Documented case (2026-08, heritage-ruins scroll scene): 4 acts over 900vh, ~8 tracks, `scripts/pace.mjs` as the meter.

---

## §1 Read the schedule horizontally, not per layer

The deadest stretch of the piece — six consecutive notches at Δ 1.1–1.8 where the neighbours ran 8–28 —
had no slow layer in it. It had three plateaus that happened to overlap:

| track | window | what it was doing in that stretch |
|---|---|---|
| glyphs scattering | 0.796 → 0.885 | long tail; most had gone in the first 20% |
| `uNight` | 0.82 black → 0.88 lift | flat platform, two whole notches |
| camera | decelerating into its 0.88 keyframe | velocity → 0 |

> **A dead beat is rarely one slow layer. It is several layers' flat sections landing on the same beat.**
> Every curve reviewed alone looks fine. Lay them out as rows against one scroll axis and the hole is
> obvious.

Fix by moving two of them (scattering ended at 0.830, `uNight` lift moved to match); the camera's
deceleration stayed, because decelerating into the end of an act is authored, not a bug.

---

## §2 Easing lives in exactly one layer

Scroll → act progress had a `smoothstep`, and each element's own window had another. **They multiply**:
the middle gets squared, both ends flatten. Measured: a tower was 2% eroded at p=0.41 and 85% eroded at
p=0.45 — the entire object disappeared inside four notches. *Adding* easing produced a harder cut than
no easing at all.

> **Ease at the element layer, where each thing has its own rhythm. Keep the timeline itself linear —
> it is time, and time should not speed up and slow down.**

---

## §3 Easing evens out the parameter, not what the eye reads

The peel front moved at constant speed **along the plate's height**. What the eye reads is **painted
area**. The tower is wide at the base and tapers, so the top 20% of height is almost no pigment:
constant-speed meant three notches of "nothing happening" followed by two notches where the whole tower
vanished. A `k ** 0.62` exponent spread the *area* loss evenly across the scroll.

The same correction, per-segment, for a stroke drawn in stages: window width per segment =
`0.85 × that segment's ink + 0.15 × equal share`.

- Ten **equal** segments gave the finial — 6.1% of the drawing's total ink — a full window: one notch
  measured Δ 1.83, i.e. a third of the sequence spent drawing a needle.
- **Pure** ink weighting gave the finial 0.058 of a notch — short enough to fall between frames.
- The 0.15 equal-share blend put it at 0.19 of a notch: a flick of the brush, not a pause.

> **Anything that sweeps along an axis owes one question: is uniformity on that axis uniformity on
> screen?**

Corollary from the same act: two rings and the tip at the very top were deliberately **not** given
separate stops. At fingernail size on screen, three stages read as three twitches; one continuous flick
reads as a single closing stroke.

---

## §4 One window, one event — a fade eats everything beside it

A curtain was authored as "fade in over 0.69–0.83", with the per-column falling in the same window.
The falling was invisible. Four frames spanning five notches were indistinguishable apart from camera
drift.

> **An opacity change consumes every other motion sharing its window.** The eye reports 「有个东西在淡进来」
> and nothing else.

Rules that follow:

- A fade-in gets the **first ~10%** of a segment (in the case project: 0.685–0.72, about one notch).
  The rest of the run belongs to the thing you actually want seen.
- Three things to say in one act = **three consecutive segments** (fall → brush → scatter), not three
  windows stacked and stirred with alpha. Stacking them is precisely what produces "just a scroll with
  some fades".
- Two annotations must not overlap: end one exactly as the next begins, or only the fading one is read.

---

## §5 A keyframe with zero velocity guarantees a dead beat after it

The seam between two acts measured Δ 2.92, the lowest non-interactive value in the piece. The cause was
not content:

```
CAM_PATH dolly segment 0.26 → 0.54 (nine notches), smootherstep
smoother(0.0714) = 0.0033  →  a 22 m dolly advanced 7 cm across the first notch
```

Everything tried inside the curve failed by construction: cubic `smoothstep` gives 32 cm; splitting the
segment makes the first notch 7× faster (23 cm) **and adds a second velocity-zero keyframe**; starting
earlier is eaten by the element windows' equally flat heads.

> **Any curve whose velocity is zero at a keyframe makes the following notch or two nearly static. That
> is the curve's definition, not a tuning error.** The longer the segment, the longer the flat head.

Two legitimate responses:

1. Accept it when the stillness is authored ("the picture does not move; the camera starts when it
   becomes a place") and **fill the beat with a different track**.
2. **Check whether some layer's time is simply wrong before adding anything.** In this case the act
   title was still firing at `0.20`, a stale value from an earlier structure, while the act itself began
   at 0.26 — announcing the next chapter over a frame that was still the previous one. Moving it to 0.26
   put its 0.045-wide ramp exactly in the hole: **2.92 → 5.34**, with nothing new built.

> When a beat is empty, look for something that should already have happened there and has the wrong
> timestamp, before authoring new content.

---

## §6 The apparatus must not outlive its content

The curtain's glyphs were all gone by 0.830. The rod they hung from, the rule beside them, and the line
inviting you to brush them stayed at full opacity until 0.876. The sky had already lifted, there was not
one glyph left, and an empty rod still hung there asking to be touched.

> **Frames, rods, captions, numbering, "scroll to continue" — anything that *contains* content must exit
> on the content's schedule.** Never back-derive it from the next act's start.

The bad number had been derived from the following act's opening (0.905 → 0.902). Directionally sensible,
and it **fails silently**: the moment the content's length changes, the container is wrong, with no error
and no visual except an empty fixture.

---

## §7 An instruction cannot precede its referent

Copy reading 「这条轮廓是推出来的，不是挖出来的。**抹掉它。**」 was fully legible at 0.61, while the
outline it refers to was still on its fifth of nine strokes. **"Erase it" named something not yet
drawn** — and worse, the sentence's fade-in shared a window with the drawing (§4), so the only thing
actually happening in the act got eaten by a fade.

> **Draw → say → hand off. Three abutting segments, none overlapping.**
> An invitation has a precondition: first the *it*, then the sentence, then the hand.

---

## §8 Every act owes one money frame (定妆帧)

The complaint was 「图还没铺满字就说完了，真到铺满的时候字又滑走了」. Measured, the two curves were
offset for the entire act: the art reached full coverage at 0.15, while the copy stood complete only over
0.07–0.08 and was gone by 0.13. **The act contained no frame showing the finished picture with the
finished words** — which is the one frame it existed to produce.

Print all tracks against scroll position as one table and look for the row where everything is at 1.0:

```
   p     art    date  title  copy1  copy2  credit   touchable
  0.14   0.965  1.00  1.00   1.00   1.00   1.00     1.00   ← money frame opens
  0.19   1.000  1.00  1.00   1.00   1.00   1.00     0.26   ← money frame closes
  0.22   1.000  0.32  0.55   0.09   0.09   0.32     0.00
```

**The interactable window is one of the rows.** Fixing the copy timing had pushed the dwell to 0.165–0.225
while the "you can touch this" gate still closed at 0.135 — so the user arrived at the money frame, reached
out, and found a dead picture. Reported as 「那个效果没了」; nothing had been deleted.

> **Move a dwell, recompute its interaction window in the same edit.** Same rule as `affordance.md` §2,
> arrived at from the other direction.

---

## §9 Stagger copy blocks; don't fade a screenful at once

Five blocks entering across 0.012–0.07 with starts **0.008** apart read as one slab of text dropping at
once. Restaggered to **0.022** apart (≈0.18 of a screen), ordered by reading order *and* by weight, with
the lightest block last:

| block | in | out |
|---|---|---|
| dateline | 0.012–0.045 | 0.194–0.236 |
| title | 0.028–0.068 | 0.200–0.243 |
| body, sentence 1 | 0.050–0.090 | 0.190–0.232 |
| body, sentence 2 | 0.072–0.112 | 0.190–0.232 |
| credit (smallest) | 0.095–0.135 | 0.194–0.236 |

Two details worth stealing: a multi-line body block **splits into its own sentences** for entry, with the
parent only governing presence and exiting slower than its children; and the lightest block goes last on
purpose, because by then the art is 90% complete and whatever lands next will land *on* the picture — so
let it be the smallest thing.

---

## §10 Threshold dissolves: the histogram of the threshold map *is* the schedule

A line drawing dissolving into a colour scene was authored as "use the paper grain as a threshold, so the
boundary bleeds like watercolour". Measured per notch:

| notch | mean-frame Δ | % of frame changed |
|---|---|---|
| 0.15 → 0.18 | 1.88 | 4.4% |
| **0.18 → 0.21** | **0.01** | **0.0%** |
| **0.21 → 0.24** | **23.48** | **45.3%** |

One notch mathematically frozen, the next flipping 45% of the frame — the hardest cut in the piece, from
code that reads like a soft dissolve. Two causes stacked:

1. **The threshold map had no distribution.** Its values spanned only 0.447–0.518; the shader mapped that
   to ±0.013 of perturbation against a `smoothstep` width of 0.30. Effectively **one global threshold** —
   the "bleed" was a whole-frame crossfade.
2. **The mapping wasted its range.** `edge = amt * 1.35 - 0.175` with `smoothstep(0, 0.30, ·)` saturates
   above `amt ≥ 0.346` and below `≤ 0.124`. The effective interval was 0.222 wide — **half a notch** of
   the 3.5 notches designed.

> **When an image is used as a threshold, what matters is not how it looks — it is its histogram.**
> Area flipped as the threshold sweeps = the map's cumulative distribution. Bell-shaped = one hard cut
> plus two long tails. For equal area per notch the threshold map must be **uniformly distributed** —
> histogram-equalize it (replace each pixel by its rank in the image). Turning the noise "up" does nothing.

Two companions, required together:

- **Use the full range:** `T = amt * (1 + 2W) - W`, leaving soft-edge width `W` at each end, so `amt` 0
  and 1 are genuinely clean and every step between them changes something.
- **Keep the timeline linear** (§2). Softness comes from the shader's bleeding edge, not from easing the
  driver. The original `1 - smoothstep(0.15, 0.26, p)` had zero derivative at both ends: first and last
  notch nearly frozen, the middle one doing half the work — 6.5× between fastest and slowest.

After the fix, the same stretch measured 11.3 / 9.5 / 14.9 / 9.2 — 1.6× between fastest and slowest, no
frozen notch, no 45% cliff.

## §11 「灵动 vs 飘」 is a stillness ratio, not an easing problem

Measured on a reference piece everyone agreed felt alive: **51% of its adjacent frame pairs were
near-identical at the pixel level** — about 15 distinct states per second on a 30fps timeline. The
rebuild that read as 「飘」 held only **13%**, at forty times the baseline motion. The whole gap was
stillness.

> **Easing changes how fast the source is read. It never changes how often a new state appears.**

No curve closes a stillness gap, which is why "再调调缓动" fails on this complaint specifically. Two
knobs actually move it:

1. **A drawing clock.** Keep rendering at 60fps, but quantise the animated *quantity* to a coarser grid
   so the picture only changes N times a second:
   ```js
   const RATE = 15;                        // distinct states per second
   const tq = Math.floor(t * RATE) / RATE; // feed tq to the curves, not t
   ```
   Apply it to the layers carrying the performance, not to camera drift or ambience — a quantised camera
   reads as jank, a quantised subject reads as animation.
2. **Ease between anchors, not merely at them.** Landing at velocity zero on each anchor buys stillness
   only *at* the anchors; on the documented build that capped out at ~21% because a couple of dozen
   anchors is all a piece has, and the source runs straight through everywhere in between. Easing the
   time map between every pair of anchors (smootherstep rather than near-linear) acts on every frame.

**Measure it**: `stillness = fraction of adjacent frame pairs whose max per-pixel delta < ε`. Print it
beside the money-frame count (§8); it is a one-number answer to a complaint that otherwise gets argued.

**Reconciling with §5.** §5 says a zero-velocity keyframe guarantees a dead beat after it; this section
says stillness is what reads as alive. Both are true and they are not the same stillness: §5's is a layer
*drifting through* a plateau while nothing else takes over — nobody is looking at anything. §11's is a
pose that has **arrived and is being held** while the next event is loaded. The test is whether the
stillness is the subject of the frame. If the eye has somewhere to rest, hold longer; if it doesn't,
you have a dead beat.

---

## §12 Checklist

- [ ] All tracks laid out as rows against one scroll axis; no beat where several plateaus coincide
- [ ] Easing in exactly one layer; the driving timeline is linear
- [ ] Sweeps weighted by what the eye reads (area / ink), not by the geometric axis
- [ ] No window contains a fade **and** something else you want seen
- [ ] Every velocity-zero keyframe's following beat is filled by another track — or authored as stillness
- [ ] Containers exit on their content's schedule, never back-derived from the next section
- [ ] No copy references something that isn't drawn yet
- [ ] Each act has a money frame where art + copy + interactability are simultaneously complete
- [ ] Any dwell change recomputed the matching interaction window in the same edit
- [ ] Copy blocks staggered ≈0.02 of scroll apart, lightest last
- [ ] Threshold maps histogram-equalized; mapping uses its full range
