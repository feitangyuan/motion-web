# Case · wheel-rail

**Declared render layer: `dom`.** Verified by
`python3 scripts/verify_case.py cases/wheel-rail/index.html --rail`.

A landing page whose entire choreography is driven by two inputs: the wheel
and the pointer. Nothing plays on a timer. Nothing animates on load. Put the
mouse down and the page is still; move it and every plane moves by a different
amount; turn the wheel and a rail translates while the document itself never
scrolls.

Reference: `https://blink.trade/` — measured live on 2026-09-03, headless
Chromium at 1440×900 — **and the clip `refs/2-blink.mp4`**, 9.55 s at 60 fps,
3424×2160. The live site gives the palette and the scroll device; only the clip
shows the signature shape, because it is the one thing on the page a still
frame cannot represent.

---

## 0 · Why this case exists

The first attempt at this reference took its palette and its grain and shipped
a page that did neither of the two things the reference actually does. The
correction was blunt and correct: *interaction motion is motion produced by
mouse scroll or mouse movement.* A page that drifts on its own is a screensaver.

So this case is scoped to exactly that claim, and the oracle is written to
fail three specific ways of faking it — see §3.

---

## 1 · Where the numbers came from

Every value below was read off the live reference, not guessed.

| Value | Measured |
|---|---|
| ground | `rgb(237, 236, 235)` |
| ink | `rgb(39, 36, 36)`, 463 elements |
| accent warm | `rgb(221, 110, 54)`, **12 elements** |
| accent olive | `rgb(154, 169, 102)`, **7 elements** |
| raised surface | `rgb(251, 252, 253)` — lighter than the ground, no border |
| hairline | `rgb(220, 217, 213)` |
| display size | 117.03 px against 14 px body |
| `document.scrollingElement.scrollHeight - innerHeight` | **0** |
| `window.scrollY` after a 900 px wheel | **0** |
| `@font-face` | 4 (Neue Haas Grotesk, Aeonik Mono Pro) |
| `<canvas>` | 0 |

The two accent rows are the whole colour brief. Twelve elements out of several
hundred carry the warm tone. The first attempt spread it over 28 % of the
frame and read as a wash; the reference spends it once, hot, in one place.

The `scrollHeight - innerHeight == 0` row is the reference's central device and
the reason this case exists.

---

## 2 · The three devices

**The wheel is hijacked.** `wheel` is bound `{passive:false}`, calls
`preventDefault()`, and accumulates into a target. A rail element is
translated; `window.scrollY` never leaves 0. `overflow:hidden` alone would
also pin `scrollY` — it would not stop a trackpad overscrolling and
rubber-banding, which is why the oracle checks `defaultPrevented` and not just
the scroll position.

**The rail eases, frame-rate independently.**

```js
cur += (target - cur) * (1 - Math.exp(-6.2 * dt));
```

Measured: 660 px behind target 40 ms after a tick, 2 px behind after 900 ms.
The `1 - exp(-k·dt)` form is what makes that identical at 60 and 120 Hz; a bare
`cur += (target-cur) * 0.1` is twice as fast on a 120 Hz display.

**The pointer drives depth, not a slide.** Three planes with different
deflections and one shared lag constant. Measured across a corner-to-corner
sweep: far wash 69.5 px, near card 9.9 px — a 7× ratio. Equal numbers would be
one flat plane sliding, which is the failure the oracle's third assertion
exists to catch.

**Every element is written every frame.** Words, raised surfaces and curves all
read their own progress out of the rail position and set opacity, transform or
`stroke-dashoffset` directly — no CSS transition, matching the reference, whose
`.word` spans measure `transition-duration: 0s` while sitting at
`translateY(8px)` / `opacity 0`. That is what makes the reveal *scrub*: turn the
wheel back and the words go back down. Five devices ride on it:

| Device | Driven by |
|---|---|
| per-word rise, 8 px, staggered `0.55/n` | rail position |
| raised surfaces rise 18 px and fade | rail position |
| curves draw via `stroke-dashoffset` | load for the hero, rail for act 4 |
| marquee band | rail position only — no idle drift |
| radar sweep: soft conic wedge over a dotted guide ring, dot at the hand tip | **its own clock**, 3.95 s per turn |
| labelled dot scales ×2, label goes to ink | pointer proximity, 150 px |

Two supporting details, both from the reference: labelled nodes are pinned to
their curves with `getPointAtLength` rather than hand-typed percentages, so
they cannot drift off the line at any viewport; and act 4's curve field is
parked by hand against the rail, because `position:sticky` cannot fire inside
a transformed ancestor.

---

## 2b · The one thing that is *not* input-driven

Built first from static frames of the live site, this case shipped with a soft
orange radial gradient sitting perfectly still, and was rejected on sight. The
clip shows what it should have been: a **radar sweep** — a dotted guide ring, a
hand turning, and a soft-edged wedge trailing behind it that closes and clears.

Measured from `refs/2-blink.mp4`, over a window where the page is provably
still (the ink baseline moves 145 → 149 px):

| Value | Measured |
|---|---|
| wedge angular span | 191° → 18°, then clears |
| that collapse takes | 55 frames at 60 fps (0.92 s) |
| full turn | ≈ 3.95 s |
| fill, peak pixel | `rgb(151, 171, 116)` |
| fill, mean | `rgb(172, 183, 146)` |

So the reference runs **both** kinds of motion at once: the wheel and the
pointer drive the layout and every reveal, and the sweep turns whether or not
anybody touches the page. Those are not alternatives. A build with only the
first is a still image until you interact with it, which is exactly how this
one read.

`--rail` was tested against three deliberately broken copies. All three fail:

| Break | Caught by |
|---|---|
| `preventDefault()` removed | wheel event not cancelled |
| all three parallax depths set equal | far 10.6 px vs near 9.9 px — planes move together |
| follow constant raised to 999 | rail within 0 px of target 40 ms after the tick |
| every reveal neutralised, rail intact | element churn 10 % |
| every reveal made a hard 0/1 step | churn still 48 %, peak mid-flight 2 |
| sweep hand pinned, breathe removed | 1 element moving after 1.5 s untouched |

The last two are the pair that matters. The first four assertions all passed a
build in which the rail translated and **not one child element ever changed** —
which is precisely the version that got rejected on sight. Churn alone is not
enough either: the snap build satisfies it and still reads as a slideshow. The
two have to pull against each other.

Measured on the finished case against the reference, both under real
`mouse.wheel` input, eight bursts of five ticks:

| | blink.trade | this case |
|---|---|---|
| elements whose visuals changed | 64 % | 48 % |
| peak caught mid-transition | — | 33 |
| still moving after 1.5 s untouched | — | 9 |
| total elements | 584 | 199 |
| word spans | 296 | 87 |

Density is itself a device, not a by-product. The first dense-enough build came
from adding what the clip shows under everything: a **hairline grid** of eleven
vertical rules that draw down on the opening clock and then track the pointer
(rules within 26 % of the cursor come up, the rest stay back), **horizontal
rules** that draw across as each act arrives, and **range markers** — a hairline
capped with two 6 px warm dots over a downward gradient. Twenty-odd elements,
all of them animating, none of them decoration invented for the case.

An oracle that passes its own broken variants is decoration. These were run
before the case was filed, not after.

---

## 4 · Known gap

Ships 0 `@font-face` and substitutes IBM Plex Mono and an Inter-class variable
face for the reference's Aeonik Mono Pro and Neue Haas Grotesk. Same debt the
other DOM cases carry; stated here rather than hidden.
