# Case · char-curtain

576 characters hung as **24 independent vertical strings**. There are no horizontal links anywhere,
which is the entire reason a pointer can push through and part it instead of denting it. Each glyph's
colour and alpha are functions of its own speed, so a still frame shows you where the ripple is.

`index.html` — single file, Canvas 2D, rAF, no dependencies, no images. Ladder **rung 2**.

Origin: ported from demo 01 of `motion-test/01-react-motion-gallery`, a React gallery built with this
skill. The demo was a bare `<canvas>` component with no page around it; the title layer, the footer
readout and the wheel gust were added here so it is a page rather than a fragment — see §5 #3 for why
that was not optional.

This is the worked example for **a cloth that is a set of strings, not a mesh**, and for what happens
to an oracle when its baseline is measured against a page that has not stopped moving.

---

## 1 · 设计系统

### Tokens

| Role | Value | Where |
|---|---|---|
| ground | `#ffffff` | the paper. Cleared every frame — the trail is in the colour, not in a fade |
| ink | `#181b1b` | a glyph at rest |
| ink-fast | `#71717a` | what a glyph fades toward at full speed, and the second line of the title |

Three values, no accent. The page has exactly one colour event and it is not a colour: it is the
grey a character turns while it is moving.

### Type

| | Size | Face |
|---|---|---|
| title | `clamp(44px, 7vw, 86px)` | system monospace, 500, `-0.04em` |
| cloth | 14px | system monospace |
| footer | 11–12px | system monospace |

Measured ratio **6.6×**. Everything on the page is monospace, including the display type, because the
cloth is made of code and a proportional heading would be a different object sitting on top of it.

### The title layer

`position: fixed` over the canvas at `pointer-events: none`. The cloth stays reachable underneath the
type, which matters: the headline occupies the top-left quarter, and if it swallowed pointer events
a quarter of the cloth would be dead.

### Section shapes

**One.** Verified with `--min-shapes 1`. Single-screen piece, not a page.

---

## 2 · 动效系统

### The structure is the mechanism

```
24 columns × 24 rows = 576 nodes
links: vertical only, 23 per column, 552 total
links between columns: ZERO
```

That last line is the case. A cloth with horizontal links is a **sheet**: push it and the whole thing
dents, because the force reaches the far edge through the mesh. With vertical links only, each column
is an independent hanging string and neighbours are free to separate — which is what "parting a
curtain" physically is. `--curtain` asserts it directly: poking column 2 displaces it **49.5px** while
the far side of the cloth moves **2.3px**, a 5% bleed. Add the horizontal links and that goes to 35%.

### Constants

| | Value | Why |
|---|---|---|
| gravity | 0.28 | light. A realistic value makes it fall rather than hang |
| drag | 0.025 | very low, so a ripple survives several seconds and reads as cloth |
| solver passes | 5 | stiffness. One pass is a rubber band; five is fabric |
| home pull | 0.35 | the top row is **sprung** to its peg, not nailed, so a hard shove visibly tugs the whole curtain off its rail and back |
| pointer radius | 75px | |
| pointer force | 4.8 | |
| y bias | 0.35 | intended to stop the rows crushing together — but see §5 #2 |
| bounce | 0.6 | reflecting `oldX` rather than `x` is what turns a clamp into a bounce: it rewrites the implied velocity |

### Verlet, and why it suits this

Position **is** the state; velocity is implied by the previous position. Nothing integrates a
velocity, so a constraint solver can move a node directly and the motion stays consistent on the next
frame for free. That is what makes 552 links at 5 passes cheap enough to run at 60fps on the main
thread with 576 glyphs being drawn on top.

### Speed as colour

```
ratio = min(speed / 8, 1)
rgb   = lerp(#181b1b -> #71717a, ratio)
alpha = 1 - ratio * 0.35
```

Both channels move together, so the fast part of a ripple greys **and** thins while the settled part
stays black. This is the only motion cue that survives into a still frame, which matters for a page
whose whole behaviour is invisible until someone moves a pointer.

### The gust

The wheel adds a sideways impulse to every node, decaying at 0.94 per frame. Anchors take a quarter
of it so the curtain leans from its rail before the body catches up. It exists for two reasons: the
wheel is the first input most visitors try, and a gust arrives at all 24 strings at once and then
falls apart at 24 different rates — the cheapest possible demonstration that they are not one sheet.

### Reduced motion

Nothing is on a clock. The cloth moves only because the pointer or the wheel moved it, so the page is
already still when untouched and there is nothing to switch off.

---

## 3 · 判据

```bash
python3 scripts/verify_case.py cases/char-curtain/index.html --min-shapes 1 --curtain
```

| Leg | Asserts | Measured here |
|---|---|---|
| 1 · reacts | a real pointer sweep moves the median column ≥ 6px sideways | **22.3px** |
| 2 · **independent** | poking one column moves it ≥ 4px while the far side of the cloth moves < 20% as much | near **49.5px**, far **2.3px**, bleed **5%** |
| 3 · does not tear | no link deviates > 35% from its 18px rest length | worst **5.4%** |
| 4 · returns home | after release, every anchor settles within 2px of its peg | worst **0.80px** |

Legs 1 and 2 are the pair. A dead cloth fails 1. A sheet passes 1 and fails 2. Only a set of
independent strings passes both.

**Proved by breaking it:**

| Broken copy | Result |
|---|---|
| `MOUSE_FORCE = 0` | FAIL — "moved the median column 0.00px" |
| horizontal links added (a sheet) | FAIL — "the far side moved 35% as much" |

---

## 4 · 可以照搬 / 不许照搬

### 可以照搬（机制层）

- **The whole Verlet + link solver.** 40 lines, no dependencies, and it is the same code as a rope, a
  flag, a chain or a hanging menu.
- **Vertical links only, for anything that should part rather than dent.** This is a structural
  decision made once at build time and it determines the entire feel.
- **Sprung anchors instead of pinned ones.** `n.x += (initX - n.x) * 0.35` on the top row. A nailed
  anchor cannot show that the curtain was shoved.
- **Bouncing by reflecting `oldX`.** In Verlet you change velocity by rewriting history.
- **Speed → colour and alpha together.** The cheapest way to make motion legible in a still frame.
- **A read-only probe plus a `colOffsets()` aggregate.** Give the oracle the summary it needs to make
  a structural claim, not just raw node positions it has to interpret.

### 不许照搬（皮层）— the reasoning transfers, the values do not

- **White ground, charcoal ink, monospace everywhere.** What transfers: matching the display face to
  the material of the artwork, so the heading belongs to the same object. That the material here is
  source code is this piece's own conceit.
- **The source text hung on the strings.** Any text works. This one is a self-portrait.
- **`24 × 24` at 18px row spacing.** Tuned so the cloth is roughly square at 420px wide. Yours will
  differ with your glyph size.
- **"Hang it, then part it."** Copy.

---

## 5 · 踩过的坑

1. **An oracle's baseline has to be measured, never assumed — a fixed settle time let a copy with
   the pointer force set to ZERO pass.** `verify_case.py` sends one real wheel event in its
   smoke test before any flag runs. This page turns a wheel into a gust that decays at 0.94 per
   frame, i.e. about **2.7 seconds**. The first version of `--curtain` waited a hard-coded 2.6s,
   which put the baseline reading *inside* that decay: the cloth was still drifting on its own, and
   every displacement measured afterwards was credited to the pointer. The fix is to poll the probe
   until maximum node speed and gust are both under threshold, and to fail if it never settles.
   **A settle time that is "long enough" today stops being long enough the moment someone adds an
   entrance.**

2. **The x/y displacement ratio cannot test an anisotropic force, and asserting it was worse than
   useless.** The pointer applies its y component at 0.35 to stop rows crushing into blobs. The
   obvious check — is horizontal displacement much larger than vertical — passes at 7.9× on the real
   case, so it looked like a working assertion. A copy with the bias set to **1.0** measured
   **8.8×**: *higher*. The vertical links absorb y motion by sliding nodes along the string, so the
   ratio is dominated by the structure and is nearly independent of the force that produced it. The
   assertion was replaced by the column-independence leg, which tests a structural claim the code
   actually makes. The y bias is still in the source and still does something visible by eye; this
   README does not claim a number for it, because none was measured.

3. **A pure-canvas page is invisible to the acceptance floor's input check.** The floor requires a
   real wheel to change something, and its change signature is scrollY plus computed styles plus
   `innerText` across the DOM — **canvas pixels are not in it**. A demo that is one `<canvas>` and
   nothing else can be alive with motion and still fail with "a real wheel event changed nothing".
   That is not a bug in the floor: a page whose only feedback is inside a canvas gives a screen
   reader, and a visitor who has not moved yet, exactly nothing. The fix is the same in both
   directions: a small live readout in the DOM. It satisfies the check *and* it is the only thing on
   the page that says it is listening before you touch it.
