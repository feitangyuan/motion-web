# Page Design — 动效页的设计，不是通用 UI 设计

The still frame is half the deliverable. This file is how the page looks and reads **before anything
moves**; `design-slop.md` is the gate that checks you actually did it.

Generic design advice ("use a type scale", "respect spacing rhythm") is true and not the problem. The
problem is that a motion-first page has structural demands a normal landing page doesn't: something on
it is going to move, and the layout has to have been designed *for* that, not decorated afterwards.

---

## §1 Macrostructure comes from the mechanic's demand, not from a template

The default web page shape — hero, three features, testimonial, CTA, footer — exists to move a reader
down a funnel. A motion-first page usually is not doing that, and inheriting the shape anyway is why
so many of them read as "a normal landing page with an animation stuck on top".

Pick the shape from what the mechanic needs:

| Shape | The page is | Mechanic sits | Tell-tale measurement |
|---|---|---|---|
| **Single scene** | one place you move through; no sections at all | *is* the page — camera or world moves on the scroll rail | very long scroll, no internal `max-width`, few DOM sections |
| **Acts** | 3–5 pinned beats, each with one idea and one money frame | one per act, sharing a vocabulary | long scroll, pinned ranges, `timeline-orchestration.md` schedule |
| **Editorial + set-pieces** | mostly readable text; motion arrives 2–4 times and means something | punctuation between passages | medium scroll, constrained measure inside a full-bleed page |
| **Index / archive** | a list you browse; the motion lives in transitions and hover | between states, not inside a section | short scroll per view, many routes |
| **Single screen instrument** | one screen you play with; scrolling is not the verb | the entire page | scroll ratio ≈ 1, all interaction, no fold |

Two rules that decide most cases:

- **Is the content linear?** If yes, acts or editorial. If no — if the visitor is browsing or playing
  — index or instrument. Forcing non-linear content onto a scroll rail is the most common structural
  mistake, and it shows up later as "这一段什么都没发生" (`timeline-orchestration.md` §1).
- **Does the camera move, or does the world?** Decided here, not in the renderer
  (`image-plane-3d.md` §12). It changes the lens, the asset budget, and whether "sections" exist at all.

**Structural variety inside the page.** At least **three different section shapes** per page. A page
where every band is `centred headline + paragraph` reads as a template no matter how good the type is
— and unlike palette, this is the variable people actually perceive as "designed". Vary: alignment,
column count, whether the band is full-bleed or inset, whether type sits over the artwork or beside it.

---

## §2 Measured — what current award winners actually do

These are **measured**, not remembered: a headless run against 15 sites captured from Awwwards
SOTD and Godly in 2026-08. Read them as the shape of current practice, not as targets to hit.

**Read the caveat first.** 3 of the 15 returned a largest-rendered-text of 12–18px — impossible for
pages that obviously have display type. Their headline type is **not in the DOM**: it is drawn into a
canvas, or the root is transform-scaled. That is itself a finding — a meaningful share of this tier
puts its typography inside the artwork — and it means the numbers below describe the 12 sites whose
type a DOM ruler can see. Quoting a median across all 15 would have been quoting the ruler's failure
(`verification-harness.md` §9).

### Type scale — the jump is enormous

| | Median | Range (n=12) |
|---|---|---|
| Largest rendered text | **108 px** | 52 – 218 px |
| Body text | **16 px** | 10 – 16 px |
| **Ratio (display ÷ body)** | **≈ 8×** | 3.3× – 14× |

The top of the distribution runs 170–218px of display type against 12–16px body. **Nothing in this
sample lives in the "everything between 16 and 48px" band** that a default build lands in. If a page
feels flat and you can't say why, measure this ratio first — under about 4× the page has no scale
contrast, and no amount of spacing fixes that. Note also that several run body at **12px**, not 16:
small body is what makes the display size read as huge.

### Palette — small, and overwhelmingly neutral

- Distinct dominant colours: **median 4**, range 1–6.
- `#ffffff` appears in **15/15**, `#000000` in **14/15**. The ground is black or white, nearly always.
- Saturated colour, when present, is **one** hue used sparingly — a green, an orange, a pale yellow.
- **Gradients as a background treatment appear in none of them**, and violet/indigo shows up once in
  the whole sample. The default AI palette is not what this tier looks like (`design-slop.md` A4).

### Typefaces

- Font families per page: **median 2**, range 1–4. One family is a normal choice, not a compromise.
- Common shape: one grotesk for everything plus a serif (often plain `Times`) used for contrast.

### Page shape — bimodal, and never a centred column

- `body { max-width }`: **none on 15/15.** Not one constrains the page globally; measure is set per
  element. A globally centred column reads as a document, not a designed page (§6).
- Page height ÷ viewport is **bimodal**: 5 of 15 sit at ≈1 screen (single-screen instruments, all
  interaction, no scroll verb); the other 10 run **7–57 viewports, median ≈ 16**. There is very little
  in between — these pages are either one screen or a long journey, and the middle ground (the
  3–5 screen marketing page) is not what this tier is doing.

### Stack — most of them are not using a motion library

| Detected | Count |
|---|---|
| No library detected (hand-written or a bundled custom engine) | 9 / 15 |
| GSAP | 4 / 15 |
| Lenis | 3 / 15 |
| Native CSS scroll timelines (`animation-timeline` in the page's own CSS) | 2 / 15 |
| Framer Motion | 1 / 15 |

Two things follow. First, **award-tier motion is mostly not a library choice** — reaching for GSAP is
not what separates these pages from a default build; the structure and the type scale are. Second,
native scroll timelines are **shipping but still rare** at 2/15, so rung 1.5 is a real option rather
than the current norm — pick it because it fits, not because "everyone is doing it".

> This block was wrong once. An earlier run reported `CSS Scroll-Driven` for **15/15**, because the
> detector called `CSS.supports('animation-timeline','scroll()')` — a probe of the *browser*, which is
> true for every page in a modern headless run. Same class of mistake the Replicate Mode warns about
> for WebGL. If a stack readout agrees across every site in a sample, suspect the ruler before
> believing the finding (`SKILL.md` self-check).

---

## §3 Design the space the motion needs

Motion needs room, but **room is not whitespace** — it is the absence of things competing for the
same attention at the same moment.

- **The hero is often not a section.** On a motion-first page the opening is frequently the mechanic
  itself with type set into it. A full-bleed band containing a centred H1, a subhead and two buttons,
  with the canvas pushed below, is the layout that guarantees the motion reads as decoration.
- **One window, one event.** If the mechanic is doing something, nothing else should be arriving at
  that scroll position. This is a *layout* decision (what is on screen together) as much as a timing
  one — see `timeline-orchestration.md` §4.
- **Type over moving artwork has a floor.** Contrast is not measurable against a surface that changes,
  so measure the worst frame, not the average one. Give the text its own ground: a scrim, a solid
  panel, or a region of the artwork that is designed to stay quiet. "It's readable in the screenshot
  I took" is not the test — seek to the busiest frame and check there (`verification-harness.md` §2).
- **Leave a quiet band.** A page where every region is active has no hierarchy of motion, which reads
  the same way as no hierarchy of type. Something should be still so the moving thing means something.

---

## §4 Typography — scale contrast *is* the design

- **The jump is the point.** Display type on these pages runs an order of magnitude above body. A page
  where everything lives between 16 and 48px looks unfinished no matter how good the font is; that is
  usually what "没设计感" means when nothing else is obviously wrong.
- **Two families is plenty; one is a legitimate choice.** Distinction comes from size, case, weight and
  measure — not from adding a third face. `data/visual-bank.json` carries five worked pairings with
  concrete `clamp()` values and letter-spacing.
- **Tighten as it grows.** Display sizes want negative tracking (≈ −0.03em to −0.04em) and line-height
  near 1.0–1.05; body wants 1.5–1.65 and no tracking. Applying one line-height across the scale is a
  reliable amateur tell.
- **Chinese display type behaves differently.** Latin display faces lean on tight tracking and tall
  ascenders; a Chinese face at the same optical size reads heavier and needs *more* line-height, not
  less (≈1.4–1.6 even in display), and negative tracking closes counters fast. Mixed CJK/Latin lines
  need the Latin face specified separately or the fallback picks something that doesn't match. Weight
  contrast carries hierarchy better than size contrast alone, because a huge 黑体 becomes a solid block.

---

## §5 Colour — commit, then let the artwork bring the rest

- **Small palettes.** Two hues plus neutrals is a palette; a spectrum is a demo. Rainbow accents and
  multi-hue cycling are among the most reliable "generated" tells.
- **The violet/indigo gradient is out.** It is the default every model reaches for
  (`design-slop.md` A4). Committing to one anchor archetype from `data/visual-bank.json` beats
  inventing a gradient every time.
- **Motion pages have a second palette you didn't choose** — whatever is inside the shader, the video,
  or the photographic assets. Design the UI palette *against* it: usually near-neutral chrome so the
  artwork carries the colour, with a single accent reserved for interactive affordances.
- **One warm accent against a cool ground** (or the reverse) does more work than five hues, and stays
  legible when it lands on top of moving artwork.
- **Replicate a reference palette's *structure*, never its values.** One light ground, one near-black,
  one high-saturation block, one grey mid-tone, one accent that appears in exactly one place — that
  is the transferable part, and it survives being re-hued. The specific hues are that studio's brand;
  lifting them ships someone else's identity under your name.

---

## §6 Spacing rhythm and section pacing

- **Section spacing is not a constant.** Even spacing produces a page that reads like a list. Vary it
  with intent: tight where two bands belong together, very generous before a beat you want landed.
- **Full-bleed page, constrained measure.** Current practice is a page with no global `max-width`,
  where *individual* elements set their own measure — running text at 60–75 characters, media
  full-bleed. A global centred column is a document, not a designed page.
- **Long scroll needs a map.** Past roughly ten viewports a visitor needs to know where they are:
  a progress indicator, section labels that change, or a persistent element that transforms. Native
  `scroll-target-group` scroll-spy is now one line of CSS (`pattern-recipes.md` #16).

---

## §7 Mobile is a different design, not a smaller one

- **Hover does not exist.** Anything the desktop design puts behind hover needs a second home
  (`affordance.md`). This is a layout decision, not a media query.
- **The scroll gets longer.** The same content at one column typically doubles page height, which
  changes the pacing you carefully set — re-read the schedule at mobile width, don't assume it scales.
- **Decide the degradation explicitly.** Fewer particles, a shorter camera path, a still frame instead
  of the canvas, or the mechanic replaced by a simpler gesture. Writing "it works on mobile" without
  naming what was dropped means it was never designed; a heavy scene that stutters on a mid-range
  Android fails for most of the audience.
- **Verify at 320 / 375 / 414 / 768.** No horizontal scroll, no two-line buttons, touch targets ≥ 44px.

---

## §8 Checklist

- [ ] Macrostructure chosen from the mechanic's demand, and nameable (§1)
- [ ] At least three different section shapes; no page where every band is centred headline + paragraph
- [ ] Type scale has a real jump — display against body, not a smooth ramp (§4)
- [ ] Two font families or fewer; display tracking tightened, body untouched
- [ ] Palette committed and small; no violet/indigo gradient; UI palette designed against the artwork's own colours (§5)
- [ ] Section spacing varies with intent; measure constrained per element rather than one global column (§6)
- [ ] Text over moving artwork checked at the **busiest** frame, not a lucky screenshot (§3)
- [ ] Something on the page is deliberately still (§3)
- [ ] Mobile degradation named explicitly, not assumed (§7)
- [ ] Still frame screenshotted with motion off and run through `design-slop.md` before showing anyone
