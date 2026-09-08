# Project Setup — 0→1 把一个网页真的立起来

`page-design.md` decides what the page looks like. This file decides what it *is*: which stack, which
token layer, which type and space scale, how fonts and images load, and where it deploys. It is the
half that has to exist before any of the design decisions can be typed into a file.

**The rule this file exists to enforce:** the stack is chosen from the page's shape, never from habit.
Reaching for Next.js because that is what you always scaffold is the same failure as reaching for R3F
because the reference "looks 3D" (`build-mode.md` ladder) — a rung too high, paid for on every
iteration afterwards.

Two ladders are in play and they are **independent**:
- **This file's ladder** = how the page is authored and shipped (HTML file → Vite → Astro → Next.js)
- **`build-mode.md`'s ladder** = how the motion is driven (CSS → rAF → GSAP → Three.js)

A single hand-written `.html` file can host a Three.js scene. A Next.js app can ship zero animation.
Do not let one ladder pick the other.

---

## §1 Page stack ladder (climb only when the lower rung fails)

| Rung | Stack | Reaches | Climb when |
|---|---|---|---|
| **0** | One `.html` file + one `.css` + one `.js`, no build | a single page, any amount of motion, deployable by drag-and-drop | never needed a component, a second route, or npm |
| **1** | **Vite** + vanilla TS/JS, no framework | multi-file source, HMR, npm libraries (GSAP, Lenis, Three), still one or two pages | you want imports and HMR, not components |
| **2** | **Astro** + islands | many pages, content collections (`.md`/`.mdx`), MDX blog/docs, zero JS by default with React/Svelte islands where interaction lives | ≥ 5 routes, or content authored as files, or SEO-heavy |
| **3** | **Next.js** (App Router) | auth, database, dynamic routes, server actions, ISR, an actual product behind the page | there is a *product*, not just a page |

**Rung 0 is the one that gets skipped, and it is right more often than it gets used.** A motion-first
creative page is frequently one route with a hand-written DOM and a rAF loop. Every layer above adds a
build step to the iteration loop, and iteration speed is the resource the design gate consumes most
(`design-slop.md` — every gate hit is a revision). If the page has one route and no content model, start
at rung 0 and climb only when a second route or a repeated component appears.

**Rung 2 vs rung 3 is decided by one question: is there a product behind the page?** Astro renders to
static HTML with opt-in islands, so a marketing page ships near-zero JS; Next.js is a React app that can
also render marketing pages. For a marketing/portfolio/campaign site with no auth and no database, Astro
is the cheaper and faster answer. Choose Next.js when the same codebase also has to serve the logged-in
product, or when the team is already React-only and the switching cost outweighs the bundle.

**Never**: Create React App (dead), a hand-rolled Webpack config, or a framework picked to justify a
component library. If a template is used, read every file in it before shipping — most landing-page
templates carry an invented-proof section (`design-slop.md` A8) and a violet gradient (A4).

**React is not required for a component tree.** Astro components, or plain template functions in rung 0/1,
cover 90% of a marketing page's reuse. Introduce React when something has real client state that spans
components — a filterable index, a configurator, a multi-step form.

---

## §2 The token layer — three levels, one substrate

Every stack on the ladder ends at the same substrate: **CSS custom properties on `:root`**. Tailwind v4's
`@theme` *is* that — it declares tokens in CSS and emits them as variables plus utilities. So write the
token layer once, in CSS, and let the framework consume it.

Three levels, and skipping the middle one is the most common cause of "changing the accent colour meant
editing 40 files":

```css
:root {
  /* 1 · PRIMITIVE — raw values, no meaning. Named by what they are. */
  --ink-900:#0b0b0c; --ink-700:#2a2a2e; --ink-400:#8b8b93; --ink-100:#e6e6e9;
  --paper:#faf9f7;  --ember-500:#d8552b;  --ember-600:#b8431f;

  /* 2 · SEMANTIC — roles the page actually reasons about. UI code only uses these. */
  --bg:            var(--paper);
  --surface:       #ffffff;
  --surface-sunk:  var(--ink-100);
  --border:        color-mix(in oklab, var(--ink-400) 32%, transparent);
  --text:          var(--ink-900);
  --text-muted:    var(--ink-400);
  --accent:        var(--ember-500);
  --accent-hover:  var(--ember-600);
  --accent-on:     var(--paper);          /* text colour ON the accent */
  --focus:         var(--ember-500);

  /* 3 · COMPONENT — only when a component genuinely deviates from the role */
  --btn-radius: 999px;
  --card-radius: 14px;
}
```

Rules that make the layer worth having:

- **Component CSS may only read level 2.** A `background: var(--ink-900)` inside a card is a level-1 leak
  and it is exactly what breaks when the palette changes or dark mode arrives.
- **Name roles by function, not appearance.** `--surface-sunk`, not `--gray-50`. The day the ground turns
  black, `--gray-50` becomes a lie and `--surface-sunk` stays true.
- **Dark mode is a level-2 remap only.** If dark mode needs component edits, level 2 is under-specified
  → `production-polish.md` §5.
- **`color-mix(in oklab, …)` for borders/scrims** instead of a hand-picked grey. It stays correct across
  both grounds and gives you one border token instead of two.
- **Keep the palette small.** Median across current award winners is **4 distinct dominant colours**, and
  the ground is black or white in 14/15 (`page-design.md` §2). A 10-step ramp per hue is a dashboard
  habit; a creative page needs three neutrals and one accent.

**Tailwind v4** — same tokens, declared in `@theme` so utilities generate from them:

```css
@import "tailwindcss";
@theme {
  --color-bg: #faf9f7;
  --color-surface: #ffffff;
  --color-text: #0b0b0c;
  --color-accent: #d8552b;
  --radius-btn: 999px;
  --font-display: "Editorial", Georgia, serif;
  --text-display: clamp(3rem, 1.2rem + 7.4vw, 9rem);
}
```
This yields `bg-bg`, `text-accent`, `rounded-btn`, `font-display`, `text-display`, **and** the raw
`var(--color-accent)` for hand-written CSS and GSAP. There is no `tailwind.config.js` in v4 — a config
file in a v4 project is a migration leftover, not a requirement.

---

## §3 Type and space scales — fluid, and anchored to a real ratio

### The scale must have a jump, not a ramp

Measured target from `page-design.md` §2: display ÷ body ≈ **8×** median across current award winners
(range 3.3–14×), body commonly **12–16px**, display **52–218px**. A page where everything lives between
16 and 48px is the single most reliable "没设计感" cause. Build the scale so the jump is structural:

```css
:root {
  /* body ladder — small steps */
  --text-xs:   0.75rem;                                    /* 12 */
  --text-sm:   0.875rem;                                   /* 14 */
  --text-base: 1rem;                                       /* 16 */
  --text-lg:   clamp(1.125rem, 1.05rem + 0.35vw, 1.375rem);

  /* the jump */
  --text-h3:   clamp(1.5rem,  1.2rem  + 1.5vw,  2.25rem);
  --text-h2:   clamp(2.25rem, 1.5rem  + 3.6vw,  4.5rem);
  --text-h1:   clamp(3.5rem,  1.4rem  + 9.6vw, 10rem);     /* ≈8× base at desktop */
}
```

**The `clamp()` formula.** For a size going from `minPx` at viewport `minVw` to `maxPx` at `maxVw`:
```
slope      = (maxPx - minPx) / (maxVw - minVw)
intercept  = minPx - slope * minVw            /* in px, then ÷16 for rem */
clamp( {minPx/16}rem , {intercept/16}rem + {slope*100}vw , {maxPx/16}rem )
```
[utopia.fyi](https://utopia.fyi) generates both the type and space scales in this form; use it rather
than hand-solving each step.

**Accessibility floor on `clamp()`:** the middle term must contain a `rem` component, never `vw` alone.
A pure-`vw` size ignores the user's browser font setting and fails WCAG 1.4.4 (resize to 200%). The
formula above always keeps the `rem` intercept — that is what makes it safe.

### Line-height and tracking move with size

| | `line-height` | `letter-spacing` |
|---|---|---|
| Display (≥ 3rem) | 0.95 – 1.05 | −0.03em to −0.04em |
| Heading (1.5–3rem) | 1.15 – 1.25 | −0.01em to −0.02em |
| Body | 1.5 – 1.65 | 0 |
| Small caps / eyebrow | 1.2 | +0.08em to +0.14em, uppercase |

One line-height across the whole scale is a reliable amateur tell (`page-design.md` §4). **CJK display
type inverts the tracking rule**: negative tracking closes counters on 黑体 fast, and line-height wants
**more**, not less (≈1.4–1.6 even at display size).

### Space scale

Use a small set and vary section spacing *with intent* — even spacing reads as a list (`page-design.md` §6).

```css
:root {
  --space-2xs: .5rem;  --space-xs: .75rem; --space-s: 1rem;  --space-m: 1.5rem;
  --space-l: 2.5rem;   --space-xl: 4rem;   --space-2xl: 6rem;
  --section-tight:   clamp(3rem, 2rem + 4vw, 6rem);
  --section-normal:  clamp(5rem, 3rem + 7vw, 10rem);
  --section-loose:   clamp(8rem, 4rem + 12vw, 18rem);   /* before a beat you want landed */
}
```

### Measure, not a global column

Current practice: **no `body { max-width }` on 15/15 sampled award sites** — each element sets its own
measure (`page-design.md` §2). Encode that as a utility, not a wrapper:

```css
.measure     { max-width: 68ch; }        /* running text */
.measure-narrow { max-width: 48ch; }     /* lead paragraph, pull quote */
.gutter      { padding-inline: clamp(1rem, 5vw, 6rem); }
```

---

## §4 Fonts — the one thing that shifts the layout

- **Self-host `.woff2`.** A Google Fonts `<link>` costs a third-party connection on the critical path,
  and since cache partitioning it is not shared across sites anyway. Download, subset, serve from origin.
- **Preload only what paints above the fold** — usually one display face, one body weight. Preloading six
  files makes the first paint slower, not faster.
  ```html
  <link rel="preload" href="/fonts/display.woff2" as="font" type="font/woff2" crossorigin>
  ```
- **`font-display: swap`** for body; `optional` is defensible for a decorative display face you would
  rather drop than shift.
- **Kill the swap shift with metric overrides.** This is the fix that most pages skip and then blame on
  "CLS from fonts":
  ```css
  @font-face {                 /* a fallback tuned to the real face's metrics */
    font-family: "Display Fallback";
    src: local("Georgia");
    size-adjust: 104%; ascent-override: 88%; descent-override: 22%; line-gap-override: 0%;
  }
  @font-face { font-family: "Display"; src: url(/fonts/display.woff2) format("woff2");
               font-display: swap; }
  :root { --font-display: "Display", "Display Fallback", Georgia, serif; }
  ```
  Derive the percentages from the real face's metrics (`fontkit`, or Next.js `next/font` does it
  automatically). Done right, the swap is invisible and CLS from fonts is zero.
- **Variable fonts**: one file covering the weight range beats four static files the moment you use more
  than two weights. Animate weight only if you meant to — it is a layout-affecting property.
- **CJK**: never preload a full face (5–12 MB). Subset by the characters the page actually uses, or split
  with `unicode-range` so only the needed ranges download. For most Chinese pages the honest answer is a
  well-chosen **system stack** (`"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`) plus a webfont for
  the display line only.
- **Always name a real fallback stack.** `font-family: "Whatever"` with no fallback renders Times.

---

## §5 Cascade layers — one order, no specificity wars

```css
@layer reset, base, layout, components, motion, utilities, overrides;
```
Everything goes in a layer; later layers always win regardless of selector strength, which is what makes
a utility class beat a component rule without `!important`. This is the same order as `build-mode.md`'s
CSS layering rules, just enforced by the cascade instead of by file order.

The `reset` layer, minimally and currently:

```css
@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  * { margin: 0; }
  html { -webkit-text-size-adjust: 100%; interpolate-size: allow-keywords; }
  body { min-height: 100svh; line-height: 1.5; -webkit-font-smoothing: antialiased; }
  img, picture, video, canvas, svg { display: block; max-width: 100%; }
  input, button, textarea, select { font: inherit; color: inherit; }
  p, h1, h2, h3, h4 { overflow-wrap: break-word; }
  h1, h2, h3 { text-wrap: balance; }        /* no orphan word in a headline */
  p          { text-wrap: pretty; }         /* Chrome/Safari; harmless elsewhere */
  :target    { scroll-margin-block: 5svh; }
  @media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
}
```

Notes on the 2026 lines specifically:
- `text-wrap: balance` on headings and `pretty` on body is the cheapest typographic upgrade available;
  Firefox ignores `pretty` and renders normally — no fallback needed.
- `interpolate-size: allow-keywords` makes `height: auto` animatable, which removes the classic
  measure-then-set-pixel-height JS for accordions (Chromium only; the JS path stays the fallback).
- `100svh` not `100vh` — `vh` on mobile is the *large* viewport and gets cut off by the URL bar.
- **Do not put `overflow-x: hidden` on `html`** to hide a leak; it silently breaks `position: sticky`
  in some containers. Use `overflow-x: clip` and then go find the element that is actually wide
  (`baseline-ui.md` §6).

---

## §6 File layout

```
rung 0                     rung 1 (Vite)              rung 2 (Astro)
index.html                 index.html                 src/
styles.css                 src/                         layouts/Base.astro
main.js                      main.ts                    components/{ui,sections}/
assets/                      styles/                    pages/index.astro
                               tokens.css               content/                 # md/mdx collections
                               reset.css                styles/tokens.css
                               layout.css               assets/
                             modules/                 public/                    # favicon, og, fonts
                               scroll.ts
                           public/
```

Two conventions worth keeping at every rung:
- **`ui/` vs `sections/`.** `ui/` is the component vocabulary (Button, Field, Card, Tag) — reusable,
  content-free. `sections/` is the page vocabulary (Hero, Manifesto, WorkIndex, FAQ, Footer) — used once
  or twice, owns its own copy. Mixing them is what produces a `components/` folder of 40 files where
  nobody can tell what is reusable.
- **`tokens.css` is imported first and imported once.** If a second file also defines `--accent`, the
  token layer has already failed.

---

## §7 Images — the other half of the first paint

- **Formats**: AVIF → WebP → JPEG in a `<picture>`, or let the framework do it (`astro:assets`,
  `next/image`). Serve **PNG only for real transparency**.
- **Always reserve the box.** `width` + `height` attributes, or `aspect-ratio` in CSS. An image without a
  reserved box is the single largest source of CLS, and animation on a shifting layout looks broken in a
  way no easing fixes (`baseline-ui.md` §5).
- **The LCP image is special**: `fetchpriority="high"`, no `loading="lazy"`, and preload it if it is
  discovered late (e.g. it is a CSS background). Every *other* image gets
  `loading="lazy" decoding="async"`.
- **`srcset` + `sizes` or you are shipping the desktop file to phones.** `sizes` describes the CSS box,
  not the file:
  ```html
  <img src="/hero-1200.jpg" alt=""
       srcset="/hero-600.avif 600w, /hero-1200.avif 1200w, /hero-2000.avif 2000w"
       sizes="(max-width: 780px) 100vw, 55vw"
       width="2000" height="1250" fetchpriority="high">
  ```
- **Never serve more than 2× the CSS box.** A 4000px file in a 600px slot costs decode time and memory
  for nothing. For scene assets the per-element budget is stricter and computed —
  `image-asset-pipeline.md` §6.
- **`<img>` beats `background-image` for anything that matters**: background images are not LCP
  candidates in the same way, cannot carry `srcset`, and are invisible to alt text.
- **Alt text is content, not compliance.** Decorative → `alt=""`. Meaningful → describe the thing.

---

## §8 Budget and deploy

Numbers to hold a creative page to (they are budgets, so print them and check, don't estimate):

| | Target | How |
|---|---|---|
| JS shipped to a marketing page | < 100 KB gzip (rung 0–2 usually < 30 KB) | `vite build --report`, `npx source-map-explorer` |
| LCP | < 2.5 s on 4G / mid Android | Lighthouse mobile, not desktop |
| CLS | < 0.05, ideally 0 | reserved boxes + font metric overrides |
| INP | < 200 ms | nothing heavy in a pointer handler; see `build-mode.md` RAF discipline |
| Fonts on first paint | ≤ 2 files | preload audit |

Deploy: **Cloudflare Pages / Netlify / Vercel** are all one command for rungs 0–2; pick on where the rest
of the stack lives. Prerender everything that can be prerendered — a creative page with no per-request
data has no reason to be server-rendered. Set long `Cache-Control` with hashed filenames for
`/assets/*`, and short for HTML.

**Verify the build before calling it done** — zero errors *and* zero warnings, type-check included. A
page that only runs under `dev` is not shipped.

---

## §9 Checklist

- [ ] Page stack chosen from route count + "is there a product behind it", not from habit (§1)
- [ ] Token layer has all three levels; component CSS reads only semantic tokens (§2)
- [ ] Palette ≤ ~4 dominant colours, ground committed (§2, `page-design.md` §2)
- [ ] Type scale has a real jump (display ÷ body ≥ 4×, target ≈ 8×) and every `clamp()` keeps a `rem` term (§3)
- [ ] Line-height and tracking vary with size; CJK rule applied if the page has Chinese display type (§3)
- [ ] Measure set per element; no global centred column (§3)
- [ ] Fonts self-hosted, ≤ 2 preloaded, metric-override fallback in place, real fallback stack named (§4)
- [ ] `@layer` order declared once; reset includes `svh`, `text-wrap`, `overflow-x: clip` discipline (§5)
- [ ] `ui/` and `sections/` separated; one `tokens.css` (§6)
- [ ] Every image has a reserved box; LCP image prioritised, everything else lazy; `srcset`+`sizes` present (§7)
- [ ] Budget numbers measured, not estimated; build passes with zero warnings (§8)
