# Case · press-stack

**Declared render layer: `dom` + `canvas2d` for every piece of artwork.**
Verified by `python3 scripts/verify_case.py cases/press-stack/index.html --stack`.

A record press's landing page: nine screens, four grounds, one type wipe. It is
the **opposite answer to `cases/wheel-rail`**. There the wheel is hijacked and a
rail is translated; here native scroll is left alone and each screen pins itself
with `position: sticky` while the next one rides up over it.

Reference: `refs/4-side-b.mp4` — 24.5 s at 30 fps, 1920×1080, by @LexnLin.
**There is no live site.** The page was generated in one pass by a model and the
author published the prompt, not a URL. Two rounds of search turned up no link,
so every number below was read out of the clip.

---

## 0 · Why this case exists

Two reasons, one technical and one about how the skill was failing.

**Technical.** `position: sticky` cannot fire inside a transformed ancestor —
`wheel-rail` had to park its pinned elements by hand. This case is the same
brief solved the other way round, so the pair documents both halves: a hijacked
rail can compute any progress it likes but gets no pinning; a sticky stack gets
pinning for free and has to read progress back out of the document.

**Process.** Four of this skill's first five cases used grey CSS gradient
rectangles where the reference had photographs. This one has no photographs at
all: every sleeve and every record is drawn on a canvas at load, and `--stack`
fails the case if a single element pulls a bitmap.

---

## 1 · Where the numbers came from

Measured off the clip, not off a description of it.

| Value | Measured |
|---|---|
| paper | `rgb(238, 233, 224)` |
| olive | `rgb(23, 24, 12)` |
| vermilion | `rgb(215, 69, 37)` |
| sage | `rgb(200, 205, 185)` |

Those four are the reference's own brand, so the case keeps the **shape** of the
system — one bright ground, one near-black, one saturated block, one muted tint,
one accent used nowhere else — and swaps the hues for a cool set: `#e9ebee`,
`#11151c`, `#2f5570`, `#c3ccd3`, with `#e08a3c` as the only warm thing on the
page. Replicating a colour *system* is the transferable part; replicating its
hues is just taking someone's brand.
| unlit type / lit type | **51 / 230 → 0.22** |
| the wipe crosses the block in | ~1.6 s of scroll |
| one line's own ramp | 0.3–0.5 s |
| preloader, counter to reveal | ~2.4 s |
| grounds in the run | 4, across 8 screens |

The `0.22` row is the whole point of the manifesto screen. Unlit words are
**dimmed, not hidden**: the block is readable before the wipe reaches it and the
sweep raises it to full. That is a different device from the `opacity: 0 → 1`
word reveal in `wheel-rail`, and it is the one a still frame cannot tell you
apart from a fade-in — you need the clip.

---

## 2 · The devices

| Device | Driven by |
|---|---|
| nine screens pinned with `position: sticky` | native scroll |
| type wipe, `0.22 → 1`, left-leaning per line | the manifesto screen's own progress |
| pressings rail walking sideways | that screen's progress |
| the record turning | that screen's progress |
| notes settling, each on its own delay | that screen's progress |
| sleeves lifting, near ones further than far | pointer |
| club card on a third axis | pointer |
| counter `00 → 100`, then the panel leaves upward | its own clock, once |

**Reading progress back out of the document.** With every screen `sticky; top: 0;
height: 100vh`, screen *i* pins for exactly one viewport, so its progress is
`clamp((scrollY - section.offsetTop) / innerHeight)`. No observers, no scroll
listeners, one read per frame.

**The dwell, and why the first build had none.** Sticky siblings that are each
exactly one viewport tall are fully visible at a *single* scroll position and
nowhere else: the moment a screen finishes arriving, the next one starts eating
it. Every content animation therefore played inside the half that was being
covered, and scrolling the page looked like nothing happening. The fix is one
line — `margin-bottom: 100vh` on each screen adds document space *after* it
without adding to its box, which buys one viewport of dwell before the hand-off
begins. Measured: at `scrollY` 0 through 900 the first screen holds the viewport
alone; at 1800 the second has covered it.

That splits progress in two, and content must use the first:

```js
dwell[i] = clamp((scrollY - top) / vh);        // the screen is whole
cover[i] = clamp((scrollY - top - vh) / vh);   // the next one is eating it
```

**The trap this layout sets.** In a sticky stack the next screen eats the bottom
of the current one first. Anything anchored with `margin-top: auto` is therefore
the first thing to disappear — the headline, the giant numeral and the section
rule all vanished on the first build for exactly this reason. Content lives in
the upper two thirds; only hairline strips go low.

**Drawn artwork.** Sleeves are five archetypes chosen by seed, not by the random
draw — leaving the pick to the RNG produced four halftones out of seven. The
record is 190 concentric grooves plus **two narrow specular arcs**; a wide
gradient wash across the whole disc reads as a gold plate rather than vinyl.

---

## 3 · What the oracle refuses

`--stack` was run against four deliberately broken copies before the case was
filed. All four fail, each on a different assertion:

| Break | Caught by |
|---|---|
| no dwell (screens exactly one viewport apart) | real-wheel churn 20 % |
| `sticky` → `relative` | 1 of 8 screens pinned |
| every word given the same wipe key | widest spread 0.00 — a switch, not a wipe |
| unlit type set to `opacity: 0` | dimmest word 0.00, not 0.22 |
| every screen given the same ground | 1 distinct ground |

The wipe assertions are a pair that pull against each other: a page that lights
everything at once satisfies the "unlit stays readable" floor, and a page that
fades from zero satisfies the "there is a gradient" test. Only doing both the
way the reference does passes.

---

## 4 · What was cut, and why

The reference's hero has photographed sleeves, a portrait, and a hand holding a
record. Sleeves and records are graphic design and geometry, so they are drawn.
**The portrait and the hand are not** — code primitives do not make convincing
people, and stacking spheres into a figure is worse than leaving it out. Those
two slots were removed and the screens redesigned around type and a drawn
record instead of being filled with a placeholder.
