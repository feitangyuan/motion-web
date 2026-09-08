# Components — 组件级的craft，页面真正由什么构成

`page-design.md` decides the page's shape. This file is the vocabulary that fills it: nav, hero, button,
card, field, accordion, dialog, table, footer — the things you have to actually build, with the states
they owe and the numbers current practice uses.

**The failure this file prevents:** a page with a beautiful macrostructure and a beautiful mechanic,
whose buttons are a default blue rounded rectangle, whose form has no error state, whose footer is one
line of copyright, and whose accordion is a `div` with a click handler. That page reads as unfinished
even when the layout is right, and no motion tuning touches it.

---

## §1 There are two component dialects, and they are measurably different

Measured 2026-08 with `scripts/measure_structure.py` at 1440×900 and 390×844 — **32 sites, two samples**:
18 Awwwards-SOTD / Godly creative sites and 14 best-in-class product
marketing sites (Linear, Vercel, Stripe, Framer, Raycast, Resend, Clerk, Cursor, Anthropic, Railway,
PostHog, Supabase, Attio, Notion). The summary below is what this skill ships; re-run the script on your own set for a fresh baseline.

| | **Creative** (n=18) | **Product** (n=14) |
|---|---|---|
| Distinct `border-radius` values on the page | **median 1** | **median 8** |
| Most common button radius | **`0px`** (20 of 35 styles) | `8px` / `4px` / `6px` |
| Elements with a `box-shadow` | **median 0** | **median 17.5** |
| Distinct button styles | median 3 | median 6 |
| Uppercase button labels | **37 %** (13/35) | **1 %** (1/82) |
| Nav CTA buttons | **median 0** | **median 2** |
| Nav links | median 5 | median 8 |
| Nav positioning | `fixed` 11/15 | `sticky` 4 / `static` 4 / `relative` 3 |
| Footer columns / links | **2 cols, 4 links** | **5 cols, 35 links** |
| Full-bleed sections | **83 %** | 32 % |
| Sections that switch background | 32 % | 14 % |
| Distinct section shapes per page | median 2.5 | median 5 |
| DOM nodes | median 1 127 | median 2 995 |
| Images with a reserved box | 37 % | 76 % |
| Images with `srcset` | 15 % | 48 % |
| Container queries in CSS | **0/18** | 6/14 |
| Native scroll timelines in CSS | 2/18 | **6/14** |
| Preloaded font files | median 0 | median 4 |

**What both agree on** (so these are not style choices, they are the floor): nav height ≈ **64 px**;
button label ≈ **14 px**; the section heading is left-aligned ~3× more often than centred (start 76 %
vs center 21 %); exactly **one `<h1>`**; gaps land on a **base-4 grid** (4/6/8/12/16/24 dominate both).

**How to use this table.** Decide which dialect the page is in *before* writing a component, and then be
consistent. The most common mistake this skill makes is building a creative page out of product-site
components — rounded cards, drop shadows, a filled nav CTA, a five-column footer — which is precisely the
"像 AI 做的" complaint (`design-slop.md` A2, A5). The reverse mistake also exists: a SaaS page with
`0px` radius, no shadows and uppercase buttons reads as a fashion lookbook and undersells the product.

**Copy their design language, not their engineering hygiene.** In the same run, **2 of 18** creative
sites had horizontal overflow at 390 px (40 px and 181 px of it), 0 of 14 product sites did; creative
sites reserved a box for only 37 % of images. Award-winning does not mean well-built —
`baseline-ui.md` is still the floor.

**The dialect is a property of the *surface*, not of the page.** The either/or above is how to start,
not where to stop. `cases/string-clock` measures as a straight contradiction — 2 radii, no nav, no CTA,
uppercase micro-labels, a 2-item footer (all creative) around a segmented control, a slider, a swatch
radiogroup and 11 shadowed pills (all product) — and it does not read as AI slop, because the *canvas*
never defects: one ground, no nav, no marketing headline, one type size that matters.

So the test is per surface, not per page: **a control surface may be product dialect inside a creative
canvas.** What produces the "像 AI 做的" complaint is not product components — it is a product **canvas**
(nav + CTA + hero + three feature cards + five-column footer) on work that wanted to be creative. When
in doubt, ask of the canvas, not the widgets: does this page need nav, a CTA and a marketing headline?
If no, keep the canvas creative and let the controls be as product as the job requires.

> **Ruler caveats, stated so the numbers stay honest.** The button probe reads up to 6 distinct
> computed styles per page, so pages with many small icon buttons pull the median height down; radius
> values like `3.35544e+07px` are a pill written as a huge number and were counted as pills; one nav
> match returned a 17 599 px height (a mis-selected wrapper) and is excluded from the height median.
> Where a reading is impossible, prefer suspecting the ruler (`page-design.md` §2 has the same warning).

---

## §2 Every interactive component owes a state matrix

Before any component is "done", answer all of these. A missing state is the single most common reason a
built page feels like a prototype.

| State | Owed by | Cheapest correct answer |
|---|---|---|
| rest | everything | — |
| `:hover` | pointer devices only | must say something specific about *that* element (`design-slop.md` B1) |
| `:active` | everything clickable | a real press: scale `0.98` or a colour step; ≤ 80 ms |
| `:focus-visible` | everything focusable | a visible ring — **never `outline: none` without a replacement** |
| disabled | buttons, fields, submit | `disabled` attribute + `cursor: not-allowed`, and say *why* nearby |
| loading / pending | anything async | in-place label swap, width locked so the layout doesn't jump |
| error | fields, forms, media | message adjacent to the control, `aria-describedby`, never colour alone |
| empty | lists, indexes, filters | a designed empty state, not a blank region |
| success | forms | persistent confirmation, not a toast that vanishes |

Two rules that are not negotiable:
- **`:focus-visible`, not `:focus`.** `:focus` puts a ring on mouse clicks and gets deleted for looking
  bad; `:focus-visible` only fires for keyboard/AT, so it can be loud.
- **Hover is an enhancement, never the only path.** Wrap hover-only styling in
  `@media (hover: hover) and (pointer: fine)` so touch devices never get a stuck hover state
  (`baseline-ui.md` §2).

```css
:where(a, button, [role="button"], input, textarea, select, summary):focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 3px;
  border-radius: 3px;                     /* so the ring hugs oddly-shaped targets */
}
@media (hover: hover) and (pointer: fine) {          /* touch devices never get a stuck hover */
  .btn:hover  { background: var(--accent-hover); }
  .card:hover .card__title { text-decoration: underline; }
}
```

---

## §3 Header / nav

Measured: height ≈ **64 px** on both dialects (mobile 59–64 px). Creative pages run it `fixed` (11/15)
with **no CTA button** and ~5 links; product pages run it `sticky`/`static` with **2 CTAs** and ~8 links.

Decisions, in order:

1. **Overlay or in-flow?** A `fixed`/`sticky` header over a full-bleed hero must survive both grounds.
   Two working answers: (a) `mix-blend-mode: difference` on the whole bar (3/15 creative sites do this —
   it inverts against whatever passes under it, and costs nothing), or (b) a scroll-driven theme swap
   (`pattern-recipes.md` #13). `backdrop-filter` is a *product-site* answer (2/14, 0/15 creative) and it
   is expensive on a page that also runs a canvas.
2. **What is in it.** Logo + ≤ 6 links + at most one CTA. A nav with 9 links needs an index page, not a
   smaller font.
3. **Mobile is a different component, not a media query.** Decide: full-screen overlay, sheet, or
   nothing-but-a-logo. Whatever it is, it owes an open state, a close affordance, focus trapping while
   open, `Esc` to close, and body-scroll lock that restores the scroll position.
4. **The scroll behaviour is a design decision.** Always visible / hide-on-scroll-down-show-on-up /
   shrink after N px. Pick one on purpose; the default (always visible, never changes) is fine and is
   what most of the sample does.

```html
<header class="site-header">
  <a class="skip" href="#main">Skip to content</a>
  <a class="logo" href="/" aria-label="Home">…</a>
  <nav aria-label="Primary"><ul>…</ul></nav>
  <button class="menu-toggle" aria-expanded="false" aria-controls="menu">Menu</button>
</header>
<main id="main">…</main>
```
The skip link was present on **0 of 18** creative sites and 4 of 14 product sites. It costs three lines
and it is the difference between a keyboard user tabbing through 40 nav links on every page or not.

**Slop tell:** a nav bar with a filled violet "Get started" pill on a page that sells nothing.

---

## §4 Hero

On a motion-first page the hero is frequently **not a section** — it is the mechanic with type set into
it (`page-design.md` §3, `design-slop.md` A1). When it *is* a section, choose a shape other than
centred-H1-subhead-two-buttons:

| Shape | Reads as | Watch |
|---|---|---|
| Type set *into* the artwork | creative, confident | contrast at the busiest frame, not a lucky one |
| Left-aligned display block, media to the right/below | editorial | the measure of the sub-line (≤ 48ch) |
| Full-bleed media, single line of type at the bottom edge | film / fashion | safe-area on mobile, text over video |
| Oversized single word / statement, everything else small | manifesto | it has to actually say something |
| Split screen, two unequal halves | product with one visual | the 50/50 split is the generic version — make it 62/38 |

Non-negotiables regardless of shape: exactly one `<h1>`; the LCP element identified and prioritised
(`project-setup.md` §7); the first screen readable before any JS runs.

---

## §5 Buttons

A page needs **three button roles at most** — primary, secondary, quiet — plus a size or two. The product
sample's median of 6 distinct computed styles is what happens when a design system grows, not a target.

```css
.btn {
  --btn-bg: var(--accent); --btn-fg: var(--accent-on);
  display: inline-flex; align-items: center; justify-content: center; gap: .5em;
  min-height: 44px;                        /* touch floor — baseline-ui.md §4 */
  padding-inline: 1.25em;
  font-size: .875rem; font-weight: 500; line-height: 1;
  border: 1px solid transparent; border-radius: var(--btn-radius);
  background: var(--btn-bg); color: var(--btn-fg);
  cursor: pointer;
  transition: background-color 140ms var(--ease-out), transform 90ms var(--ease-out);
}
.btn--secondary { --btn-bg: transparent; --btn-fg: var(--text); border-color: var(--border); }
.btn--quiet     { --btn-bg: transparent; --btn-fg: var(--text-muted); padding-inline: 0; }
@media (hover: hover) and (pointer: fine) { .btn:hover { --btn-bg: var(--accent-hover); } }
.btn:active { transform: scale(.98); }
.btn[disabled] { opacity: .45; cursor: not-allowed; pointer-events: none; }
.btn[data-loading] { pointer-events: none; }
.btn[data-loading] .btn__label { visibility: hidden; }   /* width stays, no layout jump */
```

- **`min-height: 44px` even when the design wants 32.** Give the visual button a smaller painted box and
  keep the *hit* area at 44 via padding or a pseudo-element. Painted-box ≠ hit-box is the whole point of
  `affordance.md` §4.
- **Label width must not change between states.** "Send" → "Sending…" reflows the row; swap with
  `visibility` or reserve the wider label.
- **Creative-dialect buttons are frequently not boxes at all**: a 14px uppercase label with a rule under
  it, or a word with an arrow. 37 % of creative button styles are uppercase and 20 of 35 have `0px`
  radius. Uppercase needs `+0.08em` tracking or it reads as shouting.
- **`<a>` navigates, `<button>` acts.** An `<a>` with a click handler and `href="#"` breaks
  middle-click, breaks the status bar, and is a bug report waiting to happen.

**Slop tell:** every button a pill; two buttons side by side under every headline; a "ghost" button whose
only difference is a 1px border nobody can see.

---

## §6 Eyebrow, tag, badge

Small text elements carry more hierarchy than their size suggests, and they are where an amateur page
leaks first.

- **Eyebrow / section label**: 12px, uppercase, `letter-spacing: .12em`, `--text-muted`. This is the
  cheapest way to give a section an identity without adding a second heading level.
- **Tag / chip**: must be either a link, a button, or plainly not interactive — a `<span>` styled like a
  button teaches the visitor a lie. If tags overflow, wrap them or provide an operable "+3" disclosure;
  never clip.
- **Badge**: never encode meaning in colour alone — a red dot with no text is invisible to a third of
  readers. Pair colour with a word or a shape.
- **No emoji as icons.** Use an SVG set (Lucide, Heroicons) or draw them; emoji render differently per
  platform and read as a placeholder.

---

## §7 Cards

The three-equal-cards row is the most generated layout on the web (`design-slop.md` A2). Before styling
a card, ask whether the content is genuinely a set of peers. If it is:

- **Break the grid.** Unequal spans, one promoted item, an indexed list, a stagger — anything but three
  identical boxes centred in a row.
- **A card needs one of: a surface, a border, or nothing.** Not all three. Creative pages overwhelmingly
  choose *nothing* — median **0** shadowed elements and **1** distinct radius on the whole page. A
  border-less, shadow-less card separated only by space is a legitimate and current choice.
- **If the whole card is clickable**, use one real `<a>` around the heading and stretch it — do not wrap
  a `<div>` in a click handler:
  ```css
  .card { position: relative; }
  .card a::after { content:""; position:absolute; inset:0; }   /* the whole card is the link */
  ```
  This keeps the accessible name, the middle-click, and the focus ring, and lets text inside stay
  selectable.
- **Reserve the media box** with `aspect-ratio` so the grid does not reflow as images arrive.
- **Uniform `translateY(-4px)` hover on every card is a slop tell** (`design-slop.md` B1). If you cannot
  name what the hover communicates, delete it.

---

## §8 Media and figures

```html
<figure>
  <img src="…" alt="…" width="1600" height="1000" loading="lazy" decoding="async"
       srcset="…" sizes="(max-width: 780px) 100vw, 60vw">
  <figcaption>Caption is content. It sets the tone as much as the image.</figcaption>
</figure>
```
- `aspect-ratio` + `object-fit: cover` for any fixed-shape slot; `object-position` when the subject is
  off-centre.
- **Video used as artwork**: `muted playsinline loop` + a `poster`, and `preload="none"` unless it is the
  LCP. Respect `prefers-reduced-motion` — a background video is motion.
- Only 37 % of creative-sample images reserved a box. That is a measured bad habit, not a style.

---

## §9 Forms and fields

Forms are where "能跑" and "成品" differ most, and where the measured sample is weakest: only **19 of 38**
inputs on creative sites and **19 of 37** on product sites had a label, `aria-label`, or placeholder.

```html
<div class="field">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required autocomplete="email"
         aria-describedby="email-err" inputmode="email">
  <p class="field__err" id="email-err" hidden>Enter an address that includes “@”.</p>
</div>
```

Rules:
- **A real `<label>`, always.** A placeholder is not a label — it disappears the moment typing starts and
  is invisible to autofill.
- **`type` and `autocomplete` and `inputmode` are three different things** and all three matter:
  `type` picks validation, `inputmode` picks the mobile keyboard, `autocomplete` lets the browser fill it.
- **Validate on blur, re-validate on input, never on every keystroke of an empty field.** Error message
  goes *next to* the field, references it with `aria-describedby`, and describes the fix ("include @"),
  not the failure ("invalid").
- **Never colour alone.** Red border + icon + text.
- **The submit button owes a pending state** and the form owes a success state that persists.
- **`field-sizing: content`** (Baseline since 2026-06) makes a textarea grow with its content — deletes
  the classic scrollHeight-measuring JS. Cap it: `field-sizing: content; max-height: 12lh;`
- Honeypot over CAPTCHA for a marketing form; CAPTCHA is a conversion tax.

---

## §10 Accordion / FAQ

Use `<details>`/`<summary>`. It is keyboard-accessible, findable by in-page search, and works with zero
JS. The two things it needs:

```css
summary { cursor: pointer; list-style: none; }
summary::-webkit-details-marker { display: none; }
details::details-content {                       /* animatable open/close, no JS */
  block-size: 0; overflow: clip;
  transition: block-size 260ms var(--ease-out), content-visibility 260ms allow-discrete;
}
details[open]::details-content { block-size: auto; }
:root { interpolate-size: allow-keywords; }      /* makes `auto` animatable */
```
`interpolate-size` and `::details-content` are Chromium-first — the fallback is an instant open, which is
correct, not broken. Use `name="faq"` on the `<details>` elements for exclusive-accordion behaviour
without a line of JS.

**Do not** build this from a `div` + click handler. That is the version that loses `Ctrl+F`.

---

## §11 Dialog, drawer, popover

- **`<dialog>` + `showModal()`** gives focus trapping, `Esc`, inert background, and the top layer for
  free. `::backdrop` is stylable. This replaces every hand-rolled modal.
- **Entry animation without JS timing hacks** — `@starting-style` is Baseline:
  ```css
  dialog { opacity: 0; translate: 0 8px; transition: opacity .2s, translate .2s, overlay .2s allow-discrete, display .2s allow-discrete; }
  dialog[open] { opacity: 1; translate: 0 0; }
  @starting-style { dialog[open] { opacity: 0; translate: 0 8px; } }
  ```
- **Popover / tooltip / dropdown**: the `popover` attribute + **CSS anchor positioning**
  (`anchor-name` / `position-anchor` / `position-area` / `position-try-fallbacks`) removes the
  floating-ui dependency for most menus. Firefox is behind on anchor positioning — the fallback is a
  normally-positioned element, so author it that way and enhance inside `@supports (anchor-name: --a)`.
- Whatever the mechanism: restore focus to the trigger on close, and lock body scroll *without* losing
  the scroll position.

---

## §12 Index / filter / tabs

The `index / archive` macrostructure (`page-design.md` §1) needs real component behaviour:

- **Filters must be reflected in the URL** (`?tag=motion`). A filtered view that cannot be linked or
  back-buttoned is broken.
- **Empty state is a designed state.** "No results for *X*" plus the way out (clear filters), not a blank
  column.
- **Tabs**: `role="tablist"` + arrow-key navigation, or just use links to real routes. Half-built tabs
  (divs with click handlers and no keyboard support) are worse than links.
- **View transitions** make route changes in an index feel like one surface:
  `@view-transition { navigation: auto; }` — same-document is Baseline; cross-document is landing.
  Always test with reduced-motion on.

---

## §13 Pricing, stats, testimonial, logo strip

These four exist to carry proof, and proof is the section most likely to be **invented**
(`design-slop.md` A8). If the user did not supply the number, the logo, or the quote, it does not go on
the page — build a labelled placeholder or choose a macrostructure that does not need proof.

- **Pricing**: a real `<table>` when there are ≥ 3 tiers × ≥ 4 features — it is what screen readers and
  Ctrl+F expect. Cards for 2–3 tiers. Highlight at most one. Show the billing-period toggle's effect
  immediately, no page reload.
- **Stats**: the count-up (`pattern-recipes.md` #10) must land on the real number, must be readable while
  animating, and must show the final value under reduced-motion. Use `tabular-nums`.
- **Testimonial**: one large quote beats a carousel of six. Attribute with name + role + source; an
  unattributed quote reads as invented.
- **Logo strip**: greyscale/opacity so it does not compete, real logos only, and a marquee only if it
  pauses on hover and respects reduced-motion.

---

## §14 Footer

Measured: creative **2 columns / 4 links / 0.5 vh**; product **5 columns / 35 links / 0.6 vh**. Both are
correct for their dialect — the mistake is a 5-column sitemap footer on a 3-page creative site, or a
one-line copyright on a product site that needs legal, docs and status links.

Owed regardless: a real `<footer>` landmark, the year generated not hard-coded, contact that is a real
`mailto:`/link, and — if the site collects anything — privacy/terms. A footer is also the last place to
place the one link that did not fit in the nav.

---

## §15 Checklist

- [ ] Dialect chosen (creative vs product) and every component consistent with it (§1)
- [ ] Radius, shadow and uppercase decisions match the dialect, not habit (§1)
- [ ] Every interactive component has all applicable states, `:focus-visible` included (§2)
- [ ] Hover styling wrapped in `@media (hover: hover)`; nothing essential behind hover (§2)
- [ ] Nav ≤ 6 links + ≤ 1 CTA; mobile menu has open/close/focus-trap/Esc/scroll-lock; skip link present (§3)
- [ ] Exactly one `<h1>`; hero is not the default centred stack (§4)
- [ ] ≤ 3 button roles; hit area ≥ 44px; loading state does not reflow; `<a>` vs `<button>` correct (§5)
- [ ] Tags/badges honest about interactivity; no colour-only meaning; no emoji icons (§6)
- [ ] Cards: not three equal boxes; one of surface/border/nothing; stretched-link pattern; media box reserved (§7)
- [ ] Every image has a reserved box, `srcset`, and honest alt (§8)
- [ ] Every field has a real label, correct `type`/`inputmode`/`autocomplete`, adjacent error text, pending + success states (§9)
- [ ] Accordion is `<details>`; dialog is `<dialog>`; dropdown uses `popover`/anchor with a positioned fallback (§10, §11)
- [ ] Filters in the URL; empty state designed (§12)
- [ ] No invented proof anywhere (§13)
- [ ] Footer matches the dialect; year generated; legal present if anything is collected (§14)
