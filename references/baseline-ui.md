# Baseline UI — the floor, not the design

**This file is not where the page gets designed.** That is `page-design.md`, and the quality gate is
`design-slop.md`. What follows is the usability and accessibility floor a motion-first page still owes
even when the motion is the point — the things that make it a *usable page* rather than a demo.

Everything here is checkable. If an item can only be argued about, it belongs in `page-design.md`.

---

## §1 The page works with motion switched off

The single most load-bearing item. Set `prefers-reduced-motion: reduce` and confirm:

- [ ] Every piece of content is present and readable — nothing is stuck at its `from` keyframe
- [ ] No element sits at `opacity: 0` waiting for a trigger that no longer fires
- [ ] Scroll-linked content is at its resolved state, not its 0% state
- [ ] The page is still navigable — a pinned section that never unpins traps the reader
- [ ] Reduced-motion is a *designed* version, not a broken one

The common bug: an entrance authored with `both` fill and a scroll trigger that the reduced-motion
branch disables, leaving the fill holding the invisible start state. Author the finished state as the
default and add motion on top (`pattern-recipes.md` #16).

---

## §2 Nothing essential lives behind hover

- [ ] Every hover-revealed control has a touch/click path to the same thing
- [ ] Content (not just affordance) never depends on hover — captions, prices, descriptions
- [ ] Hover-only reveals are not the only way to discover an interaction (`affordance.md` §1)

Touch devices have no hover, and a large share of desktop visitors never sweep the region you assumed.

---

## §3 Keyboard and focus survive the choreography

- [ ] Visible focus ring on every interactive element — including custom cursors and canvas overlays
- [ ] Focus order follows reading order after any reordering/pinning
- [ ] A scroll-jacked or pinned page can still be traversed with Tab, and focusing an element inside a
      pinned section scrolls the timeline to it rather than tearing the layout
- [ ] Nothing traps focus — modals, full-screen scenes, and canvas overlays all release it
- [ ] Motion-triggered state changes that matter are announced (`aria-live`) or reachable without motion

Canvas-driven pages fail this quietly: the DOM behind a `pointer-events: none` canvas is often still
in the tab order with no visible ring.

---

## §4 Hit targets and input hygiene

- [ ] Interactive targets ≥ 44 × 44 px on touch, including anything inside a canvas
- [ ] A control that also drags decides on pointer-*up*, with a movement threshold (`affordance.md` §7)
- [ ] Faded-out or inactive overlays set `pointer-events: none` so they stop eating clicks
- [ ] No interaction depends on a gesture the platform already owns (edge swipes, two-finger scroll)

---

## §5 Layout stability

- [ ] Layout is stable before animation starts — no reflow from fonts, images, or a late-loading canvas
- [ ] Media and canvases have reserved dimensions; nothing jumps when they arrive
- [ ] The first screen does not shift after hydration

Animation is a leading cause of layout shift, and shift is the one motion failure that is also a
ranking and usability problem. Animate `transform` and `opacity`; never animate a property that
triggers layout.

---

## §6 Responsive floor

Verify at **320 / 375 / 414 / 768** px:

- [ ] No horizontal scroll anywhere (`overflow-x: clip` on `html` and `body`, not `hidden`)
- [ ] No two-line buttons or nav links
- [ ] Image-bearing grid tracks use `minmax(0, 1fr)`, never bare `1fr`
- [ ] Long display headings wrap inside words (`overflow-wrap: anywhere; min-width: 0`)
- [ ] The mobile experience is a named degradation, not an accident (`page-design.md` §7)

---

## §7 Performance floor

- [ ] Cap DPR at `Math.min(devicePixelRatio, 2)` for any canvas
- [ ] Heavy scenes gate on viewport visibility and pause when hidden
- [ ] No per-frame DOM reads inside the animation loop
- [ ] Nothing animated except `transform` / `opacity` in the DOM layer
- [ ] A mid-range Android holds up, or the page ships a lighter scene to it

---

## §8 Failure patterns

- Motion used to compensate for weak hierarchy — the fix is in `page-design.md`, not in the easing
- Effects unrelated across sections, so the page reads as a collection of demos
- Canvas or video stealing attention from the primary content or action
- Reduced-motion mode shipped as a broken page rather than a designed one
- Mobile collapsing into a screenshot gallery of the desktop design
