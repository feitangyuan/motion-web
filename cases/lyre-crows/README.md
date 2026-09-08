# Case · lyre-crows

Nine strings you can strum. Strumming shakes a word loose. Three crows are hunting words, and
whichever one reaches it first **rewrites its own tail with what it caught**. Nothing on the page is
choreographed: every visible event is a consequence of the previous one, and the only input is a
pointer.

`index.html` — single file, Canvas 2D, rAF, no dependencies, no images. Ladder **rung 2**.

Origin: ported from demo 02 of `motion-test/01-react-motion-gallery`. As with `char-curtain`, the
demo was a bare canvas; the title layer, the readout and the wheel strum were added so it is a page.
The port found and fixed one real bug, in §5 #1.

This is the worked example for **a causal ecology instead of a timeline** — and for the two things
that keep one from turning into noise.

---

## 1 · 设计系统

### Tokens

| Role | Value | Where |
|---|---|---|
| ground | `#d6c8b3` | tea-stained paper, redrawn every frame |
| wash | `rgba(184,115,81,.16)` / `rgba(156,179,168,.15)` | two overlapping watercolour discs, warm and sage |
| ink | `#1e293b` | the crows, the fibre specks, the display type |
| vermillion | `#b91c1c` | strings, words, tails, and the one word of the headline that matters |

One accent, used for everything the visitor can cause. Every red thing on the page is either a thing
you can strum or a thing your strum produced. That is not decoration, it is a legend.

### Type

| | Size | Face |
|---|---|---|
| headline | `clamp(40px, 6.4vw, 78px)` italic | Georgia |
| tail glyphs | 11px italic bold | Georgia |
| word bubbles | 11px italic bold | Georgia |
| readout | 10px, `.12em` tracking | monospace |

Measured ratio **6.0×**. The tail glyphs and the headline are the same face at two extremes of size,
so the sentences the crows carry read as fragments of the same voice as the title.

### The paper

Two watercolour discs plus 35 fibre specks with a hairline each. The specks are seeded from their own
index (`sin(i * 713.82)`), not `Math.random()`, so the grain is identical every frame and every
reload. Random specks would boil at 60fps and turn a still background into television static.

### Section shapes

**One.** Verified with `--min-shapes 1`.

---

## 2 · 动效系统

### The loop

```
strum a string  →  a word is released  →  a crow steers to it
                →  it is eaten  →  that crow's tail becomes the word
```

There is no timeline, no sequence and no scheduler. Two things keep this from becoming soup, and both
are load-bearing:

1. **Rate limiting at the source.** At most one word per strum, at most **4 aloft**, and never within
   **800ms** of the last. Without this a fast drag across nine strings emits hundreds.
2. **Unconditional decay on the product.** A word loses `1/240` of its life per frame — about 4
   seconds — whether or not anything eats it. A loop that only removes things on success accumulates
   forever, and the failure is silent until the frame rate dies.

### The strings

Both ends are re-pinned to the frame every frame; a string is *defined* by its endpoints not moving.
No gravity (they are under tension), drag 0.035 so a pluck settles instead of ringing forever, five
solver passes.

The pluck takes the pointer's **velocity**, not its position:

```js
n.y += mvy * pct * 0.85;
```

Resting the cursor on a string does nothing at all. Dragging through it plucks it. That distinction
is the whole difference between an instrument and a hover target.

### The crows

Classic steering, and one detail carries it:

| | Value |
|---|---|
| max speed | 2.0, ×1.55 while diving |
| **max steering force** | **0.055** |
| catch distance | 18px |

**Clamping the steering force rather than the velocity is what gives a turn a radius.** Clamp only
the speed and the bird pivots on the spot like a cursor. The dive gain is visible intent: a hunting
crow is measurably faster than a gliding one, so you can see it commit.

Idle motion is a lissajous phase-offset by crow index, so three of them never line up into a
formation.

### The tails

A Verlet chain of 18–20 nodes at 18px spacing, each holding **one** character. Two details:

- The head node is pinned to the bird **and given the bird's previous position as its `old`**, so the
  tail inherits the bird's velocity instead of being dragged from a standstill every frame.
- Each glyph is rotated to the heading of its own segment, so the sentence reads *along* the curve
  rather than lying flat across it.

A capture does not spawn anything. It rewrites the characters already on the chain and kicks each
node — the consequence is carried by the object that was already there.

### Reduced motion

This is the one case in the skill with something genuinely on a clock: the crows glide whether or not
you touch anything. Under `prefers-reduced-motion` the steering integrator is skipped and the scene
holds its settled frame, rather than being hidden.

---

## 3 · 判据

```bash
python3 scripts/verify_case.py cases/lyre-crows/index.html --min-shapes 1 --lyre
```

| Leg | Asserts | Measured here |
|---|---|---|
| 1 · **releases** | fourteen real strum sweeps release at least one word | yes |
| 2 · **rate limited** | and never exceed the stated cap of 4 aloft while being abused | peak **4** |
| 3 · hunters converge | with prey aloft, some crow enters a hunting state and the nearest gap closes ≥ 30% | **84%** closed, 18 hunting flags |
| 4 · the loop closes | a counted capture must change that crow's tail **and** leave the caught word in it | **3/3** tails changed, 3 carry the marker |

Legs 1 and 2 are the pair. A decorative set of strings passes the cap and fails release. An
unlimited emitter passes release and floods — the broken copy hit **440** aloft.

**Proved by breaking it:**

| Broken copy | Result |
|---|---|
| `canSpawn = true` (limiter removed) | FAIL — "440 words aloft against a stated cap of 4" |
| `eat()` increments the counter only | FAIL — "no crow's tail changed at all — the counter is the only consequence" |

---

## 4 · 可以照搬 / 不许照搬

### 可以照搬（机制层）

- **The causal loop shape itself.** Input → gated emission → autonomous agents → a consequence
  written back onto an existing object. This is the transferable idea and it has nothing to do with
  birds.
- **Rate limiting at the source, decay on the product.** Both, always. Either one alone eventually
  fails: a limiter without decay still accumulates, a decay without a limiter still spikes.
- **Steering with the FORCE clamped, not the velocity.** The single line that separates a bird from
  a cursor.
- **Velocity-driven pluck.** Take the pointer's delta, not its position, when the gesture is
  "through" rather than "on".
- **A tail whose head inherits the carrier's previous position.** Free correct motion, no special
  case.
- **Per-glyph rotation to segment heading.** Text along a physical curve, six lines.
- **Deterministic seeded specks** for any texture that redraws every frame.
- **A read-only probe that reports the ecology** (words aloft, hunting flags, tail contents) rather
  than exposing setters. The oracle strums with a real pointer and waits.

### 不许照搬（皮层）— the reasoning transfers, the values do not

- **The tea-stained ground and the single vermillion.** What transfers: **one accent, assigned to
  everything the visitor can cause or has caused**, so the colour is a legend rather than a taste.
  These hues are this piece's.
- **Georgia italic at two sizes.** What transfers: carrying one face across the display type and the
  smallest object in the scene, so the fragments belong to the title.
- **The sonnet vocabulary and `X LINES TO TIME`.** Content.
- **The origami crow outline.** Nine `lineTo` calls of someone's drawing.
- **9 strings / 3 crows / 4 aloft / 800ms.** Tuned for this canvas at this size.

---

## 5 · 踩过的坑

1. **A rate limit computed once per frame is not a rate limit.** The budget was read before the loop
   over nine strings and passed in as a flag: `canSpawn = words.length < 4 && ...`. Nine strings can
   all be inside the pointer radius on the same frame, and each one that fires pushes a word —
   so a cap of 4 measured **6**, and would allow 9 in the worst case. The flag has to be re-read
   inside the loop, and the push has to be guarded again at the moment it happens. The original React
   code has the same shape, and the overshoot is invisible by eye because a few extra words look like
   a good strum. `--lyre` leg 2 is what found it.

2. **The oracle matched a string the page can never produce.** Leg 4 checked the tails for the full
   replacement sentence, `"LINES TO TIME"`. A tail holds a fixed number of nodes — 18 to 20 — and the
   rewrite writes `chars[i] || ' '` into each, so anything longer is simply **truncated**:
   `SHAKESPEARE LINES TO TIME` becomes `SHAKESPEARE LINES `. The assertion failed against a perfectly
   working page, which is the mirror image of the usual problem and just as expensive. It now
   compares each tail against a snapshot taken **before** any strumming, and separately looks for a
   short marker that fits inside the shortest tail. **Assert that state changed, not that it changed
   into one exact string.**

3. **An absolute threshold is wrong whenever sampling starts mid-event.** Leg 3 originally required
   the crow to close ≥ 20px on its prey. But sampling begins after fourteen strum sweeps, by which
   time a chase is often already in its last 30px, so a perfectly good hunt closed 13px and failed.
   The fix is scale-free: require the gap to fall to ≤ 70% of wherever the measurement started. This
   is the same class of mistake as #2 — an assertion written against one imagined run rather than
   against the property being claimed.
