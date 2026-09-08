# Case · string-clock

An analogue clock whose hands are **slack elastic strings**. Both ends are in exactly the right
place — the knot at the centre, the tip on the true angle — and the 300 units in between refuse to
be a line. You can grab any tip, or the knot itself, and fling it.

`index.html` — single file, no build, no dependencies. Ladder **rung 2** (vanilla rAF + springs).

Reference: a video clip by **@itshassco** ("the most useless watch face", `CO'WATCH!`), pulled and
frame-measured per the Video Reference Protocol. Every number below was measured off the decoded
frames, and the method is written down in §Phase 1 so the readings are checkable.

> **Correction, 2026-09-02.** This README used to say "there is no live URL, so the page
> could not be measured." That was wrong: the author posted one in his own replies —
> **`https://focus.itshassco.com/`** ("Try it"). Nobody read the thread. The physics here was derived
> from first principles and still stands, but the palette and the control geometry should be
> re-measured against the live page. `cases/AUTHORING.md` Phase 1 now makes reading the replies a
> hard step before any frame measurement.

This is the worked example for **"a control surface can be product dialect while the page around it
is creative"**, and for an oracle whose two halves pull against each other.

---

## 1 · 设计系统

### Tokens — measured, not chosen

| Role | Value | How it was measured |
|---|---|---|
| ground | `#e9e9e9` | 90.7 % of all sampled pixels in a frame |
| surface | `#fcfcfc` | every raised pill |
| track | `#dddddd` | segmented-control bed, slider bed |
| label | `#5a5a5a` | darkest pixel inside `SYSTEM PREFERENCES` |
| muted | `#616161` | darkest pixel inside an inactive segment label |
| ink | `#141414` | hour/minute strings |
| hour ticks | `#717171` | modal grey in the dial ring |
| minute ticks | `#c1c1c1` | second modal grey |
| numerals | `#969696` | third modal grey |
| accent | `#d81b2d` | mean of the 400 most-saturated red pixels |

**Ten values, one accent, one ground.** No second surface, no border colour, no gradient anywhere.

### Type

body **14 px** · display (dial numerals) **72 px** · ratio **5.1×**. The numerals are the only large
type on the page; the wordmark is 15 px and lives at the foot of the panel, as it does on the
reference — there is no masthead. That is a creative-dialect decision — 5 of 18 award-winning
creative sites in the 32-site measurement run have no `<h1>` at all, and none of the 18 uses a
marketing-scale headline over an interactive stage.

Numerals are drawn `color:#d8d8d8` + `-webkit-text-stroke:2.5px #969696` — a hollow face without
shipping a font. The fill is deliberately non-transparent so the fallback (no `text-stroke` support)
is a light grey numeral rather than an invisible one.

### Radius / shadow → dialect

Measured on the reference at native 2× and halved:

| Control | Size (CSS px) | Radius |
|---|---|---|
| icon button | 73 × 54 | 20 (soft square) |
| MODE pill | 228 × 54 | stadium |
| swatch | 54 × 54, gap 12 | circle |
| segmented control | 296 × 41 | stadium |
| slider | 296 × 41 | stadium |
| primary button | 165 × 54 | stadium |

**Two control heights (54 / 41), two radii (stadium / 20 px), one shadow level.**

This is the interesting classification and the reason the case exists. `components.md` §1 says
creative pages measure **1** radius kind and **0** shadowed elements; product pages measure **8**
radii and **17.5** shadows. This page is **neither** — it is a *product control surface sitting on a
creative canvas*:

| Axis | This page | Reads as |
|---|---|---|
| radii | 2 | creative |
| shadow levels | 1 (on ~11 elements) | product |
| button case | sentence, uppercase micro-labels only | creative |
| nav | none at all, no CTA | creative |
| footer | 2 items, 0 links | creative |
| component vocabulary | segmented control, slider, swatch radiogroup, pill toggle | product |

The rule that falls out: **the dialect is a property of the surface, not of the page.** A page can
carry a full product component vocabulary without becoming a product page, provided the *canvas*
stays creative — one ground, no nav, no CTA, one type size that matters. Getting this wrong in the
other direction is the "像 AI 做的" complaint: product components *plus* a product canvas on work
that wanted to be creative.

### Section shapes

Two sections, deliberately: `.stage` (full-viewport, 2-column grid, no heading) and `.below`
(62ch single column, centred, `border-top`). The stage owes no heading — it is the artefact.

### Components and the states each owes

| Component | States implemented |
|---|---|
| MODE pill | rest / hover (lift 1 px) / active (scale .985) / two values |
| swatch radiogroup | `role=radiogroup` + `aria-checked`, checked ring, hover lift |
| segmented control | thumb slides on `transform`, `aria-pressed` per button, active bolds |
| slider | native `input[type=range]`, fill tracks value, value label |
| string tip | rest / hover (ring at .55 opacity) / grabbed (ring + `cursor:grabbing`) |

---

## 2 · 动效系统

### Rung and what would force a climb

**Rung 2.** Continuous input drives continuous output; there is no timeline to orchestrate and no
scroll to scrub. Rung 4 (GSAP) buys nothing here. It would be forced only by adding page transitions
or a scroll-pinned sequence around the watch.

### The schedule

| Mechanic | Trigger | Driver | Band |
|---|---|---|---|
| hand advance | wall clock | `Date` → angle | continuous |
| tip spring | angle change | `K_TIP 1600 / C_TIP 52` | ~0.25 s to settle |
| string sag | always | verlet + gravity | continuous |
| trailing bow | hand direction | `BIAS 110 px/s²` along −tangent | continuous |
| sway | `Windy` | `WIND 900 px/s²`, two beat frequencies (1.7, 0.41 rad/s) | continuous |
| grab | pointerdown within 40 units of a tip or the knot | pointer | while held |
| knot return | pointerup | `K_HUB 900 / C_HUB 40` | ~0.4 s |

### Motion tokens

```
DT          1/120 s        fixed timestep, accumulator-driven
DAMP        0.994          per step  (≈ 0.49 per second)
GRAV        1200 / 2200 / 2200   calm / normal / windy
WIND        0 / 0 / 900
K_TIP 1600  C_TIP 52       tip spring — stiff on purpose, see below
K_HUB  900  C_HUB 40
ITERS 3     STIFF 0.50     strings: soft, so it stretches
ROD_ITERS 10  ROD_STIFF 1  rods: rigid
MAX_STRETCH 3.0            per-segment cap
BIAS 110                   trailing lateral acceleration
HUB_REACH 300  TIP_REACH 380  WALL 440   (in the 800-unit dial box)
```

### Why the tip spring is *stiff* and the string is *soft*

The one decision the whole design rests on. Gravity on a spring-held point produces a steady-state
droop of `g / k`. At `K_TIP = 1600` and `g = 2200` that is **1.4 units** — 0.26° at the second
hand's radius, invisible. Drop `K_TIP` to 60 (which *feels* more like a floppy string) and the droop
becomes 37 units — **6.8° off**, and the clock is simply wrong rather than illegible. So: the
endpoint is held hard and told the truth; only the body of the string is soft. The joke survives
because a person reads the *direction of a stroke*, not the position of its endpoint.

### Why the string is elastic and not inextensible

Measured on the reference: across 51 decoded frames the red hand's traced arc length ran
**332 → 684 px** — it more than doubled while being dragged, and returned. A rigid verlet chain
(8 iterations at stiffness 0.9 ⇒ effective 0.999) cannot do that; it reads as a metal chain. So the
solver here is deliberately weak (3 × 0.5) and the *only* thing forbidding spaghetti is a hard
per-segment cap at 3× rest.

### Reduced motion

A **designed still**, not a disabled page: `restShape()` lays each string on its analytic sag —
same endpoints, same bow depth, no loop, no listeners. Nothing is hidden, nothing is frozen
mid-transition, and the time is still correct. Verified: 0 of 14 checked elements stuck hidden.

---

## 3 · 判据

```bash
python3 scripts/verify_case.py cases/string-clock/index.html --strings
```

The floor, plus a domain oracle whose halves **pull against each other** — that tension is the
point. Over-damp the string and (b) dies; loosen the tip and (a) dies.

| Assertion | Threshold | Measured |
|---|---|---|
| (a) tip angle vs. true analog angle, 8 times × 3 hands, after settle | ≤ 1.5° | **0.00°** |
| (b) least sag (arc ÷ chord) over the same sweep | ≥ 1.12 | **1.331** |
| (c) `Rods` removes the sag | ≤ 1.03 | **1.000** |
| (c) `Rods` still points true | ≤ 1.0° | **0.00°** |
| (d) worst stretch under a real drag at 12 / 60 / 240 px per step | ≤ 3.2× rest arc | **2.47×** |
| (d) nodes leaving the dial box during that drag | 0 | **0** |
| (d) arc after release | within 4 % of rest | **0.3 %** |
| (a–d) non-finite nodes | 0 | **0** |
| (e) **free-running** worst tip error over 3 s, clock unpinned | ≤ 1.5° | **0.22°** |
| (e) free-running sag range | within [1.12, 1.60] | **1.331 – 1.359** |
| (e) free-running peak node speed | ≤ 400 /s | **33 /s** |

**(e) exists because (a)–(d) all pin the clock and settle** — the one regime a real page is never
in. Unpinned, a tip that drifts or a body that never stops sloshing shows up here and nowhere else.

**(d) uses a real pointer, not the probe.** `__probe` deliberately exposes *no* method that moves a
string: it can pin the clock, step the sim, and read state, and that is all. The oracle calls
`__probe.tipXY(key)` to find where the tip is on screen, then drives `page.mouse` through
`pointerdown / pointermove × 48 / pointerup`, and asserts `__probe.grabbing()` actually latched. This
is the direct answer to the probe-only lesson — a probe that writes state bypasses the handlers and
tests a path nobody takes.

Floor readings: type ratio **5.1** · h-overflow **0** at 320/375/414/768/1440 · 23 custom properties
referenced, **0** dead · ground `rgb(233,233,233)` · 1 `<h1>` · reduced-motion hidden **0/14**.

### The floor check this case added

`verify_case.py` now fails any page that **references a custom property nothing defines**, or whose
`body` background is transparent. See 踩过的坑 #1 — that is the failure it was written for, and all
five existing cases pass it unchanged.

---

## 4 · 可以照搬 / 不许照搬

### 可以照搬（机制层）

| Piece | What it gives you |
|---|---|
| `Hand` + `step()` + `constrain()` | a slack string pinned at **both** ends where one end is driven by data — the general shape is "an inextensible-ish curve between a fixed anchor and a datum" |
| stiff end-spring + soft body | the readout stays exact while the visual is soft. Reusable anywhere a value must be *legible at a point* and *expressive along a path* |
| `capSeg()` swept **forwards and backwards, twice** | a stretch cap that resolves in one frame instead of migrating one segment per frame |
| end nodes at ¼ weight in the projection | string tension barely moves a driven end, but a hard drag still transmits down the chain |
| `clampTo(box) → clampTo(reach)` | two clamps in that order: the artefact has an edge, *and* the string has a reach. Either alone is not enough |
| the `WALL` with `px += nx - x` | a zero-restitution boundary that injects no energy, because the previous position moves with the current one |
| `BIAS` along −tangent | the motivated asymmetry that lets a *vertical* slack string choose a side to buckle to |
| fixed `DT` + accumulator + `__probe.settle(ms)` | the same integration path for rAF and for the oracle, so a headless check and a real frame agree |
| `restShape()` | the reduced-motion pattern: recompute the *end state* analytically rather than disabling the loop |
| `--dial` as the single scale token | one length drives the SVG box, the numeral radius and the hit radius; nothing needs a resize listener |

### 不许照搬（皮层）— the reasoning transfers, the values do not

- **Ten tokens, one accent.** Not because ten is correct, but because this artefact has exactly one
  thing to say (which stroke is the seconds) and every additional hue would compete with it. Count
  the things your page must distinguish, then allow one accent per genuine distinction.
- **Two control heights.** Not 54/41 — the reasoning is that a *primary* row and an *inset* row is
  the smallest set that still reads as a hierarchy. Three heights on a panel this size reads as
  carelessness.
- **One shadow level.** Elevation here answers one question: is this pill pressable? A second level
  would imply a second kind of layering that does not exist on the page.
- **The dialect split.** Do not copy "product controls on a creative canvas" as a look. Copy the
  test: *does the canvas need nav, CTA, marketing headlines?* If no, keep it creative even when the
  controls are unmistakably product.
- **`Rods` as a mode.** The value is not a rods setting — it is shipping the *degenerate case of your
  own idea as a switch*, so a person can see what the design is refusing, and so the oracle has
  something to compare against.
- Colours, copy, wordmark, the reference's brand and its actual control names (`SOUND`,
  `Mute/System/Watch`, `Buy me a coffee`) were **not** carried over. `SWAY` and `SLACK` replace them
  because every control on this page must change the physics; a decorative control is how a case
  starts looking like a demo.

---

## 5 · 踩过的坑

Every one of these was silent. None threw.

**1 · A `*/` inside a banner comment ate the entire `:root{}`.**
The mechanism/skin banner contained the literal text `/* @mechanism */` as a pointer to the tag used
below. That inner `*/` closed the comment early; the CSS parser then treated the remaining banner
prose as a selector and consumed the **next block** — `:root{…}` — as its declaration body. Result:
23 custom properties undefined, `background: var(--ground)` invalid at computed-value time (body
transparent), and `font: 400 14px/1.55 var(--sans)` dropped whole, so the page rendered in **Times
16px** on a white ground.

It passed the entire floor. The type-ratio check reported `64/16 = 4.0` against a `>= 4.0` threshold
— it survived by a rounding hair, and would have passed outright with a 60 px numeral. What exposed
it was reading the printed `body: 16` and asking why, not any assertion.

> Fix: never write `*/` inside a comment (write `@mechanism`, not `/* @mechanism */`), and
> `verify_case.py` now fails on any referenced-but-undefined custom property and on a transparent
> body background. A stylesheet that fails to parse does not error — it *recovers*, and recovery
> eats whatever comes next.

**2 · `translateY(-40%)` put all four numerals on the hub.**
A percentage in a transform resolves against the **element's own** border box, not the container. 40 %
of a 64 px numeral is 26 px, not the intended 320 units. Four numerals, one pile, dead centre.

**3 · The same trap by a second route — and it only showed on one breakpoint.**
Fixed (2) with `translateY(calc(-0.40 * var(--dial)))`, where
`--dial: min(74vh, 100%, 760px)`. Mobile came out perfect and desktop did not, from **one
declaration**: mobile's `--dial` is `min(86vw, 560px)` — no percentage — while desktop's contains
`100%`, which inside a `translateY()` resolves to the numeral's own height, so `min()` picked ~64 px.
A token used as *both* a length and a transform argument must contain no percentage. Now
`min(74vh, calc(100vw - 470px), 760px)`.

**4 · `Rods` is not `Strings` with the slack set to 0.**
`slackRatio() → 0` made the rest length equal the chord, but a deliberately soft solver (3 iterations
at 0.5) cannot hold a taut line against gravity: rods still measured **1.108× sag**. A rigid object
needs rigid settings — `ROD_ITERS 10, ROD_STIFF 1.0`, and the loads (gravity, wind, bias) zeroed.
The oracle caught this; looking at it would not have, at that magnitude.

**5 · A one-directional stretch cap migrates the violation instead of fixing it.**
Sweeping `i = 0 … last-1` and capping each segment moves the excess *inward by one segment per
frame*. Under a 240 px/step drag the chain measured **8.30× rest arc** with the cap nominally
enabled. Sweeping forwards then backwards, twice, brought it to 2.47×.

**6 · Clamping the grab to the string's reach but not to the dial.**
`reach = R(1+slack) · MAX_STRETCH · 0.92` is 1084 units for the second hand — in an **800-unit box**.
The pointer dragged the tip clean off the canvas, and the chain sat so close to its cap total that
Gauss–Seidel could not converge in the sweeps available (**4.69×**). Clamping to the dial *first*
(`TIP_REACH 380`) and to the reach *second* dropped it to 2.47× and put every node back inside the
frame. Order matters: clamping toward the hub after a centre-clamp keeps the point inside both, by
convexity.

**7 · A live readout from a hidden browser tab is a frozen simulation.**
Opening the page in the Browser pane and reading `__probe.hand('second')` reported a **118° tip
error** and sag 2.08 — both alarming, both false. The pane was hidden, so Chrome had suspended
`requestAnimationFrame` (and throttled `setTimeout` to 1 s, which is what gave it away: the samples
were byte-identical and only `target`, computed from `Date`, moved — the error shrank by exactly
6.0°/s, the second hand's own rate). The sim was stopped; the clock was not. Re-measured in headless
Playwright: worst error **0.22°** over 20 s.

> `page-design.md` §2's rule applies to live pages too — **suspect the ruler**. Before believing a
> number read off a running physics page, confirm the loop is actually running (count rAF callbacks
> over a known interval). It did, however, expose a real gap: the oracle only ever tested the pinned
> + settled path, so a free-running block was added — see 判据 (e).

**8 · A vertical slack string has no preferred side to buckle to.**
With the tip directly above the hub, gravity is parallel to the chord and the extra length has no
reason to go left rather than right — it jitters or compresses into a spike. `BIAS` (110 px/s² along
−tangent) is the fix and it is also physically right: the hand sweeps clockwise, so the string
should trail. The reference shows exactly this — its 12-o'clock string bows *left*.

---

## 6 · 改造方向

The mechanism is "a slack curve between a fixed anchor and a moving datum, where the datum must stay
exact". Point it at:

- **A live metric.** Anchor at the axis origin, datum at the current value on a gauge. The value is
  exact; the ribbon between is soft and lags — a dashboard that shows *rate of change* as physical
  slack, without a second chart.
- **A nav rail.** Anchor at the logo, datum at the active section marker. The string re-settles as
  you scroll; the sag is the distance travelled.
- **A cursor tether.** Anchor at a card, datum at the pointer, cap the reach. The card is "still
  attached" while you drag away from it — a much cheaper affordance than a ghost preview.
- **Loading.** Anchor and datum both fixed, `slack` animated 0 → 0.6 → 0: the string breathes.
  Zero new mechanism, and it never rotates, so it reads as *waiting* rather than *spinning*.
- **`slack` as a data channel.** The slider is a design control here, but `slackRatio()` is just a
  number. Bind it to confidence, load, latency, staleness — anything where "this value is real but
  soft" is the honest message.

Raise `HANDS[].n` for smoother sag (cost is linear); the current 14/18/22 is where the Catmull-Rom
smoothing stops being visible at a 760 px dial.
