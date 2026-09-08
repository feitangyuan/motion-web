# Motion Tokens

Complete reference for duration, easing, spring config, and stagger values.
Use these as your first lookup before inventing ad-hoc numbers.

---

## Duration Scale

| Token | Value | Intent |
|---|---|---|
| `instant` | 80–100ms | Cursor feedback, tooltip show/hide |
| `fast` | 150–200ms | Hover states, button active, toggle |
| `standard` | 280–350ms | Card expand, panel slide, drawer |
| `medium` | 400–500ms | Section reveal, image open, scroll trigger |
| `slow` | 600–800ms | Page enter, hero text reveal, route transition |
| `cinematic` | 1000–1400ms | Cold-open beat, curtain wipe, dramatic entrance |
| `ambient` | continuous | Background loop, particle field, breathing glow |

Rule: if you can't justify a duration with the intent column, halve it.

---

## Easing Dictionary

### Standard Curves (CSS / Framer tween)

| Name | CSS cubic-bezier | Character |
|---|---|---|
| `ease-out-expo` | `cubic-bezier(0.16, 1, 0.3, 1)` | Fast in → soft landing. Default for reveals. |
| `ease-in-expo` | `cubic-bezier(0.7, 0, 0.84, 0)` | Slow start → hard exit. Use for exits only. |
| `ease-in-out-quart` | `cubic-bezier(0.76, 0, 0.24, 1)` | Symmetrical smooth. Good for auto-play loops. |
| `ease-out-back` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Slight overshoot landing. Playful hovers. |
| `ease-out-circ` | `cubic-bezier(0, 0.55, 0.45, 1)` | Very fast decel. Crisp mechanical feel. |
| `ease-sharp` | `cubic-bezier(0.65, 0, 0.45, 1)` | Hard brand slam. Broadside openings. |
| `ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` | Material default. Safe baseline. |
| `ease-expressive` | `cubic-bezier(0.68, -0.6, 0.32, 1.6)` | Overshooting both ends. Very playful — use rarely. |
| `linear` | `linear` | Scroll-scrub animations, shader uniforms. |

### Spring Config (Framer Motion / motion library)

| Preset | stiffness | damping | mass | Character |
|---|---|---|---|---|
| `spring-gentle` | 100 | 15 | 1 | Soft, slow, no bounce. Ambient reveals. |
| `spring-default` | 200 | 22 | 1 | Natural feel. Card hovers, drawer slides. |
| `spring-snappy` | 350 | 28 | 1 | Premium fast snap. Button feedback. |
| `spring-bouncy` | 200 | 10 | 1 | Playful overshoot. Game-like icons. |
| `spring-heavy` | 150 | 35 | 1.5 | Weighted, sluggish. Large hero panels. |
| `spring-stiff` | 500 | 40 | 1 | Near-instant. Mouse-tracking cursors. |

```js
// Framer Motion usage
transition={{ type: "spring", stiffness: 350, damping: 28 }}

// GSAP equivalent (approximate with ease config)
gsap.to(el, { ease: "elastic.out(1, 0.6)", duration: 0.8 })
```

### GSAP Named Eases

| GSAP Ease | Equivalent Feel |
|---|---|
| `power4.out` | Very fast reveal, soft landing → closest to `ease-out-expo` |
| `power2.inOut` | Smooth loop → near `ease-in-out-quart` |
| `back.out(1.7)` | Overshoot landing → near `ease-out-back` |
| `elastic.out(1, 0.5)` | Spring bounce → use for playful icon confirms |
| `expo.out` | Equivalent to `ease-out-expo` |
| `circ.out` | Crisp mechanical → `ease-out-circ` |
| `sine.inOut` | Very gentle loop, breathing effects |

---

## Stagger Patterns

| Pattern | Value | Use |
|---|---|---|
| `tight-grid` | 0.04s per item | Data grid row entry, developer tool panels |
| `standard-list` | 0.07–0.08s | Card lists, feature grids, nav links |
| `editorial-line` | 0.08–0.1s per line | Text reveals, article sections |
| `dramatic-cascade` | 0.12–0.18s | Award-site heroes, broadside reveals |
| `no-stagger` | 0s | Single decisive CTA entrance, snappy brand moves |

Stagger direction: default top-to-bottom. Use `from: "center"` for radial effects. Use `from: "end"` for exits.

### Native CSS stagger (no JS, no per-item index)

```css
.item { animation-delay: calc(sibling-index() * 60ms); }   /* 1-based position among siblings */
```

`sibling-index()` / `sibling-count()` remove the usual `style="--i:3"` plumbing entirely. Chromium first;
keep the un-delayed animation as the fallback (a missing delay is a stagger of 0, which is safe — a
missing *animation* is not). See `pattern-recipes.md` #16 for the support matrix and authoring order.

### `linear()` — real spring/bounce curves in plain CSS

`cubic-bezier()` cannot express overshoot-and-settle; `linear()` can, by listing sampled points, and it is
broadly supported (unlike the scroll-timeline features). Generate the stops from the same spring config
you would have given the JS — this is how a CSS-only element matches the handfeel of a sprung one:

```css
transition-timing-function: linear(0, 0.32 8%, 0.79 20%, 1.03 30%, 1.01 46%, 1);
```

Use it for the small stuff (a button, a chip, a toggle) so the page keeps one motion character without
booting an animation library for every element.

---

## Transform Property Budget

Performance tiers — stay in the cheap tier by default:

| Tier | Properties | GPU composite? | Cost |
|---|---|---|---|
| **Cheap** | `transform` (translate, scale, rotate, skew), `opacity` | ✅ Yes | Always safe |
| **Medium** | `filter: blur()`, `filter: brightness()`, `clip-path` | ⚠️ Partial | OK if area is small |
| **Expensive** | `width`, `height`, `padding`, `margin`, `top`, `left` | ❌ No — causes layout | Avoid in animation |
| **Very expensive** | `box-shadow` (large blur), `border-radius` during scale | ❌ Paint | Avoid in animation |

Rule: if you're animating layout properties (width/height), switch to `scaleX`/`scaleY` with a transform-origin trick.

---

## Reduced Motion Fallback Ladder

For every motion you design, define a fallback in this order:

1. **Opacity only**: fade in/out with `duration: 200ms` — always safe.
2. **Translate only**: small `translateY(8px → 0)` — safe for most users.
3. **No motion**: `display: none → block`, no transition — for severe vestibular disorders.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

Always test: open DevTools → Rendering → Emulate prefers-reduced-motion.

---

## `will-change` Rules

Use `will-change: transform` only on elements actively animating. Remove it after the animation completes. Never apply it globally.

```js
// Correct: add before animation, remove after
el.style.willChange = 'transform';
gsap.to(el, { x: 100, onComplete: () => el.style.willChange = 'auto' });
```

Too many `will-change` declarations = wasted GPU memory = lower FPS on mobile.
