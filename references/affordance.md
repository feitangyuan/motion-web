# Affordance — 能点 ≠ 看得出能点

Everything else in this skill makes motion happen. This file is about whether a human ever finds it.

**Documented case (2026-08, heritage-ruins scrollytelling).** The user reported 「只有一尊能点开」 in three
separate rounds. Hit-testing was correct every single time — a 12px grid sweep showed the three targets
owning 9.6% / 7.3% / 4.3% of the region, and clicking the centre of each one passed. Nothing was broken.
What was missing was the **invitation**: only one of the three carried a visible mark, and that mark's
window closed 0.012 of scroll *before* the camera parked — i.e. right before the user stopped to look.

Two rounds of engineering went into the wrong half of the problem because the test only ever asked
"does it work", never "would anyone find it".

---

## §0 The false pass

A test that clicks the centre of the target and passes is the test that cannot catch this class of bug.
Centre-click measures the **mechanism**. The complaint was about **discovery**.

> **The test has to encode the user's complaint, not your model of it.**

If the user says "I can't open it" and your test says "it opens", the test is asking a different question.
Find the question they're actually asking before you change any code.

---

## §1 The three questions

An interactive element is not done until all three are answered with evidence, not confidence:

| # | Question | Evidence |
|---|---|---|
| 1 | **Is it hittable?** | Grid sweep (§9), not a centre click. Report the % of the region each target owns. |
| 2 | **Does it *say* it's hittable?** | A persistent visual mark. **A cursor change is not an invitation** — the cursor is invisible until the pointer is already on the target, so it can only confirm a guess, never prompt one. |
| 3 | **Is it still saying so at the moment the user looks?** | Affordance window vs dwell window (§2). |

Most "can't find the interaction" bugs are #2 or #3. Almost none are #1 — but #1 is the only one a
normal test suite checks, which is why this whole file exists.

---

## §2 The invitation must outlive the dwell (窗口 ⊇ 停留)

Scroll-driven pages have places where the camera/timeline **parks** — a pinned section, a held frame, a
stretch where scroll maps to almost no visual change. That park is where the user stops and looks around.
It is the only moment they will go hunting for something to click.

Every affordance live in that section must span **the entire pin**.

```
BAD    pin:        [0.64 ──────────────── 0.70]
       affordance: [0.545 ───── 0.652]
                                 ↑ dies here, just before anyone stops
GOOD   affordance: [0.545 ──────────────────── 0.715]
```

Checkable invariant: `affordance_window ⊇ dwell_window`. Compute both, compare, don't eyeball.

---

## §3 A tidiness rule must never close the last entrance

The window above was closed on purpose. The comment justifying it read: *"一个窗口一件事，标注不许去抢"* —
one window, one job; the annotation doesn't get to compete with the erase interaction that starts at 0.65.
It sounded like discipline. It was the only door into a whole page of content.

Before enforcing any self-imposed rule of the form *"only one X at a time"* / *"don't repeat the invitation"* /
*"this section already has an interaction"* — check what it deletes. **Two invitations in different screen
regions do not compete**; the one in the upper-left and the three in the lower-middle were never in conflict.

---

## §4 描出来的，不是淡进来的

Eyes track *change*, not presence. A mark that fades in is, on every single frame, a static object at a
different opacity — peripheral vision files it under "background" and skips it. A mark that **draws itself**
has a moving edge, and a moving edge is the one thing peripheral vision cannot ignore.

Use `stroke-dashoffset` on an SVG path — see `pattern-recipes.md` #14.

**Trap that costs an hour:** `vector-effect: non-scaling-stroke` moves the dash pattern into screen space,
so a `stroke-dasharray` sized to the path's user-space perimeter never completes the draw — the line
stops halfway and stays there. If you need a ring stretched non-uniformly (`preserveAspectRatio="none"`),
keep the stroke in user space and accept the width anisotropy: at ±25% stretch a 1.9px hairline renders
1.4–2.4px and nobody can see it, whereas a draw-on that never finishes is visible to everyone.

---

## §5 Multiple invitations stagger; they don't spawn

N marks appearing at once read as *"the UI just spawned some controls"*. The same N staggered ~0.15–0.20
apart read as *someone marking them one at a time* — and the eye follows the sequence to the end, which is
precisely what makes marks #2 and #3 get seen at all.

```js
// per mark i, driven by the shared window amount a
const ai = smoothstep(i * 0.17, i * 0.17 + 0.66, a)
setOpacity(el, smoothstep(0, 0.4, ai))            // ink lands in the first 40%…
el.style.setProperty('--draw', (1 - ai).toFixed(3)) // …then the line is drawn across the rest
```

Ink first, line second. If both track `ai` linearly, the stroke is half-drawn *and* half-transparent at
the midpoint — which is to say nothing has visibly happened yet.

---

## §6 The mark hugs the painted pixels, not the box

Transparent margin is the norm: PNG cutouts, SVG with padding, sprite atlases, `object-fit: contain`.
A ring drawn on the element's box circles a lot of air, and for a wide subject in a tall box it circles
mostly air. Measure the **painted** bbox once, offline, and ship it as data:

- threshold `alpha > 200`, not `> 0` — most exported art carries faint non-zero alpha everywhere, so a
  naive `Image.getbbox()` returns the full canvas and you will believe it
- require ≥1% coverage per row/column before counting that row/column as painted (kills stray pixels)

Same pass, same threshold as the asset metadata in `image-plane-3d.md` §2 — measure `cx` / `baseline` /
painted bbox together and ship one JSON per asset.

At runtime, project the **four corners** of that rect — not centre + size. Going through the corners means
a mirrored / rotated / flipped element is handled by its own transform and you never branch on `flipX`:

```js
// paint = [u0, u1, v0, v1] in the element's own 0–1 space
function paintedScreenBox(mesh, paint, camera, out) {
  const g = mesh.geometry.parameters
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity
  for (let i = 0; i < 4; i++) {
    _v.set((paint[i < 2 ? 0 : 1] - 0.5) * g.width, (paint[i & 1 ? 3 : 2] - 0.5) * g.height, 0)
    mesh.localToWorld(_v).project(camera)
    const sx = ((_v.x + 1) / 2) * innerWidth, sy = ((1 - _v.y) / 2) * innerHeight
    x0 = Math.min(x0, sx); x1 = Math.max(x1, sx)
    y0 = Math.min(y0, sy); y1 = Math.max(y1, sy)
  }
  out[0] = (x0 + x1) / 2; out[1] = (y0 + y1) / 2
  out[2] = (x1 - x0) * 1.26; out[3] = (y1 - y0) * 1.26
}
```

**Why ×1.26 and not √2:** an ellipse inscribed in a w×h box touches only the four edge midpoints, so √2 is
what it takes to circumscribe the whole rectangle — but a subject's bbox corners are empty anyway, so √2
reads as a loose ring floating around the thing. 1.22–1.30 reads as *circling it*.

Recompute every frame while the camera moves. A hardcoded position circles empty ground two seconds later.

---

## §7 Click and drag on the same element: 按下记坑，抬手判定

When one element carries both a click (open / navigate) and a continuous gesture (drag, rub, paint, scrub):

```js
let downOn = -1; const downAt = [0, 0]
onpointerdown = (e) => { downOn = pick(e); downAt[0] = e.clientX; downAt[1] = e.clientY }  // nothing visible
onpointerup   = (e) => {
  const i = downOn; downOn = -1
  if (i < 0) return
  if (Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 6) return  // that was the gesture
  open(i)
}
onpointercancel = () => { downOn = -1 }
```

- **Never open on `pointerdown`** when a gesture shares the element — the user starts to rub and the page
  jumps out from under them.
- **Never make press-and-hold the entry** to anything. Documented user rejection:
  「按住不放 这种交互都是在增加使用成本。不行的」. Hold is a cost the user pays before knowing what they'll get.
- Restoration/undo of the gesture must be **immediate**, not on a timer. Also documented:
  「我划过以后要等好久才还原啊，交互动效需要实时的反馈和手感」.

If a DOM overlay sits on top of the target and calls `stopPropagation()` on `pointerdown`, the window-level
handler above never records the hit — give that overlay its own click path, don't leave it silently dead.

---

## §8 Copy narrates; it never explains the interaction

「点击查看」 / 「拖动试试」 spends the most expensive space on the page explaining what a working affordance
already says. Documented user rule: **「字只做叙事辅助讲解，而不是产品说明」**.

If the copy *has* to explain the interaction, the affordance failed. Fix the affordance and delete the
sentence — never keep both.

One exception: a single short label attached to the mark itself (「近看」) is part of the mark, not copy.
With N marks, label **one** of them — the same sentence three times is noise. Check where that label lands:
a leader line pointing away from mark #1 can drop the label straight inside mark #2's ring.

---

## §9 Numeric oracles — 量出来，不是看出来

Screenshots cost tokens and settle nothing. Every row below is a number you can print in one headless run.

| Worry | Measure | Pass |
|---|---|---|
| "只有一个能点开" | Sweep a grid (12px) over the region, feed each point to the hit test, report **% of cells each target owns** | every target > ~2%, and no target at 0 |
| Invitation is missing / mistimed | Affordance window vs pin/dwell range | window ⊇ dwell |
| Mark is clipped by the frame or safe area | `getBoundingClientRect()` of each mark vs `innerHeight − safeArea` | strictly inside, with margin |
| Shared-element handoff reads as a cut | At the handoff frame, on-screen size of incoming ÷ outgoing (§10) | within 3% |
| "太大 / 太近了" | Don't reach for the scale knob — measure **what is actually clipped**: the subject's foot line / baseline vs the safe area | inside |
| Transition "没生效" | Sample size & position at t = 0.002 / 0.35 / 1, not just t = 1 | monotonic, no jump at t≈0 |

**"太近了" is worth its own note.** The user said 「3 个离屏幕都太近了一点」 and the reflex was to shrink them.
Measuring showed the actual defect: the nearest subject's ground line sat at 0.994 of frame height — its feet
were *out of frame* and its ring was cut by the border. Not "too big", "too close to the edge". Pulling the
group back along their own view rays fixed it and cost only 15% of on-screen size; shrinking would have
thrown away the scale that a previous round had specifically asked for.

Grid sweep, in full:

```js
for (let y = y0; y < y1; y += 12) for (let x = x0; x < x1; x += 12) pts.push([x, y])
const owned = {}
for (const [x, y] of pts) { setPointer(x, y); const i = hitTest(); if (i >= 0) owned[i] = (owned[i] || 0) + 1 }
// print owned[i] / pts.length per target — "全过" from three centre clicks means nothing
```

---

## §10 The invisible handoff — 交接那一帧必须一样大

The whole trick behind *"it flew from there into view"* is that at the handoff frame the incoming element
is **exactly the size and position of the outgoing one**. Miss it and the eye reads a cut — and the user
reports 「动效没生效」, not "the size jumped", which is why this is nearly impossible to diagnose from the
complaint alone.

**Documented case (2026-08-15).** The detail view carried its own `realH = 2.2` while the scene object had
been raised to `4.6` in an earlier round. On-screen size = real size ÷ distance, so at handoff the detail
view was **48%** of the thing it was supposed to be replacing, then grew back to full — a hard cut wearing a
0.6s animation. The comment sitting directly above the constant read *"both planes are the same size (both
2.2m)"*. It had been true once.

> **A comment asserting that two numbers agree is not a mechanism.** Make one side read the other.

Fix and oracle:

1. One source. The detail view now copies its geometry from the scene object it replaces, per item.
   Two places that must agree cannot both hold a literal.
2. Anchor on **the element that was actually picked**, not a hardcoded first one.
3. Expose a dev hook that **pins the transition at an arbitrary t** (`window.__hold(t)`), because a headless
   screenshot takes ~1s and an un-pinned check only ever catches the end state — an end-state-only test gives
   a hard cut full marks. Measure at `t = 0.002`.
4. Assert `|inH − outH| / outH < 3%`. Measured 52% → 0.0% on the case above.

The same rule covers FLIP / shared-element route transitions in the DOM: the entering node's first frame
must match the leaving node's `getBoundingClientRect()`, not "roughly the same place".

---

## §11 When brightness runs out, spend on motion — 「钉一下」

The brief that has no static answer: 「三处都看不太清楚，但也不要太抢眼」. Both halves are real, and they
close the contrast knob.

**First, spend the contrast you legitimately have.** Measured with the on/off oracle (§9,
`verification-harness.md` §8) and raised one notch each in size *and* density:

| mark | before | after |
|---|---|---|
| corner brackets | 1.55vh / 1px / α 0.31–0.45 | 1.9vh / **1.5px** / α 0.44–0.62 |
| dots under the glyphs | 0.05em / α 0.30–0.46 / no halo | 0.08em / α 0.44–0.64 / **paper-coloured halo** |
| curtain bracket | *(no static mark existed)* | box × 1.32 / 2px / α 0.56–0.72 |

**Then it is over.** These are the only saturated red in the whole piece; one more notch and they read as
UI chrome, which is the complaint you were told to avoid. So the second cut is on **movement**:

- Move half the breathing out of alpha and into **position** — brackets open and close 0.24vh, dots swell
  and shrink. Same amplitude budget, different channel.
- Add a **tap**: every **6.2 s**, inside **half a second**, the brackets pull inward 0.62vh and spring
  back / the dot swells and settles. The mark replays its own entrance (the draw-on already grows the
  brackets out of the corners), so nothing new has to be designed.

The arithmetic is the whole point:

```
breathing:  2 px over 4.6 s  ≈ 0.8 px/s   → the eye classifies this as stationary
tap:        5 px over 0.25 s ≈ 20 px/s    → peripheral vision cannot ignore it
```

> **Peripheral vision catches fast-and-small, not slow-and-big.** A tap is quiet while you're looking at it
> and waves while you're not.

Stagger the phases across marks (`i * 0.29` of the period) so they don't pulse as a group — a group pulse
is a UI, an offset one is three separate annotations.

**Keep the whole thing deterministic** — drive breathing and tap from the same pinnable clock the scene
uses, so the oracle can pin a frame at the tap's peak (`t = 0.25 + 6.2k`) *and* at rest, and screenshots
stay reproducible.

Two placement details that cost a round each:

- **The weakest mark decides.** The bracket that measured worst sat on a dark part of the mound
  (background Y=121) while the vermilion itself is Y=89 — **the line is invisible there**, and the mark
  reads only because of a two-layer paper-coloured `drop-shadow` behind it. Every mark needs the halo, not
  just the ones over busy ground.
- **A padding constant carries the shape it was derived for.** `CALLOUT_PAD = 1.26` was the inscribed-
  ellipse allowance; corner brackets touch the corners and owe no such margin — 1.26 → 1.10.
- **Adjacent marks fuse.** Bracketing two vertically adjacent glyphs at line spacing ×1.34 with boxes
  ×1.32 leaves a 1 px gap: the pair reads as one horizontal bar, i.e. a table rule. Bracket the first one
  only.

---

## §12 An auto-demo must not touch the state the user owns

Waiting for the user is legitimate design, but 「等人动手的静止」 and 「没做完的静止」 look identical on
screen. Demonstrating after a dwell (in the case project: 2.6 s of no input → perform the gesture once,
then let it restore; never again once the user has done it themselves) is the cheapest fix — the mechanism
already exists, only the trigger is new.

Three constraints, each learned by breaking it:

**1. The demo writes to its own channel.** The copy says 「散帘后纸上剩的那几个红字，是你亲手翻过的」.
A demo that writes into the same store makes that sentence false the moment it runs. Render
`max(userState, demoState)`; read **only** `userState` for anything that counts. Give the demo's output a
lighter value (0.62 vs full) so it reads as a suggestion rather than a record.

**2. Size the demo by what it removes, not by how far it travels.** A stroke of path length 0.23 cleared
6.5% of the mask and was invisible in before/after frames. Length 0.42 cleared 9.4% and read as whole
sections disappearing. Calibrate against the ceiling first — clearing the *entire* mask changed only 19.1%
of pixels by more than 6 levels, because the artwork is pale thin lines. **A demo on faint artwork must be
much larger than it feels.** And weight by the artwork's own alpha, not by mask area
(`verification-harness.md` §5).

**3. Phase comes from an absolute timestamp.** Accumulating `dt` looks equivalent and isn't: main loops
clamp `dt` (0.05 for backgrounded tabs), so under 20 fps the demo drifts later and later — a demo authored
at 2.6 s first measured at 5.2 s.

Expose a switch that suppresses the **static hint** while leaving the **demo** running, and vice versa.
The on/off oracle needs everything except the thing under test to be identical between the two renders.

---

## §13 「高亮」 is a generic UI word, and a piece has no generic UI

The first version of "light up the post holes as they're revealed" was a warm glow around each hole. One
look settles it: **holes do not glow.** Rows of glowing dots on an earthwork read as Christmas lights.

The replacement is the pen the piece had already established — the same vermilion used to mark brushed
glyphs and to stamp the seal. The viewer has met this red twice already and knows what it means: *somebody
made a note here*. On the holes it reads as an archaeologist circling evidence.

> **Glow, outline, pulse and halo are words borrowed from somewhere else, and a borrowed word has no
> antecedent inside your piece.** Before inventing an indicator, look at what this work already uses to
> point at things.

The placement follows the same judgement: the vermilion is composited **before** the atmospheric pass
(`mix(c, uCinnabar, …)` one line above `mix(c, uPaper, k * 0.68)`), so it is washed out by 160 m of air
along with the thing it marks. Composited after, it stays fully saturated and instantly reads as an
overlay floating outside the picture.

**And put the pen down when you're done pointing.** The marks ramp in as the sentence that mentions them
arrives and clear as it leaves — ending exactly where the next annotation begins, since two annotations in
one window means only the fading one is read (`timeline-orchestration.md` §4).

**A revealed thing rarely needs a second timeline.** The holes are painted into the artwork and the peel
front already uncovers them row by row: alpha eats whatever hasn't been revealed, so "row by row" is free
and — because the peel front carries noise — better staggered than any hand-authored sequence. Two fronts
authored separately will not stay aligned, and the viewer sees marks lighting on ground that is still
covered. Ride the existing front.

*(A mask that annotates artwork must be authored in that artwork's own frame. A mask made for a different
plate puts the marks where there is nothing — worse than no mask. And if the feature is already painted
into the art, the script's job is to **find** it, not to redraw it.)*

---

## §14 Reveal interactions are decided by what is underneath, not by the gesture

A page-curl was built for act ①: corner lifts, crease softens, backside paper is a stop darker, drop
shadow along the fold. Four assertions green — lift reached 0.23, 609 of 1024 sampled points changed,
cursor became `nw-resize`, released flat in 1.6 s with no residue. The screenshots read convincingly as a
lifted corner.

**Then someone looked at what had been uncovered: empty paper.** The composition is a tower in the centre
third; all four corners are pale ground and pale sky, under a stop of difference from the paper itself.
The uncovered triangle spanned uv x 0.869→1, y 0→0.232 — a few footprints.

> **Lift / erase / scrub / spotlight interactions are validated by the content under the hand, not by the
> fidelity of the gesture.** Settle it before the first line of shader code: render the underlying layer
> alone and look at the region the hand is going to.

The fix is never "make the gesture more convincing" — it is to move the interaction to where the content
is. Here: the content only exists in the centre, so the reveal had to follow the finger instead of living
in a corner (colour bleeding up under the fingertip, reusing the field and bleed function the full-frame
dissolve already used — one mechanism, two scales).

Related, and worth its own line: **a premise that saves you work deserves re-checking against the frame.**
A stroke was drawn only across the top third of a tower, with a comment explaining that the rest was
occluded by the mound. It wasn't: the annotation layer had `depthWrite: false` and `renderOrder 70`, so it
never participated in occlusion at all, and the tower is wider than the mound anyway — none of the nine
eaves was actually hidden, and the ones crossing the mound were the most legible part of the stroke.
「挡住了所以不用画」「看不见所以不用做」 save effort, and are therefore exactly the claims nobody goes back
to verify.
