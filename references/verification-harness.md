# Verification Harness — 判据台架

`affordance.md` §9 lists *which* numbers to print. This file is the machinery that makes those numbers
trustworthy, and the ways it lies when you build it wrong.

Everything here was paid for twice: once by shipping a wrong number, once by believing it.

> Documented case (2026-08, heritage-ruins scroll scene): ~20 probe scripts against a scroll-driven three.js scene.
> Reference implementations: `scripts/shot.mjs`, `afford-shot.mjs` + `afford-oracle.py`,
> `ambience-test.mjs`, `measure-scale.mjs`, `erase.mjs`.

---

## §0 The one thing that makes a harness harmful

A previous version of this project shipped `verify-frame.py` — six quantitative quality metrics, one
composite verdict. **It gave 6/6 to every single version a human later rejected.** It was deleted.

> **A general "quality score" is worse than no test.** It converts "I don't like it" into "the tests
> pass", which is the exact opposite of what you built it for.

An oracle is legitimate only when it **encodes one specific complaint**:

| Legitimate | Harmful |
|---|---|
| 「只有一个能点开」 → % of a grid each target owns | "interaction score: 8.2" |
| 「有拼接感」 → mean R−B per asset batch | "cohesion: pass" |
| 「音效像环境噪声」 → dB remaining 0.25 s after the hand stops | "audio quality: 6/6" |

The final verdict on anything aesthetic stays with a human looking at it. The oracle's job is to stop
you from *re-litigating a measurable thing by eye* — nothing more.

### The first run of a new oracle tests the oracle

Before an instrument is allowed to report on the thing you built, feed it **an input whose answer you
already know** and check it comes back right. If it doesn't, fix the instrument.

This is not paranoia. The `3d-scene-studio` skill keeps a running table of instruments caught lying —
**four so far, one of them its own**: a black-frame watchdog reporting "100% black" on correctly rendered
frames (it was reading a discarded buffer under `preserveDrawingBuffer: false`); a camera probe reporting
"the camera swung 171° while the car turned 9°" (a point transform fed a relative vector); a screenshot
set where 10 of 11 images differed between identical runs (one shared page, so particle age and decal
buffers leaked forward); and a pixel readout that raised a reference target by 33% (a double sRGB
conversion). Full table and the round-trip technique: **`3d-scene-studio/SKILL.md` 「信读数之前先验证仪器」**.

Every failure in §3, §4, §6 and §7 below is a variant of the same thing. This rule is the general form.

---

## §1 The probe surface is a design contract

Build these into the page from the start; retrofitting them costs more than they cost.

```js
window.__seek = (p) => { scrollP = p; render() }   // jump the timeline
window.__hold = (t) => { held = t }                // pin a transition at an arbitrary t
window.__clock = (t) => { ambienceT = t }          // pin every ambient clock
window.__noDemo = true                             // suppress auto-demos (a flag, not a function)
window.__noHint = true                             // suppress hints WITHOUT suppressing the demo
window.__probe = () => ({ boxes, windows, hitAtPointer })
window.__state = () => ({ wipeLevel, markedCount, netLevel })   // state exits, see §5
```

Four properties that matter more than the exact names:

1. **Time is settable, not just readable.** Anything driven by wall-clock — weather, breathing, particle
   spawn, idle animations — needs a pin. Without it, half of every A/B difference is "the cloud moved".
2. **Transitions can be frozen mid-flight.** A headless screenshot costs ~1 s, so an unpinned check only
   ever catches the end state — and an end-state-only test gives a hard cut full marks. This is exactly
   how a **52%** size jump at a shared-element handoff survived a passing suite (`affordance.md` §10).
   Measure at `t = 0.002`.
3. **Suppressors are orthogonal.** `__noDemo` and `__noHint` must be separate switches, because the
   on/off diff in §3 requires *everything except the one thing* to be identical between the two renders.
4. **State exits exist for interactions** (§5).

Match the harness viewport to the real viewing environment — `deviceScaleFactor: 2` if people watch on
Retina. A hairline that measures fine at dpr 1 can disappear at dpr 2 and vice versa.

---

## §2 `__seek` lies about anything with a lifetime

Teleporting the timeline is correct for static layers and **wrong for any layer where each object has
its own timer** — falling type, particles, physics, staggered releases.

Jumping to `p` means every object releases in the same frame and sits on the same fade value: the
screenshot shows *one uniformly half-transparent curtain*. Scrolling there for real shows glyphs
detaching one after another. Measured: `__seek` frames at p=0.835 and p=0.855 were nearly identical;
really-scrolled frames differed obviously. **Every timing parameter tuned off the teleported frames was
wrong.**

Give the harness a real-scroll mode and use it for those layers:

```
--scroll <from>     # step 0.008 per 40 ms ≈ 6.5 wheel notches/sec
```

---

## §3 The general oracle: render the same frame twice with one thing toggled, and subtract

This is the workhorse. It applies to pixels and to audio identically.

```js
await page.evaluate((t) => { window.__clock(t); window.__noDemo = true }, T)   // pin every clock
await page.evaluate((p) => window.__seek(p), P)
await page.screenshot({ path: 'on.png' })
await page.evaluate(() => {                                    // hide ONLY the thing under test
  const st = document.createElement('style'); st.id = 'hint-off'
  st.textContent = '.callout{display:none!important}'
  document.head.appendChild(st)
})
await page.screenshot({ path: 'off.png' })
```

Notes that are not optional:

- **Inject a stylesheet rather than editing elements** — pseudo-elements (`::after`) are unreachable from JS.
- **Canvas-drawn marks need a code switch** (`__noHint`), and that switch must leave everything else
  running. In the case project the demo had to keep playing between the two shots, otherwise the diff
  captured *which glyphs were flipped*, not the bracket under test.
- **Same clock value in both renders.** Say it twice because it is forgotten every time.

### Determinism is a precondition, and randomness poisons it invisibly

Each impulse in the audio layer started at `nz.start(t0, Math.random() * 4)` — a random offset into a
noise table. The offset itself was correct design; the consequence was not: **every later layer's
sampling position shifted with it**, and the whole measurement rests on subtracting two renders sample
by sample.

It cost two false conclusions: a seal impulse whose peak moved **7.3 dB** between identical runs, and a
「①翻面比钤印还响」 alarm for a sound that had not been touched — it was simply sampled from a different
part of the table. The first investigation blamed an unrelated layer.

> **Any per-event randomness must advance a per-event deterministic sequence, not a global one.**

```js
const phaser = (i) => (start[i] += 0.618034 * 4) % 4    // golden-ratio step, per event
```

Now a disabled event's phase does not advance at all, and the subtraction is clean. The same rule covers
visual jitter, particle seeds, and any `Math.random()` reachable from a render path.

---

## §4 When the frame is always moving, a before/after diff measures the camera

Two screenshots at different scroll positions, subtracted, produce **the edge map of the entire
painting** — every silhouette in the scene rimmed in white — because a breathing camera moved everything
half a pixel. The erased stroke you were looking for is buried in it.

Documented: this trap was written in a code comment *by the same author* and then walked into twice.

> **If anything in the scene moves on its own, leave the screen. Measure the state.**

---

## §5 State exits: how you measure an interaction at all

Headless has no pointer at a meaningful position, and screen diffs are poisoned (§4). So the page must
expose what the interaction *did*, not what it looked like:

```js
window.__wipeLevel()   // fraction of the erase mask cleared
window.__marked()      // how many glyphs the user has actually brushed
window.__figHit()      // which target the current pointer is over
window.__mouseAt(x,y)  // drive a real pointer
```

Then drive a real pointer through a real gesture and print a table:

| p | cursor | mask | ink |
|---|---|---|---|
| 0.60 | — | 0 | 0 |
| 0.655 | crosshair | 9.8% | 7.7% |
| 0.71 | crosshair | 9.7% | 7.6% |
| 0.735 | — | 0 | 0 |

This caught a bug that two rounds of screenshot review missed entirely: a curtain rebuilt itself every
few notches and wiped every mark the user had made. **The first interaction-state run found it.**

### Mask covered ≠ content removed

Two different numbers. The mask is a whole cloth; the drawing is a few lines on it. A horizontal stroke
covered *more mask area* than the diagonal demo stroke but removed **2.3× less ink** (7.4% vs 16.9%),
because eaves are horizontal lines — running along one only scuffs that one line, while cutting across
diagonally passes through three. **Weight each cell of the mask by the artwork's own alpha** before you
decide whether a stroke was worth anything.

---

## §6 Don't race the clock in headless

Screenshots stall rAF. Waiting `N` seconds for a stroke to advance measures nothing — between two shots
the page barely ran, the "time since release" accumulator never reached its threshold, and the run
concluded 「抹完再也不长回来」.

Same class of error: an auto-demo whose phase accumulated `dt`. The main loop clamps `dt` at 0.05 for
backgrounded tabs, so below 20 fps the demo drifted later and later — first measurement said it took
5.2 s to start a stroke that was authored at 2.6 s.

> **Drive state directly (`page.evaluate` to set the stroke to a fraction of its path); compute phase
> from an absolute timestamp, never from accumulated `dt`.**

---

## §7 Sampling rate: ≤ 1/5 of the event, and never one window

A cloud-shadow probe sampled one frame every 6 s and concluded 「cloud shadow has no effect on
elements」. The texture's dark blobs are 0.042 of texture width wide — one blob crossed a point in
almost exactly 6 s. **Sampling a 6-second event every 6 seconds measures aliasing, not signal.** At
1.2 s per frame every expected swing showed up.

The other half is worse because it looks rigorous: a 12-row parameter sweep, each row one 90-second
window starting at t=0. Changing the repeat changes each element's starting uv, i.e. a different scan
line — so the table's 0% / 47% jumps were recording *which cloud happened to be overhead*, not the
parameter.

> **Estimate the event's own duration first. Sample at ≤ 1/5 of it. Never tune off one window's
> statistics.**

---

## §8 Peak is not weight; and never measure a line against its own neighbourhood

Two refinements that changed conclusions:

**Report peak Δ *and* the count of pixels over threshold.** A 1 px line and a 2 px line have the same
peak but twice the visual weight. The first affordance oracle reported only the strongest pixel, passed
a hint at Δ 20.7, and the user still couldn't see it. With both numbers the same marks read
`Δ31.0 / 76 px`, and "thin" became visible to the harness.

**Never measure a mark against the background beside it in a single image.** Done that way, one bracket
reported Δ 78 — twice any other — because it happened to sit exactly on the boundary between mound and
sky. The oracle had measured *the background's own edge*. Always on/off diff (§3), with a neighbourhood
radius small enough not to reach the content: `AFFORD_R = 8` was required where 16 ran onto the glyphs.

---

## §9 The ruler has a resolution floor

A whole-frame motion meter (`pace.mjs`) downsamples to 120×68 to report "how much changed per notch".
At that size **a 2 px spire and a line of 20 px type both vanish**. A change that fixed a real ordering
problem moved the number from 1.87 to 1.85 — not because it didn't work, but because the ruler cannot
see either object involved.

> **When a number says nothing happened, first ask whether the ruler can resolve the thing.**
> Then fall back to the only other legitimate check: lay the frames out in a row and look at the order.

And when a measured number disagrees with a human's earlier judgement: **change the parameter nobody
ever looked at, not the one somebody sat in front of the screen and tuned.**

---

## §10 Harness hygiene

- Scripts live **inside the project** (module resolution, dev-server origin, relative asset paths).
- Use whatever headless binary is actually installed — check before assuming (`playwright-core` pointing
  at the cached `chrome-headless-shell`, in the case project; `puppeteer` was not present).
- Remove any gesture gate / splash before measuring (`document.getElementById('gate')?.remove()`).
- Collect `console` errors and `pageerror` on every run and print them — a clean regression sweep is
  half "the numbers are right" and half "nothing threw".
- Keep every oracle script. They cost nothing to re-run and they are the only record of what a number
  meant.
- Note which probes are one-shot investigations vs. regression sweeps, and don't re-run the one-shots.

---

## §11 Two neighbouring rulers live in `3d-scene-studio`

This file is **methodology** — how to design an oracle that doesn't lie. Two concrete instruments for
three.js pages live in the `3d-scene-studio` skill and are worth reaching for rather than rebuilding:

| Need | Where | What it gives |
|---|---|---|
| "did anything render at all", draw-call / triangle budget, console, blank-canvas detection | `3d-scene-studio/references/runtime-visual-verification.md` (`scripts/inspect-three-scene.mjs`) | `WebGLRenderer.info` against a budget + objective pixel statistics. **Also reports `gpu.softwareRendered` — when true, any FPS or frame-time reading from that run is fiction.** |
| Anything a still frame cannot see | same file, 「Build an automated player」 | A gameplay oracle (two runs differing by **one bit** of input, asserting the intended proposition) and a handfeel oracle (camera lag, peak angular velocity — *the nausea metric* — overshoot, framing, stability, and frame-rate independence) |

The second row carries a finding this file's §0 only half-states. On one documented project, **six
adversarial visual critics scored three full rounds and found zero gameplay bugs** — wrong-way detection,
no mobile controls, black frames, a pause menu that hung the race permanently, a ten-second mobile crash
were **all** found by the author playing it. Visual oracles are structurally blind to everything a still
frame cannot show.

> The dividing line stays the same in both files: **a script answers questions with one right answer**
> (does it make you sick, does it change with frame rate, is the risky line actually faster);
> **a person answers whether they like it.** Don't push all of "handfeel" onto the person.

The same skill's failure list independently reached this file's §0 conclusion — a global statistics
script scoring 6/6 on rejected work (`3d-scene-studio/references/stylized-web3d.md` #10). Two projects, two teams, same
wall.

## §12 Frame-rate independence is a claim; run 30 / 60 / 120 and diff

Every follower and spring in `handfeel.md` §7 is written as `1 - exp(-k·dt)` *specifically* so the
result does not depend on frame rate. That is a claim about the whole loop, not about the formula —
one `x += d * 0.1`, one `dt` you forgot to multiply by, one physics step that runs once per frame,
and the claim is false while every formula in the file still looks correct.

**Method:** run the same scripted input at three fixed steps and compare against the finest one.

```js
for (const fps of [30, 60, 120]) {
  const dt = 1 / fps;
  reset(seed);                                  // identical initial state
  for (let i = 0; i < STEPS * fps; i++) step(dt);
  record(fps, subject.position, eventTimes);
}
// assert against the 120fps run
```

Thresholds that held on a real build: position drift **< 0.5 world units**, event-time drift
**< 0.2 s** over a full run. Both are loose on purpose — this oracle is looking for the difference
between "independent" and "not", which is usually a factor of two, not a rounding error.

This is the cheapest oracle in the file (no browser, no pixels, no screenshots) and it catches a class
of bug that only shows up on someone else's machine.

---

## §13 Scope a metric to where the promise applies — a global smoothness score bans intentional discontinuity

A jerk / smoothness statistic over *every* frame silently encodes "motion should always be continuous".
If the design is hold-and-snap — a pose that lands, holds, then leaves — that metric scores the
intended thing as broken and pushes every fix toward mush. **A metric that is wrong about the design's
own premise is worse than no metric** (§0), and this is the most common way it happens.

Documented case: a p95 inter-frame acceleration check over a whole piece rated the reference material —
the thing being matched — as terrible, because the reference is built on arrivals and holds.

**Fix — exempt the neighbourhood of the intended discontinuities, stay strict everywhere else:**

```js
const ACC_WIN = 0.14;                       // seconds around a planned arrival/hold
const mask = new Array(a.length).fill(true);
for (const t of plannedHolds) {
  const i = Math.round(t * fps);
  mask.fill(false, Math.max(0, i - ACC_WIN * fps), Math.min(a.length, i + ACC_WIN * fps));
}
const jerkOutsideAccents = a.filter((_, i) => mask[i]);
```

The general rule: **the exempt set has to come from the schedule, not from the data.** Exempting the
frames that happen to score badly is fitting the ruler to the result. Exempting the frames where the
timeline says an arrival was planned is measuring the promise that was actually made — holds and snaps
are design; inter-frame jitter is a bug; the only thing that separates them is whether the schedule
says something was supposed to land there.

Also count reversals rather than sign changes when the question is "does it look jittery": a raw
sign-change count treats a sub-pixel wobble as a direction change. Count only reversals whose monotone
run exceeds a stated fraction of the subject's own size (0.5% of body height on the documented build).

---

## §14 Dynamic occlusion is a different oracle from static visibility

Static visibility asks "is the target painted on screen" (§8). A moving scene has a second failure the
first cannot see: things that pass *between* camera and subject. Project every dynamic object's bounds
into NDC, test containment against the subject's ellipse, and budget the result as **duration**, not
as an instantaneous count:

- single continuous occlusion **< 2.0 s**
- total occluded fraction of the run **< 8%**

Reporting only "% of frames occluded" hides the failure that matters — one three-second blackout and
sixty scattered single frames give the same average and are not the same experience. This is the same
shape as §8's "peak **and** area", applied on the time axis.

---

## §15 The churn floor: does anything actually move?

Every other oracle in this file asks whether a *mechanism* exists. None of them
ask the question a person asks in the first two seconds, and twice in a row a
page passed the whole harness and was rejected on sight with "there is no
motion". Both times the same measurement settled it.

`scripts/measure_churn.py` drives a real wheel and reports the share of on-screen
elements whose `transform`, `opacity` or `stroke-dashoffset` changed at least
once. Measured:

| page | churn | mid-flight | dominant property |
|---|---|---|---|
| blink.trade | 62 % | 210 | opacity, 235 elements |
| a rail that translated with frozen children | 13 % | 2 | — |
| the same page after splitting copy per word | 48 % | 20 | transform 92 / opacity 83 |
| a sticky stack with no dwell | 20 % | 37 | — |
| the same stack with one viewport of dwell | 42 % | 60 | transform 56 / opacity 50 |

Three things follow.

**Use a real wheel.** `scrollTo()` teleports past the arriving-and-leaving
window, which is exactly where the motion lives. Three separate oracles here
passed dead pages because they teleported: `--rail`, `--stack`, and the hover
probe in the floor.

**Churn alone is not enough, and neither is mid-flight.** A page that snaps
between states scores high churn and reads as a slideshow; a page with a
beautiful ramp on four elements scores high mid-flight and reads as empty.
Assert both, and they will pull against each other the way §0 wants.

**A low opacity count means the copy is not split.** On every reference measured
for this skill, opacity on per-word spans is the dominant device — 235 of
blink's 246 moving elements. A page whose churn is all `transform` is moving
containers.

Run it on the reference *before* building, and keep its number. "48 % against
the reference's 62 %" is a fact you can act on; "it feels a bit static" is not.

## §16 Checklist

- [ ] No composite "quality score" anywhere; every oracle encodes one stated complaint
- [ ] `__seek` / `__hold` / clock pin / `__noDemo` / `__noHint` / state exits all present
- [ ] Harness viewport and dpr match the real viewing environment
- [ ] Layers with per-object lifetimes verified by **real scrolling**, not teleport
- [ ] All clocks pinned to the same value in both halves of every A/B
- [ ] No `Math.random()` on a render path that a diff depends on — per-event deterministic phaser instead
- [ ] Interaction verdicts come from state exits, not screen diffs
- [ ] Mask coverage weighted by the artwork's alpha before judging a stroke
- [ ] Sampling interval ≤ 1/5 of the event; conclusions never drawn from a single window
- [ ] Visibility oracles report peak **and** area over threshold
- [ ] When a metric says "no change", the ruler's resolution was checked first
- [ ] Every new oracle's first run was a known-answer round trip against itself
- [ ] No timing claim quoted from a software-rendered run
- [ ] Anything a still frame can't show has an automated player, not another visual critic
- [ ] Every `exp(-k·dt)` claim run at 30 / 60 / 120 fps and diffed against the finest
- [ ] Smoothness / jerk metrics exempt the *scheduled* arrivals, and the exempt set comes from the timeline, not the data
- [ ] Occlusion budgets stated as duration (longest single, total fraction), not as a frame percentage
