# Production Polish — 从「能跑」到「像成品」

The page builds, the mechanic works, the design gate passed. It still reads as a demo, because the
twenty things that only show up outside the happy path were never built: the tab has no icon, the link
preview is blank, the 404 is the framework's, the form's error state was never seen, and the whole thing
flashes white on a dark-mode phone.

This is the last file to run, and it is checkable end to end. Nothing here is a matter of taste.

**Measured baseline** — same 32-site run as `components.md` §1. The gap
between the two samples is almost entirely *here*:

| | Creative (n=18) | Product (n=14) |
|---|---|---|
| `<meta name="description">` | 15/18 | **14/14** |
| `og:image` / `og:title` / `og:description` | 16 / 15 / 14 | **14 / 14 / 14** |
| `twitter:card` | 14/18 | **14/14** |
| favicon | 16/18 | **14/14** |
| `apple-touch-icon` | 11/18 | 11/14 |
| `rel=canonical` | **8/18** | 13/14 |
| `lang` on `<html>` | 14/18 | **14/14** |
| exactly one `<h1>` | 10/18 (**5 had zero**) | 11/14 |
| skip link | **0/18** | 4/14 |
| `theme-color` | 6/18 | 6/14 |
| `prefers-color-scheme` rules | 1/18 | 4/14 |
| `<title>` length | median 28.5 chars | median 42.5 chars |

Award-winning creative sites skip this layer routinely. That is a measured habit, not a licence — a page
with no `lang`, no canonical and no `<h1>` is a page that loses to search, to screen readers and to
translation for nothing in return.

---

## §1 The head, in full

Everything below is either present or it is a defect. There is no judgment call.

```html
<!doctype html>
<html lang="zh-Hans">          <!-- or "en" — set it; 4/18 creative sites did not -->
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>Nome — what it is in five words</title>   <!-- 40–60 chars -->
  <meta name="description" content="One sentence, 120–155 chars, written for a human.">
  <link rel="canonical" href="https://example.com/">

  <!-- link previews: Slack, iMessage, X, WeChat, Feishu all read these -->
  <meta property="og:type"        content="website">
  <meta property="og:url"         content="https://example.com/">
  <meta property="og:title"       content="…">
  <meta property="og:description" content="…">
  <meta property="og:image"       content="https://example.com/og.png">  <!-- absolute URL -->
  <meta property="og:image:width"  content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card"       content="summary_large_image">

  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">   <!-- 180×180, no transparency -->
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" media="(prefers-color-scheme: light)" content="#faf9f7">
  <meta name="theme-color" media="(prefers-color-scheme: dark)"  content="#0b0b0c">
  <meta name="color-scheme" content="light dark">
</head>
```

- **`og:image` must be an absolute URL.** A relative one silently produces a blank preview — the single
  most common "why does my link look broken in Slack" cause.
- **`<title>` is a name plus a claim**, 40–60 characters. The creative sample's median of 28.5 is short
  enough that many are just the brand name, which wastes the one line search results show.
- **`theme-color` per scheme** paints the mobile browser chrome. Two lines, and the page stops looking
  like a web view.
- **Favicon**: `.ico` (32px, for legacy) + `.svg` (scales, can be theme-aware) + a 180px PNG for iOS.
  An emoji-as-favicon SVG is fine for a personal page and obviously wrong for a client's.

---

## §2 The OG image

A 1200×630 PNG. Two acceptable ways to get it:

1. **Static** — export the hero's still frame, or a card with the wordmark and the headline. Fine when
   the site is one page.
2. **Generated per route** — `@vercel/og` / `satori`, or Astro's endpoint pattern. Do this when the site
   has an index of projects or posts; a shared OG image across 40 URLs is a missed signal.

Design it as a *card*, not a screenshot: it is rendered at ~500px wide in a feed, so the type must be
enormous and the safe area generous. Test it with the real unfurl (paste the URL into Slack) before
calling it done — most OG bugs are caching or absolute-URL bugs, invisible from the markup.

---

## §3 404, error, and the routes nobody designed

- **A designed 404** with the site's own type and one route back. The framework's default page is the
  loudest possible signal that nobody finished.
- **500 / error boundary**: say what happened in one sentence and give an action. Never show a stack.
- **The empty state of every list** (`components.md` §12).
- **A trailing-slash and case decision**, made once and redirected consistently. Two URLs for one page is
  a real bug that shows up as duplicate analytics and split social counts.
- `robots.txt` and `sitemap.xml` — one line each in most frameworks, and the difference between being
  indexed correctly and being indexed weirdly.

---

## §4 The states that only exist off the happy path

| State | Where it is missing most often | What "done" looks like |
|---|---|---|
| Loading | first paint of a media-heavy scene | a designed hold — not a spinner on white; reserve the layout so nothing jumps |
| Pending | form submit, async action | button label swaps in place, control disabled, no double-submit |
| Success | after submit | persists on the page; a toast that fades is not a receipt |
| Error | form validation, failed fetch | adjacent to the cause, describes the fix, `aria-describedby` |
| Empty | filtered index, search | names the filter and offers the way out |
| Offline / slow | anything fetched | a fallback that is not an infinite skeleton |

**Microcopy is where the page's voice lives.** The 404 line, the empty-state sentence, the text under the
submit button, the error message — these are read more carefully than any headline, because the reader is
stuck. Write them in the same voice as the rest, and never in developer language ("Request failed with
status 422").

---

## §5 Dark mode — only if you mean it

Only **1/18** creative and **4/14** product sites in the sample ship a `prefers-color-scheme` branch. A
page committed to one ground is a legitimate choice — but then commit properly: set `color-scheme` so
form controls, scrollbars and the caret match, or a dark page will render light native widgets.

```css
:root { color-scheme: light; }          /* committed light page */
```

If you do ship both, it is a **level-2 token remap only** (`project-setup.md` §2). If any component needs
editing, the token layer is under-specified.

Use `light-dark()` (Baseline since 2024) rather than duplicating the palette into a media query *and*
an attribute selector — one definition, and a manual toggle works in both directions because it only has
to change `color-scheme`:

```css
:root {
  color-scheme: light dark;                        /* follows the OS by default */
  --bg:         light-dark(#faf9f7, #0b0b0c);
  --surface:    light-dark(#ffffff, #141416);
  --text:       light-dark(#0b0b0c, #f4f3f1);
  --text-muted: light-dark(#6b6b73, #8b8b93);
  --border:     light-dark(color-mix(in oklab, #0b0b0c 16%, transparent),
                           color-mix(in oklab, #f4f3f1 18%, transparent));
}
:root[data-theme="light"] { color-scheme: light; } /* the toggle only touches this */
:root[data-theme="dark"]  { color-scheme: dark;  }
```

- **No flash.** If there is a manual toggle, read the stored preference in a tiny **blocking inline
  script in `<head>`** that stamps `data-theme` on `<html>` before first paint. A `useEffect` toggle
  flashes on every load.
- **The artwork has a second palette** that does not remap (`page-design.md` §5). Photos, video and
  shader output stay as they are — design the chrome to work against both, or ship a different asset.
- **Check contrast in both**, at the busiest frame if type sits over motion.

---

## §6 The small things that read as "finished"

```css
::selection      { background: var(--accent); color: var(--accent-on); }
:root            { accent-color: var(--accent); caret-color: var(--accent); }
html             { scrollbar-gutter: stable; }   /* no width jump when a modal locks scroll */
a                { text-underline-offset: .18em; text-decoration-thickness: from-font; }
:is(a,button)    { -webkit-tap-highlight-color: transparent; }  /* only with a real :active state */
@media print     { … }                            /* if the page has anything worth printing */
```

- `scrollbar-gutter: stable` removes the horizontal jolt every time a dialog locks body scroll — a
  one-line fix for a bug that reads as sloppiness.
- **Removing the tap highlight without adding an `:active` state makes the page feel dead on mobile.**
  The two go together.
- **Text over media needs a floor**, measured at the worst frame, not a lucky screenshot
  (`page-design.md` §3, `verification-harness.md` §2).
- Real apostrophes and quotes (’ “ ”), a non-breaking space before units, `—` not `--`. In Chinese copy:
  full-width punctuation, and no space before a full-width comma.

---

## §7 Structure that machines read

- **One `<h1>`, and no skipped levels.** 5 of 18 creative sites had *zero* `<h1>` — usually because the
  display type is drawn in canvas. If the headline is in the artwork, the DOM still owes a real heading
  (visually hidden if necessary).
- **Landmarks**: `<header>` `<nav aria-label>` `<main id="main">` `<footer>`. A screen-reader user
  navigates by these; a page of `<div>`s has no map.
- **Visually-hidden utility** (not `display:none`, which hides it from AT too):
  ```css
  .vh { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden;
        clip-path:inset(50%); white-space:nowrap; border:0; }
  ```
- **Structured data** (`Organization`, `Person`, `Article`, `BreadcrumbList`) as JSON-LD when the page has
  a real-world referent. Skip it for an art piece.
- **`prefers-reduced-motion` is content, not a toggle** — the reduced version must be a *designed* page
  (`baseline-ui.md` §1).

---

## §8 Analytics, consent, third parties

- **Ship at most one analytics script**, and prefer a cookieless one (Plausible/Umami/Fathom) — no banner
  needed, no consent flow to design, no 45 KB of tag manager on the critical path.
- If the site targets the EU and sets non-essential cookies, the banner is a real component with real
  states — design it, don't paste one that covers the hero on mobile.
- **Every third-party script is a budget line.** Load it `async`/`defer`, after first paint, and re-run
  the budget from `project-setup.md` §8 afterwards.
- Never send analytics from a preview/staging deploy into production data.

---

## §9 Pre-ship: run these, don't estimate them

```bash
npm run build && npm run typecheck        # zero errors AND zero warnings
npx lighthouse <url> --preset=desktop --view
npx lighthouse <url> --form-factor=mobile --throttling-method=simulate --view
npx @unlighthouse/cli --site <url>        # every route, not just the home page
```

Then, by hand, in this order:

1. **Load with JS disabled.** Content present? (For a canvas page: is there anything at all?)
2. **`prefers-reduced-motion: reduce`.** A designed page, not a broken one.
3. **Tab through the whole page.** Visible ring everywhere, order matches reading order, nothing traps.
4. **320 / 375 / 414 / 768 / 1440.** No horizontal scroll (2 of 18 sampled creative sites failed this),
   no two-line buttons, no clipped display type.
5. **Zoom to 200 %.** Nothing clipped, nothing overlapping — this is where a `vw`-only `clamp()` dies.
6. **Real phone, mid-range Android**, not just the simulator.
7. **Paste the URL into Slack** and look at the unfurl.
8. **Submit the form**, including the failing case, and read the error you actually wrote.
9. **Visit a URL that doesn't exist.**
10. Reload five times: no flash, no layout shift, no console error.

---

## §10 Checklist

- [ ] `lang`, `<title>` 40–60 chars, description, canonical present (§1)
- [ ] og:title / description / **absolute** og:image 1200×630 / twitter:card, verified by a real unfurl (§1, §2)
- [ ] favicon `.ico` + `.svg` + apple-touch-icon; `theme-color` per scheme (§1)
- [ ] Designed 404; robots.txt + sitemap.xml; trailing-slash/case decided and redirected (§3)
- [ ] Loading / pending / success / error / empty states all built and seen at least once (§4)
- [ ] `color-scheme` set; dark mode either shipped as a token remap with no flash, or deliberately not shipped (§5)
- [ ] `::selection`, `accent-color`, `scrollbar-gutter`, tap-highlight-with-`:active`, real punctuation (§6)
- [ ] Exactly one `<h1>` in the DOM even if the display type lives in canvas; landmarks present; skip link present (§7)
- [ ] ≤ 1 analytics script; third parties deferred; budget re-measured after adding them (§8)
- [ ] All ten manual checks in §9 actually performed, not estimated
