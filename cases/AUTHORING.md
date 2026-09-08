# Authoring a case — 参考 → 复刻 → 收录

How a design reference becomes a `cases/<name>/` entry that is a **complete case**: a design system, a
motion system, working code, and a re-runnable oracle. Read this before starting one.

`SKILL.md` § Cases says what a case *is* and the 机制层/皮层 rule. This file is the procedure.

---

## Phase 0 · Intake — is this reference a candidate?

**The gate: strip every photograph, illustration and video out of the reference in your head. Is there
still a design?**

- Yes → the design lives in type, grid, colour, geometry and motion. **Replicable.**
- No → most of what you liked was the artwork. Replicating it produces grey rectangles where the
  reference had pictures, which is the documented failure of this skill's first five cases.

If the reference fails the gate and the user still wants it, the asset step is a **precondition, not a
detail**: agree where the images come from before writing any code (per the user's global rules, images
are generated with Nano Banana Pro only, or supplied by the user). Do not start and hope.

**A video reference is not a reference yet.** If it is a clip you cannot open, run the Video Reference
Protocol in `SKILL.md` first — pull the real media, extract frames, state the trajectory as geometry.
Titles tell you the topic, not the motion.

---

## Phase 1 · Deconstruct with numbers, not impressions

Both scripts, both readouts quoted in the report:

```bash
python3 scripts/measure_churn.py     <url>        # motion: share of elements that change under a
                                                  # REAL wheel, and how many are caught mid-transition
python3 scripts/measure_structure.py <url>        # page: sections, nav, buttons, token scales,
                                                  # forms, media, meta, mobile overflow
# Then open the page and read the bundle: library, easing, keyframes, scroll choreography,
# WebGL programs and uniforms — the numbers you quote come from there (SKILL.md, Replicate Mode).
```

What you must be able to state before designing anything:

| Axis | The number to have |
|---|---|
| Type | largest rendered px, body px, **the ratio** |
| Palette | count of dominant colours, the ground, where saturation appears |
| Radius / shadow | how many distinct radii, how many shadowed elements → **which dialect** (`components.md` §1) |
| Structure | section count, distinct section shapes, full-bleed %, ground changes |
| Page shape | height in viewports; one screen, or 7–50? |
| Motion | library or none, trigger, duration, easing, what is pinned, what is scrubbed, over which band |
| Stack rung | which rung of `build-mode.md` the reference is actually on (usually lower than it looks) |

**Before you decide a reference has no live URL, read the thread.** This is a hard step, not a
courtesy. Measured 2026-09-02 on the seven references this skill was handed: a previous session
declared all of them URL-less and spent its whole Phase 1 on frame measurement — **every single one
had a live site, and in every case the author had posted it in their own replies**:

| reference | where the URL was | what it turned out to be |
|---|---|---|
| `overheard` | author reply: "it's <url> (for that screen click on partnership)" | `overheardhq.com` — Next.js + Tailwind |
| `CO'WATCH` | author reply: "Try it <url>" | `focus.itshassco.com` |
| `INTO THE VOID` | author reply: "Play it here: <url>" | `ink-crowd.vercel.app` |
| `ibuongiorno` | in the post text itself | `ibuongiorno.com` |

The replies also settle a question frames never can: **whether the thing is a web page at all.** In
that same post the author answered "AE or Jitter?" with *"1st jitter + figma, 2nd figma motion, 3rd
rive + gsap, 4th idk (dev did it haha)"* — three of the four "designs" were motion-design renders
with no web implementation to replicate, and one was a real site. Replicating a Jitter render as a
web page is work that cannot succeed, and one reply would have said so.

```bash
safe-x tweet <url> --json | grep -i 'http\|figma\|jitter\|rive\|gsap\|built\|dev'
curl -sSL -o /dev/null -w '%{url_effective}\n' <the t.co link>    # resolve it
```

Only once the thread is exhausted is a clip URL-less. **Then** neither capture script can run — a
video has no DOM — so say so and measure the frames instead:

```bash
safe-x tweet <url> --json                    # or the platform's own CLI — routing doc first
curl -sL -o ref.mp4 "<the media url in that json>"

python3 scripts/measure_frames.py sheet   ref.mp4          # ALWAYS first — then look at it
python3 scripts/measure_frames.py palette ref.mp4 -t 8      # ground %, accents, mid greys
python3 scripts/measure_frames.py bands   ref.mp4 -t 8      # control heights + widths
python3 scripts/measure_frames.py trace   ref.mp4 --color red   # arc / chord, per frame
```

`sheet` is not optional and not a formality: every other subcommand answers a question you can only
ask after you have seen the thing. A screen capture of a retina window is **2× CSS px** — the script
prints both, halve before writing anything into a README.

What each one settles:

| Axis | Subcommand | What the number means |
|---|---|---|
| palette | `palette` | the ground is the ≥80 % entry; accents are the mean of the top-N most-saturated pixels, **not** the mean of all coloured pixels; the mid-grey list is the tick / rule / muted-text scale |
| control geometry | `bands` | distinct band heights **are** the control scale. Two is a hierarchy; three on one panel is usually a mistake |
| motion | `trace` | a near-constant arc across frames = inextensible; arc that grows 2–3× under a drag = **elastic**, and that changes the solver (`pattern-recipes.md` #19) |
| circular furniture | (by hand) | least-squares circle fit to the tick pixels; if the fit is contaminated by other UI, ray-scan from the centre and read the runs |

State in the report **which instrument produced each number**, and never present a frame measurement
as a headless readout of the live page. The tracer's own caveat applies: a column/row scan averages a stroke that
doubles back, so it under-reports arc on a looping curve — cross-check a surprising row against the frame.

**Suspect the ruler before believing a finding.** If a readout agrees across every site in a sample, or
returns something impossible (12px display type on a page with huge headlines), the instrument is
wrong — `page-design.md` §2 has two worked cases of exactly this.

---

## Phase 2 · Classify before building

Four decisions, all named, all written into the README later:

1. **Dialect** — creative or product (`components.md` §1). This settles radius, shadow, nav CTA,
   footer scale, button case. Getting it wrong is the "像 AI 做的" complaint.
2. **Blueprint** — which spine from `page-blueprints.md` §2, and which sections it actually needs.
3. **Macrostructure + arc** — `page-design.md` §1 and `choreography-arc.md`, chosen together.
4. **Ladder rung** — `project-setup.md` §1 for the page stack, `build-mode.md` for the motion stack.
   Start at rung 0 / rung 1.5. A case that needs a bundler to demonstrate a technique has buried it.

**Replicate ≠ copy** (`SKILL.md` § Replicate Mode). Recreate the interaction pattern, the motion
character, the structural idea and the *reasoning* behind the type and colour decisions. Do not carry
over brand colours, copy, or identifiable product UI. Say in the report what was faithful and what was
adapted.

---

## Phase 3 · Build

- **One file, no build**, unless the technique genuinely needs more. `cases/*/index.html` are all
  single files and that is the convention — it makes the case openable and editable in one step.
- **The mechanism/skin banner is mandatory.** A comment banner in the `<script>` (and a note in the
  CSS if a block is mechanism) marking what may be lifted verbatim and what may not.
- **Build the probe surface as you go** (`verification-harness.md` §1). Retrofitting `__probe` costs
  more than writing it. And it must expose **the real commit path**, not a shortcut into internal state
  — see the hard lesson below.
- **Author the finished state first**, then add motion on top. Reduced-motion and unsupported engines
  get a whole page, never a blank one.
- **Content is not a placeholder problem to solve later.** If the case will hold pictures, decide now
  whether they exist. Grey gradient rectangles standing in for photographs is how a page passes every
  check and still looks like a diagram.

---

## Phase 4 · Verify

```bash
python3 scripts/verify_case.py cases/<name>/index.html [--beats|--detent|--strings|--stack|--rail|--layer|--follow|--no-js-expected]
```

The floor, applied to every case: no console errors · zero horizontal overflow at 320/375/414/768/1440 ·
one `<h1>` · `lang` · display ÷ body ≥ 4× · ≥ 3 distinct section shapes · **every referenced custom
property actually defined** · **a body that paints its own ground** · nothing stuck hidden under
reduced-motion · **a real wheel and a real hover change something**.

If the case has a mechanic, it owes a **domain oracle** — one that encodes what would actually be
wrong. Existing ones, reusable as patterns:

| Flag | Encodes |
|---|---|
| `--beats` | pacing — the longest scroll run where **no** track moved |
| `--detent` | a control lands exactly, settles, reaches every slot, clamps at both ends |
| `--strings` | **two assertions in tension** — the data-driven endpoint stays exact *and* the body still sags; either one alone passes a broken build |

Adding another is normal. **The best oracles are pairs that pull against each other**: `--strings` is
the clearest example — over-damp the physics and the sag assertion fails, loosen the endpoint and the
accuracy assertion fails, and no single "quality score" can express that. The rule from `verification-harness.md` §0 still holds: **each oracle encodes
one stated complaint**; a general "quality score" is worse than no test.

---

## Phase 5 · File it — what "complete case" means

A case is not the HTML file. It is three systems plus the code, and the README is where the first two
are actually written down.

### `cases/<name>/README.md` must contain

**1 · 设计系统 (design system)** — extracted as values, not adjectives:

- the token block: ground, surface, border, text, accent(s) — and how many there are
- type scale: display px, body px, the ratio, line-height and tracking per tier
- space and radius scales; shadow levels, or the explicit decision to have none
- the **dialect** and the four or five choices that follow from it
- the section shapes used, and why they differ from each other
- which components from `components.md` appear, and what states each owes

**2 · 动效系统 (motion system)** — as a schedule, not a list of effects:

- the ladder rung, and what would force a climb
- every mechanic named, with its trigger, driver, and the band it occupies
- for a scroll page: the tracks laid out horizontally with their ranges, and *why* they overlap
- motion tokens: durations, easings, spring constants — the actual numbers
- the reduced-motion design (a designed version, not a disabled one)

**3 · 判据 (the oracle)** — the table of checks with this case's measured values, and the command.

**4 · 可以照搬 / 不许照搬** — two explicit lists. The skin list must give the **reasoning** behind each
decision, not the values; the reasoning is what transfers.

**5 · 踩过的坑** — every silent failure hit while building, with the number that exposed it. This is
the highest-value section in every existing case README and the one most likely to be skipped.

**6 · 改造方向** — the same mechanism pointed at different pages.

### Then wire it in

- `SKILL.md` § Cases — a row in the case table (name, what it teaches, stack)
- `SKILL.md` § Scripts — its `verify_case.py` line with the right flag
- `SKILL.md` § Cases — a row in the oracle table if the case added a flag
- **If the case produced a general technique** → a numbered recipe in `references/pattern-recipes.md`,
  with the failure modes and the numbers
- **If it produced a general rule** → a bullet in `SKILL.md` § Core Rules
- **If it produced a measurable finding about current practice** → a record in
  a `measure_structure.py` run over the site, and a line in whichever reference file owns
  that axis
- **If the mechanic is new** → one line in the Used-Mechanics Graveyard in
  `references/composition-guide.md`, so it can never be reused

---

## 两条硬教训（2026-08-31，五个 case 建完后）

**1 · 只用探针验过的东西不算验过。** Every check on one early case went through
`__probe.set()`, which writes the angle directly. It passed all of them — landing error 0.0000°, all
slots reachable, both ends clamped — while being **completely dead to a real scroll wheel**: the sign
was inverted so the impulse drove the angle into its own clamp, and `preventDefault()` swallowed the
page scroll at the same time. A probe that bypasses the event handlers tests a path nobody takes.

> `verify_case.py` now sends one real wheel and one real hover on **every** case and requires the page
> to react. When you add a probe method, ask which real gesture it stands in for, and make the oracle
> drive that gesture at least once.

**2 · 占位几何能通过所有判据，然后依然什么都不像。** The first five cases passed every oracle —
type ratios, dead beats, detent landing, state matrices — and the honest verdict on looking at them was
that they were technique diagrams: grey CSS-gradient rectangles where the reference had photographs,
literal grey bars where it had content, solid colour squares where it had cut-out artwork. **No oracle
in this skill measures whether a page has any visual content at all**, and none should be invented to —
that verdict stays with a person looking at the thing (`verification-harness.md` §0).

> So it is a Phase 0 decision, not a Phase 3 one: either the reference survives the strip-the-images
> gate, or the assets are agreed before the build starts. "I will put real pictures in later" is how
> five cases ended up looking like diagrams.

---

## Checklist

- [ ] Reference passes the strip-the-images gate, or its assets are agreed up front (Phase 0)
- [ ] Both capture scripts run — or, for a clip with no live URL, frame measurements with the
      instrument named; type ratio, palette count, dialect, structure and motion params quoted (Phase 1)
- [ ] Dialect / blueprint / macrostructure+arc / ladder rung all named (Phase 2)
- [ ] Single file; mechanism-skin banner present; probe exposes the real commit path (Phase 3)
- [ ] `verify_case.py` passes, including the real-input smoke test; a domain oracle added if there is a mechanic (Phase 4)
- [ ] README carries 设计系统 + 动效系统 + 判据 + 可照搬/不许照搬 + 踩过的坑 + 改造方向 (Phase 5)
- [ ] SKILL.md case table, script line, and oracle table updated
- [ ] General technique → recipe; general rule → core rule; new mechanic → graveyard
