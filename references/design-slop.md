# Design Slop — 动效页专属的 AI 味闸门

Generic anti-slop advice ("use a real type scale", "don't invent metrics") applies here too, but it is
not what makes a *motion* page look generated. This file is the failure list specific to pages where
something moves — the tells that survive a good palette and a good font.

**How to run it.** Screenshot the page with **all motion disabled** — set `prefers-reduced-motion`,
or comment the mechanic out — and judge that still frame first. Then re-enable and run the motion
gates. A gate hit is a revision, not a note-to-self.

> The single question that catches most of it: **would this still frame place on Awwwards with zero
> animation?** If the honest answer is "no, it's a centred headline and three cards", the motion is
> carrying a page that was never designed. That is the documented failure of this skill.

---

## A. Still-frame gates (motion off)

**A1 · The default hero.** Full-bleed section, centred H1, centred one-line subhead, two buttons
(one filled, one outline), maybe a badge pill above. This is the single most generated layout on the
web. → Break at least one of: centring, the two-button pair, the badge, or the assumption that the
hero is a *section* at all. On a motion-first page the hero is often the mechanic itself with the type
set into it, not a text block above it.

**A2 · Centred three-column feature cards.** Three equal cards, icon on top, bold noun, two lines of
grey body. If the content is genuinely three peers, that is a *content* fact — the slop is rendering
it as three equal boxes in a row. → Asymmetric weights, a stacked editorial list, a diagonal, an
indexed table, or one card promoted and two demoted.

**A3 · Every section is `headline + paragraph, centred`.** A page where every band has the same
internal structure reads as a template even with perfect typography. → At least three *different*
section shapes per page. Structural variety is what separates two designs; palette variety is not.

**A4 · The violet/indigo gradient.** `#6366f1 → #a855f7`, purple-to-blue mesh backgrounds, glowing
violet orbs. This is the most reliable AI tell that exists — it is the default every image and code
model reaches for. → Pick an anchor from `data/visual-bank.json` and commit. Two hues plus a neutral
is a palette; **a spectrum is not a palette** — rainbow accents and multi-hue cycling read as a
demo, not a brand. If a scene needs warmth against cool, one warm accent against a cool ground does
more than five hues.

**A5 · Decoration standing in for design.** Noise overlay, floating blobs, a grid pattern, a glow
behind everything — added because the page felt empty. They do not fix emptiness; they make it
textured emptiness. → Emptiness is a *structure* problem: the type scale is too small, the sections
are too similar, or there is no scale contrast anywhere.

**A6 · No scale contrast.** Everything between 16px and 48px. Real creative-web pages run enormous
display type against small body — the jump *is* the design. → See `page-design.md` §2 for measured
ratios from current award winners.

**A7 · Fake chrome.** Hand-drawn browser bars with traffic-light dots, fake phone frames, mock IDE
windows around a `<pre>`. → Real screenshot in a `<figure>`, or no frame.

**A8 · Invented proof.** "+47% conversion", "trusted by 50,000+ teams", five logo placeholders,
invented testimonials. If the user did not supply the number, it does not go on the page. → A
labelled placeholder block, or a macrostructure that doesn't need proof.

---

## B. Motion gates (motion on)

**B1 · Uniform hover lift.** Every card does `translateY(-4px)` + shadow on hover. It is the motion
equivalent of the three-column feature row: applied to everything, meaning nothing. → Hover should
say something specific about *that* element. If you can't name what it communicates, cut it and let
the cursor/state carry it.

**B2 · Universal scroll fade-up.** Every block enters with `opacity 0→1, translateY 20px`. The page
becomes a slideshow of identical arrivals, and the reader learns to ignore entrances by section three.
→ Reveal is an editing decision: most content should already be *there*. Reserve entrance for the
two or three things that genuinely benefit, and give them different arrivals.

**B3 · One easing, one duration, everywhere.** A single `0.3s ease` on the whole page reads as a
CSS default because it is one. → Motion tokens with at least three tiers (`motion-tokens.md`), and a
spring where the thing should feel physical.

**B4 · The whole budget in the hero.** Everything moves in the first screen, then eight screens of
static text. → Spend across the page; a scroll timeline is a schedule, not a firework
(`timeline-orchestration.md` §1).

**B5 · Motion unrelated to content.** Particles behind a B2B pitch, orbiting spheres behind a book
club, a fluid sim because it looked cool. The mechanic must come from the topic's own physics
(`composition-guide.md` §5). → If the mechanic would work equally well on any other brief, it is
decoration.

**B6 · Parallax as the only depth idea.** Every layer at a different scroll rate and nothing else.
→ Depth reads from occlusion and silhouette overlap far more than from rate differences
(`image-plane-3d.md` §4).

**B7 · The trailing dot cursor.** A small circle lerping behind the pointer, unattached to anything.
It was a signature in 2019; it is now a default. → Either make the cursor *do* something (reveal,
magnify, carry state) or leave the system cursor alone.

**B8 · Nothing survives reduced-motion.** The `prefers-reduced-motion` branch is a blank page or a
broken one. → The still frame is the page; motion is the enhancement. If the reduced-motion version
is unusable, gate A was never really passed.

---

## C. What to do with a hit

Do not "note it for later". Each hit maps to a structural fix, and structural fixes are cheap while
the page is young and expensive after the mechanic is wired in — which is exactly why the design act
comes *before* the mechanic goes in (`SKILL.md` freeform step 5).

| Gate | The fix is almost always |
|---|---|
| A1–A3 | A different macrostructure — `page-design.md` §1 |
| A4 | Commit to one palette archetype — `data/visual-bank.json` |
| A5–A6 | Raise the type scale and vary section shapes; delete the decoration |
| B1–B3 | Delete most of the motion, then spend it on fewer things |
| B4 | Re-read the schedule horizontally — `timeline-orchestration.md` §1 |
| B5 | Go back to the operators — `composition-guide.md` §5 |
