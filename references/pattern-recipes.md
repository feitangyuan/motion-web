# Pattern Recipes

Ready-to-use motion pattern implementations for creative web. Each recipe includes:
- What it does and when to use it
- Vanilla JS / CSS implementation
- Framer Motion variant
- GSAP variant
- Performance notes and reduced-motion fallback

---

## 1. Text Split Reveal (Line by Line)

**What**: Each line of a heading is wrapped in a clip-path mask and slides up into view.
**Use for**: Editorial section headers, hero text, chapter titles. (Arc: `editorial`, `cold-open`)

### Vanilla JS + CSS
```js
// Split text into lines (simple word-count approach or use SplitType library)
function splitLines(el) {
  const words = el.textContent.trim().split(' ');
  el.innerHTML = words.map(w => `<span class="word">${w}&nbsp;</span>`).join('');
  
  // Group words into visual lines by top offset
  const lines = [];
  let currentLine = [], lastTop = -1;
  el.querySelectorAll('.word').forEach(word => {
    const top = word.getBoundingClientRect().top;
    if (top !== lastTop && lastTop !== -1) lines.push(currentLine), currentLine = [];
    currentLine.push(word);
    lastTop = top;
  });
  if (currentLine.length) lines.push(currentLine);
  
  // Wrap each line in a clip container
  lines.forEach(lineWords => {
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'overflow:hidden; display:block';
    const inner = document.createElement('div');
    inner.className = 'line-inner';
    inner.style.cssText = 'transform: translateY(105%); will-change: transform';
    lineWords.forEach(w => inner.appendChild(w));
    wrapper.appendChild(inner);
    el.appendChild(wrapper);
  });
}

// Animate in (use IntersectionObserver for scroll trigger)
function revealText(el, delay = 0) {
  el.querySelectorAll('.line-inner').forEach((line, i) => {
    line.animate([
      { transform: 'translateY(105%)' },
      { transform: 'translateY(0)' }
    ], {
      duration: 700,
      delay: delay + i * 80,
      easing: 'cubic-bezier(0.77, 0, 0.18, 1)',
      fill: 'forwards'
    });
  });
}
```

### GSAP + SplitText
```js
import { SplitText } from 'gsap/SplitText';
gsap.registerPlugin(SplitText);

const split = new SplitText('.hero-title', { type: 'lines', linesClass: 'line-wrap' });
gsap.set(split.lines, { yPercent: 105 });

// On trigger:
gsap.to(split.lines, {
  yPercent: 0,
  duration: 0.7,
  stagger: 0.08,
  ease: 'power4.out'
});
```

**Reduced motion**: `opacity: 0 → 1` with no translateY. Keep the stagger but reduce it to 0.

---

## 2. Magnetic Hover

**What**: An element (button, icon, avatar) bends toward the cursor when the mouse enters its radius.
**Use for**: CTAs, social icons, nav links, creative portfolio buttons.

```js
function magnetize(el, strength = 0.4) {
  const rect = () => el.getBoundingClientRect();
  
  el.addEventListener('mousemove', (e) => {
    const r = rect();
    const cx = r.left + r.width / 2;
    const cy = r.top + r.height / 2;
    const dx = (e.clientX - cx) * strength;
    const dy = (e.clientY - cy) * strength;
    el.style.transform = `translate(${dx}px, ${dy}px)`;
    el.style.transition = 'transform 0.1s linear';
  });
  
  el.addEventListener('mouseleave', () => {
    el.style.transform = 'translate(0, 0)';
    el.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
  });
}

// Apply to all magnetic elements
document.querySelectorAll('[data-magnetic]').forEach(el => magnetize(el, 0.35));
```

**Framer Motion**:
```jsx
const [position, setPosition] = useState({ x: 0, y: 0 });
// onMouseMove: calculate delta → setPosition → animate with spring
<motion.button animate={position} transition={{ type: 'spring', stiffness: 500, damping: 40 }}>
```

**Reduced motion**: Remove the translate entirely. Keep only the `background-color` hover state.

---

## 3. Clip-Path Curtain Reveal

**What**: An image or block reveals itself by animating a clip-path from closed to open, like a curtain being pulled.
**Use for**: Project thumbnails, editorial images, section transitions.

```css
.reveal-container {
  clip-path: inset(0 100% 0 0); /* closed: right edge at left */
  transition: clip-path 0.8s cubic-bezier(0.77, 0, 0.18, 1);
}
.reveal-container.in-view {
  clip-path: inset(0 0% 0 0); /* fully open */
}
```

**Direction variants**:
- Bottom-up: `inset(100% 0 0 0)` → `inset(0 0 0 0)`
- Center-out: `inset(0 50% 0 50%)` → `inset(0 0% 0 0%)`
- Diagonal: Use `polygon()` clip-path for diagonal wipe

**GSAP ScrollTrigger**:
```js
gsap.fromTo('.reveal-img', 
  { clipPath: 'inset(0 100% 0 0)' },
  { clipPath: 'inset(0 0% 0 0)', duration: 0.9, ease: 'power4.out',
    scrollTrigger: { trigger: '.reveal-img', start: 'top 80%' }
  }
);
```

**Image scale trick** (feels more cinematic): Scale the image inside to 1.15x while the container reveals at 1x. When reveal completes, scale image back to 1x. This gives a "camera pull" effect.

---

## 4. Scroll-Velocity Skew

**What**: Elements skew on the Y (or X) axis proportional to how fast the user is scrolling. The faster the scroll, the more lean. Snaps back elastically on slow/stop.
**Use for**: Large serif headings, editorial sections, hero type.

```js
let lastScroll = 0, velocity = 0, skew = 0;
const maxSkew = 5; // degrees

function onScroll() {
  const current = window.scrollY;
  velocity = (current - lastScroll);
  lastScroll = current;
}

function tick() {
  // Lerp skew toward velocity target
  const target = Math.max(-maxSkew, Math.min(maxSkew, velocity * 0.08));
  skew += (target - skew) * 0.1; // spring damping
  velocity *= 0.9; // decay
  
  document.querySelectorAll('.skew-text').forEach(el => {
    el.style.transform = `skewY(${skew}deg)`;
    el.style.willChange = Math.abs(skew) > 0.05 ? 'transform' : 'auto';
  });
  
  requestAnimationFrame(tick);
}

window.addEventListener('scroll', onScroll, { passive: true });
tick();
```

**Performance**: Keep `will-change` conditional (only set when `|skew| > 0.05`). This prevents wasted GPU allocation when the page is static.

---

## 5. Horizontal Scroll Rail

**What**: A section scrolls horizontally while the page scroll is vertical. The section "pins" in place while the horizontal rail scrubs through.
**Use for**: Portfolio project galleries, timeline sequences, case study slides.

### GSAP ScrollTrigger (preferred)
```js
const rail = document.querySelector('.h-rail');
const items = rail.querySelectorAll('.h-item');

gsap.to(items, {
  xPercent: -100 * (items.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: rail,
    pin: true,
    scrub: 1,
    snap: 1 / (items.length - 1),
    end: () => `+=${rail.offsetWidth}`
  }
});
```

**Mobile**: Never pin on mobile. Use `gsap.matchMedia()`:
```js
mm.add('(min-width: 768px)', () => {
  // horizontal scroll setup
});
// Mobile: just vertical stack, no pin
```

---

## 6. Parallax Depth Stack

**What**: Multiple layers move at different speeds during scroll, creating spatial depth.
**Use for**: Hero sections, product atmosphere, editorial feature images.

```js
const layers = [
  { el: document.querySelector('.layer-bg'), speed: 0.2 },
  { el: document.querySelector('.layer-mid'), speed: 0.5 },
  { el: document.querySelector('.layer-fg'), speed: 0.8 },
];

// RAF loop (no ScrollTrigger dependency)
function parallaxTick() {
  const scrollY = window.scrollY;
  layers.forEach(({ el, speed }) => {
    el.style.transform = `translateY(${scrollY * speed * -1}px)`;
  });
  requestAnimationFrame(parallaxTick);
}
parallaxTick();
```

**Important**: Wrap each layer in `overflow: hidden` and give it extra height/width so it doesn't clip early. Layer items need `position: absolute` inside a `position: relative` container.

---

## 7. Cursor Trail / Custom Cursor

**What**: A custom circle follows the mouse with spring lag. Optionally morphs on hover states.
**Use for**: Creative portfolios, award sites, interactive product pages.

```js
const cursor = document.querySelector('.cursor');
let cx = 0, cy = 0, tx = 0, ty = 0;

document.addEventListener('mousemove', (e) => {
  tx = e.clientX;
  ty = e.clientY;
});

function cursorTick() {
  cx += (tx - cx) * 0.12; // spring damping
  cy += (ty - cy) * 0.12;
  cursor.style.transform = `translate(${cx - 12}px, ${cy - 12}px)`;
  requestAnimationFrame(cursorTick);
}
cursorTick();

// Expand on hover
document.querySelectorAll('a, button, [data-cursor-expand]').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('expanded'));
  el.addEventListener('mouseleave', () => cursor.classList.remove('expanded'));
});
```

**CSS**:
```css
.cursor {
  position: fixed; top: 0; left: 0;
  width: 24px; height: 24px;
  border-radius: 50%; background: rgba(0,0,0,0.8);
  pointer-events: none; z-index: 9999;
  transition: width 0.2s, height 0.2s, background 0.2s;
}
.cursor.expanded { width: 48px; height: 48px; background: rgba(0,0,0,0.4); }
```

**Accessibility**: Always hide `.cursor` on touch devices (`@media (pointer: coarse)`). Never hide the system cursor on non-creative developer sites.

---

## 8. Route / Page Transition (Framer Motion)

**What**: Page content fades or slides out on navigation and the next page fades/slides in.
**Use for**: Next.js portfolios, multi-page creative sites.

```jsx
// _app.tsx or layout.tsx
import { AnimatePresence, motion } from 'framer-motion';

const pageVariants = {
  initial: { opacity: 0, y: 16 },
  enter:   { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] } },
  exit:    { opacity: 0, y: -8, transition: { duration: 0.25, ease: [0.7, 0, 0.84, 0] } }
};

export default function App({ Component, pageProps, router }) {
  return (
    <AnimatePresence mode="wait">
      <motion.div key={router.pathname} variants={pageVariants} initial="initial" animate="enter" exit="exit">
        <Component {...pageProps} />
      </motion.div>
    </AnimatePresence>
  );
}
```

**Gotcha**: `mode="wait"` ensures exit completes before enter starts. Without it, both animate simultaneously and collide.

---

## 9. Scroll-Pinned Sequence (GSAP)

**What**: A section pins to the viewport and plays an animation as the user scrolls through a scroll distance, like a video scrubbed by scroll.
**Use for**: Product feature reveals, storytelling sequences, step-by-step process sections.

```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.pinned-section',
    start: 'top top',
    end: '+=200%',  // scroll 3x the viewport height through this section
    pin: true,
    scrub: 1.5,    // 1.5s lag = smoother scrub
    anticipatePin: 1
  }
});

tl.from('.step-1', { opacity: 0, y: 40 })
  .to('.step-1', { opacity: 0, y: -40 }, '+=0.3')
  .from('.step-2', { opacity: 0, y: 40 })
  .to('.step-2', { opacity: 0 }, '+=0.3')
  .from('.step-3', { opacity: 0, scale: 0.95 });
```

**Mobile fallback**: Replace pinned sequence with a vertical stacked timeline. Use `gsap.matchMedia()` to conditionally disable the pin.

---

## 10. Number/Counter Reveal

**What**: A number animates from 0 (or previous value) to its final value when scrolled into view.
**Use for**: Stats, metrics, data reveals.

```js
function animateCounter(el) {
  const target = parseFloat(el.dataset.target);
  const prefix = el.dataset.prefix || '';
  const suffix = el.dataset.suffix || '';
  const decimals = (String(target).split('.')[1] || '').length;
  
  gsap.fromTo({ val: 0 }, { val: target },
    { duration: 1.4, ease: 'power2.out',
      onUpdate: function() {
        el.textContent = prefix + this.targets()[0].val.toFixed(decimals) + suffix;
      },
      scrollTrigger: { trigger: el, start: 'top 85%', once: true }
    }
  );
}

document.querySelectorAll('[data-counter]').forEach(animateCounter);
```

HTML: `<span data-counter data-target="98.7" data-suffix="%">0%</span>`

---

## 11. SVG Goo Metaball Reveal (悬停/拖拽揭示第二形态)

**What**: A cluster of SVG circles follows the pointer, blurred and re-thresholded via `feGaussianBlur` + `feColorMatrix` so they melt into one blobby shape ("goo" effect). That blob is then used as a `<mask>` over a second image/layer — wherever the pointer drags, the hidden layer shows through. Zero WebGL.
**Use for**: "Reveal the alternate form" interactions — drag to unmask a hidden illustration, hover to reveal a photo negative, paint-away overlays. (✅ 实测 2026-07: drag-across-face → viking helmet reveal)

```jsx
// Trail of N points chasing the pointer with per-point lag (leader-follower chain)
const points = useRef(Array.from({ length: 6 }, () => ({ x: 0, y: 0 })))
const target = useRef({ x: 0, y: 0 })

function tick() {
  const pts = points.current
  pts[0].x += (target.current.x - pts[0].x) * 0.12
  pts[0].y += (target.current.y - pts[0].y) * 0.12
  pts.slice(1).forEach((p, i) => {
    const leader = pts[i]
    const follow = Math.max(0.1, 0.19 - i * 0.014) // later points lag more
    p.x += (leader.x - p.x) * follow
    p.y += (leader.y - p.y) * follow
  })
  // write pts[i].x/.y into each <circle cx cy>
  requestAnimationFrame(tick)
}
```

```jsx
<svg viewBox="0 0 W H">
  <defs>
    <mask id="revealMask" maskUnits="userSpaceOnUse" x="0" y="0" width="W" height="H">
      <rect width="W" height="H" fill="black" />
      <g filter="url(#goo)">
        {points.map((_, i) => <circle key={i} r={radius * Math.max(0.48, 1 - i * 0.1)} fill="white" />)}
      </g>
    </mask>
    <filter id="goo" x="-35%" y="-35%" width="170%" height="170%" colorInterpolationFilters="sRGB">
      <feGaussianBlur stdDeviation="22" result="blur" />
      {/* Pushes the blurred alpha through a steep threshold so overlapping
          blur halos fuse into one blob instead of staying as separate soft circles. */}
      <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9" />
    </filter>
  </defs>
  <g mask="url(#revealMask)">
    <image href={hiddenLayerSrc} width="W" height="H" />
  </g>
</svg>
```

**Tuning**: `stdDeviation` controls blob softness/fusion distance (bigger = circles merge sooner). The `22 -9` matrix values control threshold steepness/cutoff — raise the `22` for a harder edge, shift `-9` to change how much blur survives before disappearing. Radius should grow with pointer speed/drag-state for a "more pressure = bigger blob" feel (compose with handfeel.md §1/§2).

**Reduced motion**: Skip the trail physics — snap the mask circle directly to pointer position, or show the hidden layer at a fixed low opacity instead of gating it behind pointer movement.

---

## 12. Lenis + GSAP ScrollTrigger Canonical Wiring

**What**: The standard three-piece hookup for inertial smooth-scroll (Lenis) driving GSAP's ScrollTrigger. Missing any one piece causes scroll-jank or ScrollTrigger reading stale positions.
**Use for**: Any GSAP ScrollTrigger build that also wants smooth/inertial scrolling rather than native scroll.

```js
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
gsap.registerPlugin(ScrollTrigger)

useEffect(() => {
  const lenis = new Lenis({ lerp: 0.085, smoothWheel: true, anchors: true })
  const update = () => ScrollTrigger.update()
  const raf = (time) => lenis.raf(time * 1000) // Lenis wants ms, gsap.ticker gives seconds

  lenis.on('scroll', update)      // ScrollTrigger must re-read scroll position on every Lenis tick
  gsap.ticker.add(raf)            // drive Lenis off GSAP's own rAF loop, not a second one
  gsap.ticker.lagSmoothing(0)     // disable GSAP's tab-refocus catch-up jump — it fights Lenis's own easing

  return () => {
    gsap.ticker.remove(raf)
    lenis.off('scroll', update)
    lenis.destroy()
  }
}, [])
```

**Gotchas**:
- Skipping `lenis.on('scroll', update)` → ScrollTrigger positions lag a frame behind, pins jitter.
- Running Lenis off its own `requestAnimationFrame` instead of `gsap.ticker` → two competing clocks, occasional double-tick stutter.
- Forgetting `lagSmoothing(0)` → after an alt-tab or long task, GSAP tries to "catch up" the timeline in one jump, which looks like a scroll-teleport since Lenis's position doesn't jump with it.
- `lagSmoothing(0)` is the safe default, but it is not the only setting that works: a shipped build used
  `lagSmoothing(500, 33)` (raise the threshold instead of disabling the mechanism) with no scroll-teleport.
  If you see the catch-up jump *and* dropped frames on heavy sections, try the two-argument form before
  concluding the wiring is wrong.

**Where an R3F canvas fits in this chain**: it doesn't — and that is correct. A background canvas driving
its own `useFrame` loop and reading `window.scrollY` directly is a *third* independent reader of the same
DOM truth, alongside Lenis and ScrollTrigger. Do not try to publish scroll values from one into the other;
they stay in sync because they all read the same source each frame. What you must not do is let the canvas
keep its own integrated scroll estimate — that is the thing that drifts.

**Do you still need Lenis?** Since GSAP 3.13 (2025-04, under Webflow) the entire toolset is free, including
`ScrollSmoother`, `SplitText`, `MorphSVG`, `DrawSVG` and `Inertia` — so the old "ScrollSmoother is paid"
tiebreaker is gone and this is now a real choice. `ScrollSmoother` requires a specific DOM shape
(`#smooth-wrapper` > `#smooth-content`) and is already inside ScrollTrigger's clock; Lenis smooths the
window directly with no wrapper, ships smaller, and hands you raw scroll frames for anything else that
wants them (a canvas, an audio bus). Pick ScrollSmoother when the page is GSAP end-to-end and the DOM is
yours; pick Lenis when the layout is layered/non-standard or something outside GSAP needs the scroll frames.

---

## 13. Scroll-Adaptive Header Theme (背景感知反色 Header)

**What**: A fixed header/nav that flips between light and dark styling based on what section is currently behind it — reading each candidate section's actual computed background color rather than hardcoding "section 3 is dark".
**Use for**: Fixed headers over pages that alternate light/dark full-bleed sections.

```js
function updateHeaderTheme() {
  const probeY = 38 // px from top — where the header visually sits
  // Sections that are dark by design (className allowlist) count directly
  const fixedDark = [...document.querySelectorAll('.is-dark-section')]
    .some(el => { const r = el.getBoundingClientRect(); return r.top <= probeY && r.bottom >= probeY })

  // Sections whose darkness depends on runtime state (theme-morphing scroll sections)
  // must be measured live via computed background luminance, not assumed.
  const dynamic = document.querySelector('.theme-morph-section')
  const rect = dynamic?.getBoundingClientRect()
  const rgb = dynamic ? getComputedStyle(dynamic).backgroundColor.match(/[\d.]+/g)?.map(Number) : null
  const luminance = rgb ? rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114 : 255
  const dynamicDark = Boolean(rect && rect.top <= probeY && rect.bottom >= probeY && luminance < 145)

  setOnDark(fixedDark || dynamicDark)
}

// Re-check on scroll, plus one delayed re-check after scroll settles — Lenis's
// smoothing means the geometry from the scroll event itself is already stale.
window.addEventListener('scroll', () => {
  updateHeaderTheme()
  requestAnimationFrame(() => requestAnimationFrame(updateHeaderTheme))
}, { passive: true })
```

**Why the luminance formula over a class toggle**: some sections change background color as *part of their own scroll animation* (e.g. a scrubbed `backgroundColor` MotionValue) — a static "is this section dark" className can't know the color at the current scroll offset, only a live computed-style read can. Use the class-allowlist path for statically-dark sections (cheaper) and the luminance path only for sections whose background is itself animated.

---

## 14. Drawn Annotation Ring (朱砂圈 — 圈住一个东西，邀请点它)

**What**: A hand-drawn-looking ellipse that *draws itself* around a target, sized to the target's real
painted extent, with an optional leader line + label. The archival-plate / margin-note idiom, not a button.
**Use for**: Inviting a click on something that lives in the artwork rather than in the UI — a figure in a
canvas scene, a region of an image, a hotspot on a diagram. Read `affordance.md` before using this;
the ring is the easy half, the window and the sizing are where these fail.

```html
<div class="callout">
  <!-- preserveAspectRatio="none" lets one ring serve wide and tall subjects alike -->
  <svg viewBox="0 0 76 140" preserveAspectRatio="none" aria-hidden="true">
    <ellipse cx="38" cy="70" rx="36.5" ry="68.5"/>
  </svg>
  <b></b><s>近看</s>
</div>
```
```css
.callout { position: fixed; left: 0; top: 0; transform: translate(-50%, -50%);
           pointer-events: auto; cursor: pointer; }        /* w/h written from JS, see below */
.callout svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible;
               transition: scale .42s ease; }
.callout ellipse {
  fill: none; stroke: var(--accent); stroke-width: 1.9; opacity: .74;
  /* perimeter by Ramanujan for rx 36.5 / ry 68.5 ≈ 341. --draw 1 → 0 = the pen goes round */
  stroke-dasharray: 341; stroke-dashoffset: calc(var(--draw, 0) * 341);
}
.callout:hover svg { scale: 1.07; }
.callout b { position: absolute; right: 92%; bottom: 74%;                 /* leader line */
             width: 5.4vh; height: 1.5px; background: var(--accent);
             rotate: 24deg; transform-origin: right center; }
.callout s { position: absolute; right: 92%; bottom: 74%; translate: -5.2vh -2.6vh;
             text-decoration: none; white-space: nowrap; color: var(--accent); }
```
```js
// every frame while the scene moves — a hardcoded position circles empty ground two seconds later
const b = paintedScreenBox(target)   // affordance.md §6 — painted pixels, not the element box
el.style.left = `${Math.round(b[0])}px`;  el.style.top    = `${Math.round(b[1])}px`
el.style.width = `${Math.round(b[2])}px`; el.style.height = `${Math.round(b[3])}px`
el.style.setProperty('--draw', (1 - ai).toFixed(3))   // ai staggered per ring, affordance.md §5
el.style.pointerEvents = a > 0.5 ? 'auto' : 'none'    // faded-out rings must stop eating the pointer
```

**Three traps, all of them load-bearing:**

- **Don't add `vector-effect: non-scaling-stroke`** to get an even stroke under the non-uniform stretch.
  It moves the dash pattern into screen space, so the `stroke-dasharray` sized to the *user-space*
  perimeter never finishes the draw — the pen stops mid-air. Live with ±25% width anisotropy; on a 1.9px
  hairline that's 1.4–2.4px and invisible, while a half-drawn ring is visible to everyone.
- **Size from the painted bbox, ×1.22–1.30.** The element box includes transparent margin; a couchant
  animal in a tall sprite cell gets circled by a vertical stick. √2 (true circumscription) reads as a
  loose ring floating nearby — the subject's corners are empty anyway.
- **Check where the leader label lands.** With several rings, a label offset up-left from ring #1 can drop
  straight inside ring #2. Hang the label on the outermost ring, pointing into empty space.

**Reduced motion**: skip the draw — set `--draw: 0` and fade opacity 0 → .74 over 200ms. The ring must
still appear; it's the affordance, not decoration.

---

## 15. Verlet Text Curtain (文字帘 — 悬挂、被滚动激励、可拨开)

**What**: A block of copy hung as physical strings — each column is an independent vertical Verlet chain.
Not a cloth: **there are no horizontal constraints at all**. Column density does the visual work of a
sheet, at an order of magnitude less solve cost.
**Use for**: editorial hero copy, poem/lyric sections, a menu that should feel touchable, anything where
the text itself is the material.

```js
// per column, per frame — positions only, velocity is implied by (x - oldX)
for (let it = 0; it < 5; it++) {            // 5 Gauss-Seidel passes is enough at this scale
  for (const [a, b] of constraints) {        // constraints are built INSIDE a column, never across
    const d = dist(a, b), k = (d - rest) / d * 0.5
    a.x += (b.x - a.x) * k; a.y += (b.y - a.y) * k
    b.x -= (b.x - a.x) * k; b.y -= (b.y - a.y) * k
  }
}
// top anchor is soft, not pinned — a hard pin reads as a nail, a soft one as a hem
p.x += (p.initX - p.x) * 0.35
```

**The five numbers that make it read as fabric:**

| Knob | Value | Why |
|---|---|---|
| Solver iterations | 5 / frame | Below 3 the chain stretches visibly; above ~8 buys nothing here |
| Top anchor | soft return `0.35` | Hard pin looks nailed on |
| Pointer repulsion | X full, **Y × 0.35** | Isotropic force squeezes the text into a lump; the anisotropy is what keeps lines readable |
| Repulsion falloff | `(1 - d/70)² × 4.2` | Quadratic, so the edge of the radius is gentle and the centre is decisive |
| Boundary bounce | reflect `oldX/oldY`, restitution `0.6` | Reflecting the *previous* position is how you bounce in Verlet — there is no velocity to negate |

**Scroll injects energy; it does not set position.** This is the part worth stealing even if you never
build a curtain:

```js
scrollEnergy += Math.abs(deltaY) * 0.004
scrollEnergy *= 0.97                                   // per frame
const amp  = 0.014 + scrollEnergy * 0.05
const freq = 0.85  + scrollEnergy * 0.7
sway = Math.sin(t * freq) * amp * (0.35 + 0.65 * (y / height))   // hem moves more than collar
```

Position-driven motion stops dead the instant scrolling stops, which reads as a puppet. Energy-driven
motion keeps ringing and decays — which reads as mass. It is the sibling of `handfeel.md` §3's momentum
guard: that one *rejects* phantom scroll input, this one *stores* real input and spends it over time.

**Per-instance hygiene** (a page usually has several): give each curtain its own `IntersectionObserver`
(`rootMargin: 80px`) so off-screen curtains stop solving, use a sine-hash for the per-column jitter so
no seed needs storing and the scene stays deterministic, and ship a static block under
`prefers-reduced-motion`.

**Variant — fitting the columns to an image's silhouette** (a route that was tried and abandoned, but
whose three traps are real): derive each column's start Y by interpolating the image's alpha contour, and
mark fully transparent columns with `-1` so they're skipped — otherwise text floats in empty air. Compute
the column count from the **measured** container width, not an assumed one, or `startX` goes negative and
the edge columns overlap out of frame. And cap each column's row count by *its own* remaining space, never
a global `maxRows` — a global cap flattens every column onto the bottom edge and prints, in the original
author's words, 「一整条挤在底边的字符污渍」.

---

## 16. Native Scroll Reveal & CSS-Only Stagger (no library, no observer)

**What**: The two things almost every page uses GSAP for — reveal-on-enter and staggered lists — now have
native forms. **Scrubbed** (progress follows scroll) and **triggered** (a normal timed animation fires when
a boundary is crossed) are different features; pick deliberately.

```css
/* A. scrubbed — progress is tied to scroll position (Chrome 115+, Safari 26+) */
.parallax   { animation: drift linear both; animation-timeline: view(); }

/* B. triggered — a normal 0.35s animation, fired once on entry (Chrome 146+, Chromium only) */
.card {
  animation: slide-in .35s ease-out both;
  timeline-trigger: --t view() contain / cover;
  animation-trigger: --t play-forwards play-backwards;   /* reverse on exit; omit the 2nd value to keep it */
}

/* C. stagger with no JS and no per-item index attribute */
.card { animation-delay: calc(sibling-index() * 60ms); }
```

**Firefox implements none of this** — it has blocked Baseline for scroll-driven animations since 2025-09.
So the authoring order is not optional:

1. Write the **finished** state as the element's normal CSS. That is what Firefox, and any reduced-motion
   user, will see. A page that is blank without the timeline is broken, not progressive.
2. Put the timeline inside `@supports (animation-timeline: scroll())` (and `@supports (animation-trigger: --t)`
   for the triggered form), so unsupported engines never see a `both`-filled keyframe holding the *from* state.
3. Keep `prefers-reduced-motion` as a separate gate — support and consent are different questions.

**When this beats rung 4**: single-element reveals, parallax bands, progress indicators, list staggers.
Safari 26.4 runs scroll-driven animations on the compositor, so they survive a busy main thread in a way
no JS scroll loop can. **When it doesn't**: pinning, a seekable labelled timeline, orchestration across
elements that aren't siblings, or any build that owes Firefox the same motion — that is still GSAP.

Related native pieces worth knowing, same support caveat: `scroll-target-group: auto` + `:target-current`
gives scroll-spy nav highlighting with no observer, and scroll-state container queries (`scrolled`) give
the hide-on-scroll header. `linear()` lets a CSS easing carry a real spring/bounce curve instead of a
cubic approximation, and unlike everything else in this recipe it is broadly supported.

---

## 17. Corner-Pin Warp (四角形变 — 把矩形元素贴进任意四边形)

**What**: Map any DOM element onto an arbitrary convex quadrilateral with one `matrix3d`. A projective
(homographic) transform, so it keeps straight edges and perspective foreshortening — no canvas, no WebGL,
no library, and the element stays real DOM (selectable text, working links, `<video>`).
**Use for**: cards that bend as they hang or drag, a hero image keystoned into a surface, a page-fold or
flag effect, screenshots pinned into a 3D-looking mock, anything where `rotate + skew` is not enough
because the two opposite edges need *different* directions.

`skew()` cannot do this. Skew shears both edges by the same amount; a corner pin moves all four corners
independently, which is what makes a card read as *bent* rather than *slanted*.

```js
/* src rect (w×h) → dst quad, given as TL,TR,BL,BR in page px */
function adj(m){return[m[4]*m[8]-m[5]*m[7],m[2]*m[7]-m[1]*m[8],m[1]*m[5]-m[2]*m[4],
                       m[5]*m[6]-m[3]*m[8],m[0]*m[8]-m[2]*m[6],m[2]*m[3]-m[0]*m[5],
                       m[3]*m[7]-m[4]*m[6],m[1]*m[6]-m[0]*m[7],m[0]*m[4]-m[1]*m[3]];}
function mul(a,b){const c=[];for(let i=0;i<3;i++)for(let j=0;j<3;j++){let s=0;
  for(let k=0;k<3;k++)s+=a[3*i+k]*b[3*k+j];c[3*i+j]=s;}return c;}
function mv(m,v){return[m[0]*v[0]+m[1]*v[1]+m[2]*v[2],m[3]*v[0]+m[4]*v[1]+m[5]*v[2],m[6]*v[0]+m[7]*v[1]+m[8]*v[2]];}
function basis(x1,y1,x2,y2,x3,y3,x4,y4){const m=[x1,x2,x3,y1,y2,y3,1,1,1];
  const v=mv(adj(m),[x4,y4,1]);return mul(m,[v[0],0,0,0,v[1],0,0,0,v[2]]);}
function projection(s,d){const t=mul(basis(...d),adj(basis(...s)));return t.map(x=>x/t[8]);}

function cornerPin(w,h,d){                       // d = [TLx,TLy, TRx,TRy, BLx,BLy, BRx,BRy]
  if(!quadOK(d)) return null;                    // ← never skip this, see failure 1
  const t=projection([0,0, w,0, 0,h, w,h], d);
  return `matrix3d(${[t[0],t[3],0,t[6], t[1],t[4],0,t[7], 0,0,1,0, t[2],t[5],0,t[8]].join(',')})`;
}
```
The element needs `position:absolute; left:0; top:0; transform-origin:0 0` — the matrix carries the
placement, so any additional offset fights it.

**Accuracy, measured**: applying the produced matrix to the four source corners and reading them back
through the browser's own `DOMMatrix` reproduces the requested quad to **2.7e-15 px in pure JS** and
**0.016 px after the CSS round-trip**. The math is exact; the 0.016 px is CSS transform *serialisation*
precision and is the resolution floor of this ruler — an oracle with a tighter threshold than that is
measuring the ruler, not the code (`verification-harness.md` §9).

### The three ways it breaks

**1 · A non-convex or inverted destination quad paints a screen-sized shape.** When the quad self-
intersects (a bowtie), the homography's `w` goes negative for some corners and the element flips through
infinity. There is no error, no console warning — just an enormous block of colour. **Guard every quad:**

```js
function quadOK(d){                                   // TL,TR,BR,BL winding
  const P=[[d[0],d[1]],[d[2],d[3]],[d[6],d[7]],[d[4],d[5]]];
  let sign=0;
  for(let i=0;i<4;i++){
    const [ax,ay]=P[i],[bx,by]=P[(i+1)%4],[cx,cy]=P[(i+2)%4];
    const cr=(bx-ax)*(cy-by)-(by-ay)*(cx-bx);
    if(Math.abs(cr)<1e-6) return false;               // collinear → degenerate
    const s=Math.sign(cr);
    if(sign===0) sign=s; else if(s!==sign) return false;   // winding flipped → bowtie
  }
  return true;
}
```
Fall back to a plain `translate()` when it returns false. **But a guard that fires is still a visible
glitch** — the element snaps from warped to flat. The guard is the seatbelt; failure 2 is the fix.

**2 · Clamp the edge tilt, and clamp it against the right thing.** For a card of width `w` and span `h`,
tilting an edge by `t` slides its corners along the card's own axis by `(w/2)·sin t`. The two side edges
cross once `(w/2)(sin t₀ + sin t₁) > h`, so:

> **`t_max = asin(h / w)`** — and there is no limit at all when `w ≤ h`.

```js
const TILT_MAX = CARD_W > CARD_H ? Math.asin(Math.min(1, CARD_H/CARD_W)) * 0.85 : Math.PI/2;
function clampTilt(n, ax, ay, bx, by){          // n = raw normal; a→b = the card's own axis
  let dx=bx-ax, dy=by-ay; const L=Math.hypot(dx,dy)||1e-6; dx/=L; dy/=L;
  const pa=Math.atan2(-dx, dy);                 // angle of the axis' perpendicular
  let d=Math.atan2(n[1],n[0])-pa;
  while(d>Math.PI)d-=2*Math.PI; while(d<-Math.PI)d+=2*Math.PI;
  const c=Math.max(-TILT_MAX, Math.min(TILT_MAX, d));
  return [Math.cos(pa+c), Math.sin(pa+c)];
}
```

Clamp each edge normal to within `t_max` of the perpendicular of **the card's own axis**. Clamping the two
normals against *each other* is the wrong constraint and does nothing: both can be within a few degrees of
one another and still be rotated flat into the axis. Documented: clamping the mutual angle at 57° left the
degenerate count unchanged at 53 per 600 frames; clamping tilt-vs-axis at `asin(84/190)·0.85 = 22.3°`
took it to **0 at every input speed, up to 200 px/frame**.

**3 · Filtering, not geometry, is what makes it look cheap.** A strongly keystoned element resamples with
the browser's default filter. Keep the on-screen magnification near 1× (`image-asset-pipeline.md` §6), and
add `image-rendering: auto; backface-visibility: hidden` plus a `will-change: transform` on the animated
element so it gets its own layer instead of re-rasterising every frame.

**Curved edges need strips.** A homography can only produce a quadrilateral — straight edges. To bend an
edge into a curve, split the element into N slices along the bend axis and corner-pin each slice
(piecewise-linear, ~8 slices is enough for a card-sized bend); seams appear if slices don't share exact
corner coordinates, so compute the shared edge once and pass it to both. Past ~16 slices or if the surface
must also be lit, stop and go to a WebGL plane with vertex displacement (`shaders-spec.md`).

---

## 18. Verlet Card Chain (卡片链 — 一串图片挂在光标下，跟着摆动并弯折)

**What**: N image cards strung on a Verlet chain that hangs from the pointer. Each card is corner-pinned
between two chain nodes and takes its two edge normals from the chain's local tangents — so when the chain
curves, the card physically **bends**. Recipe #15 supplies the chain, #17 supplies the bend.
**Use for**: a work index where hovering a row trails its images, a drag-to-browse gallery, a cursor that
carries content rather than being a dot (`design-slop.md` B7).

The bend is the whole point. A chain of cards that merely *rotate* to follow the tangent reads as a
rigid-body toy; the deformation is what makes them read as physical objects with give.

```js
const N=7, REST=118, CARD_W=190, CARD_H=84;   // CARD_H < REST → a gap, and the rope shows
const GRAV=0.55, DAMP=0.965, ITER=16;         // low gravity + high damping = hangs, doesn't whip

function step(){
  for(const p of pts){ const vx=(p.x-p.px)*DAMP, vy=(p.y-p.py)*DAMP;
    p.px=p.x; p.py=p.y; p.x+=vx; p.y+=vy+GRAV; }
  for(let k=0;k<ITER;k++){
    pts[0].x=head.x; pts[0].y=head.y;                    // pin to the pointer
    for(let i=0;i<pts.length-1;i++){
      const a=pts[i], b=pts[i+1];
      let dx=b.x-a.x, dy=b.y-a.y;
      const d=Math.hypot(dx,dy)||1e-6;
      const share=(i===0)?1.0:0.5;         // ← a pinned end gives its whole correction to b
      const diff=(d-REST)/d*share; dx*=diff; dy*=diff;
      if(i>0){ a.x+=dx*0.5/share; a.y+=dy*0.5/share; }
      b.x-=dx; b.y-=dy;
    }
  }
}
// central-difference tangent → the normal that gives each card edge its direction
function normalAt(i){
  const a=pts[Math.max(0,i-1)], b=pts[Math.min(pts.length-1,i+1)];
  let tx=b.x-a.x, ty=b.y-a.y; const L=Math.hypot(tx,ty)||1e-6;
  return [ty/L, -tx/L];
}
function draw(){
  const hw=CARD_W/2, t=(1-CARD_H/REST)/2;                // inset so cards don't touch
  for(let i=0;i<N;i++){
    const p0=pts[i], p1=pts[i+1];
    const ax=p0.x+(p1.x-p0.x)*t, ay=p0.y+(p1.y-p0.y)*t;
    const bx=p1.x-(p1.x-p0.x)*t, by=p1.y-(p1.y-p0.y)*t;
    const [nx0,ny0]=clampTilt(normalAt(i),   ax,ay,bx,by);   // #17 failure 2
    const [nx1,ny1]=clampTilt(normalAt(i+1), ax,ay,bx,by);
    const m = cornerPin(CARD_W, CARD_H,
      [ax-nx0*hw, ay-ny0*hw,  ax+nx0*hw, ay+ny0*hw,
       bx-nx1*hw, by-ny1*hw,  bx+nx1*hw, by+ny1*hw]);
    if(m) cards[i].style.transform = m;
  }
}
```

**The bug that costs an afternoon**: `share=(i===0)?1.0:0.5`. With a pinned node 0, giving the top segment
only half its correction leaves it permanently under-solved, and the chain can settle **folded above its
own anchor** — node 1 above node 0. Distance constraints alone do not forbid folding. The visible symptom
is not a fold; it is the *first card exploding*, because a folded top segment flips that card's two edge
normals into opposite directions and the quad becomes a bowtie (#17 failure 1). Measured before the fix:
node 1 at y=82 with the anchor pinned at y=200, and card 0's quad at signed area **0** with `w_min = −1`.

**Numeric oracle** (`verification-harness.md`): expose `__chain = { setHead, settle(n), nodes(), segError(), degenerate() }`
and sweep the pointer on a continuous figure-8 rather than teleporting it — a teleport is not a pointer
event and produces failures no user can trigger. Assert across 600 frames at 25 / 60 / 200 px per frame:

| | must be |
|---|---|
| `degenerate()` — cards that hit the corner-pin fallback | **0** at every speed |
| `segError()` — worst deviation from `REST` | < ~2 px during motion; **stable**, not growing |
| `segError()` settled | < 0.2 px |
| bend at rest | 0.00° |

Settled `segError` never reaches 0: it is the steady-state gravity stretch at a finite iteration count.
Measured 0.125 px on a 118 px segment (0.1 %), **constant across 2 000 further steps** — constant is the
proof it converged. A number that keeps growing is a divergent solver; a small constant is physics.

---

## 19. Slack String Between Anchor and Datum (软绳硬端点 —— 中段乱写，端点不许说谎)

A curve whose two ends are **exact** and whose middle is **soft**. One end is a fixed anchor, the
other is a datum written by data (a clock angle, a value on a gauge, an active nav item). The body
between them carries more length than the straight path, so it must sag — and the sag is the whole
expression. Proven in `cases/string-clock`.

**Why it is not "a verlet chain with the ends pinned".** Two things are load-bearing and both are
counter-intuitive:

**1 · The datum end is spring-held, and the spring must be stiff.**
Gravity on a spring-held point rests at an offset of `g / k`. Make the tip spring soft because a
string "should feel floppy" and the readout is simply wrong: at `g = 2200`, `k = 60` puts the tip
**37 units** below its true position — 6.8° at a 308-unit radius. At `k = 1600` the offset is
1.4 units, 0.26°, invisible. **Soft body, stiff endpoint.** The reason the illusion works at all is
that people read the *direction of a stroke*, not the position of its endpoint, so you may lie
extravagantly in the middle and not at all at the ends.

**2 · The body is elastic, not inextensible.** A rigid solver (8 iterations at stiffness 0.9,
effective 0.999) reads as a metal chain. A real string stretches when you yank it — measured on the
reference clip, a dragged hand's arc ran 332 → 684 px and came back. So run the solver *weak*
(3 iterations at 0.5) and forbid spaghetti with a hard per-segment cap instead.

```js
// per fixed step, dt = 1/120
tipV += (K_TIP*(target - tip) - C_TIP*tipV) * dt;   tip += tipV*dt;   // stiff
for (let i=1;i<last;i++){                                            // soft body
  const vx=(x[i]-px[i])*DAMP, vy=(y[i]-py[i])*DAMP;
  px[i]=x[i]; py[i]=y[i];
  x[i]+=vx + (wind + bx*BIAS)*dt*dt;
  y[i]+=vy + (g    + by*BIAS)*dt*dt;
}
x[0]=anchor.x; y[0]=anchor.y; x[last]=tip.x; y[last]=tip.y;
constrain();                       // 3 x 0.5 projection, then the cap below
```

**Four failure modes, all silent:**

| Symptom | Cause | Fix |
|---|---|---|
| the curve jitters or spikes when the datum is directly "above" the anchor | gravity is parallel to the chord; a slack string has no preferred buckling side | a motivated lateral bias — `BIAS` along −tangent, so the string *trails* the sweep |
| stretch grows with input speed, up to 8× rest arc, with the cap enabled | a one-directional cap sweep moves the violation inward one segment per frame | sweep the cap **forwards then backwards, twice** |
| nodes fly off the canvas on a fast fling | the grab was clamped to the string's reach but not to the artefact's box | clamp to the **box first, then the reach**; the intersection is what you want, and clamping toward the anchor after a box-clamp stays inside both |
| the "rigid" variant of the same control still sags | slack 0 is not rigidity — a weak solver cannot hold a taut line | give the rigid mode its own settings (10 iterations at stiffness 1.0) and zero the loads |

**Give the driven ends ¼ weight** in the distance projection: string tension then barely moves them
(so the datum stays true) while a hard drag still transmits down the chain.

**Boundary with zero restitution** — clamp position *and* move the previous position with it, or you
inject energy:

```js
if (d > WALL){ const nx=..., ny=...;
  px[i]+=nx-x[i]; py[i]=py[i]+ny-y[i]; x[i]=nx; y[i]=ny; }
```

**Numeric oracle** (`verify_case.py --strings`) — the two assertions must **pull against each other**,
otherwise the test is decoration:

| | must be |
|---|---|
| datum end vs. its true value, after settle | ≤ 1.5° (measured 0.00°) |
| least sag, arc ÷ chord, same sweep | ≥ 1.12 (measured 1.331) |
| rigid mode sag | ≤ 1.03 (measured 1.000) |
| worst stretch under a **real pointer** fling at 12/60/240 px per step | ≤ 3.2× rest arc (measured 2.47×) |
| arc after release | within 4 % of rest (measured 0.3 %) |

Over-damp and the sag assertion dies; loosen the endpoint and the accuracy assertion dies. A single
"looks about right" score would pass both broken versions.

**Reduced motion**: compute the rest shape analytically (`restShape()` — same endpoints, same bow
depth, one quadratic) and redraw on the datum's own cadence. Never a straight line, never blank.

## 20. Cumulative Emergence (堆积式涌现 —— 数量本身就是构图，而且一动不动)

一次一件地把内容发到画面上，直到铺满。不是 stagger 入场（那是把已知的一批**揭示**出来），
是**集合本身在长大**，而"长到多满"就是这一页要说的话。用在：实时活动、社会证明、归档、
任何"东西还在不断进来"的主张。

**先说反直觉的那条：这个模式里最好不要有入场动画。**
参考片逐帧实测（60fps，8.4s）：

```
504 帧 → 444 帧完全静止（88%）
一张卡片的区域：到达前 mean|Δ|=0.000 → 到达帧 9.28 → 之后 0.01（压缩噪声），直到片尾
到达帧号 90/100/120/140/180/201/211/… → 间隔全是 10 帧的整数倍 = 167 / 333 / 500ms
底部黑带：逐帧互相关位移 = 0px（它根本不滚）
```

一秒钟要落 3–6 件东西的时候，给每件加 260ms 缓动只会糊成一片粥。这个模式的动效预算
**全部花在"什么时候出现"上**，不是花在曲线上。

### 1 · 到达时钟：网格 + 跳格

```js
const TICK = 167;                     // ms，量出来的
function loop(now){
  if (dealing && visible && now >= nextAt){
    deal();                                        // 一帧画完，没有 transition
    const skip = rng() < .34 ? (rng() < .3 ? 3 : 2) : 1;
    nextAt = now + TICK * skip;                    // 跳格才有节奏，等距是节拍器
  }
  requestAnimationFrame(loop);
}
```

判据：所有间隔都落在 tick 网格上（偏离 ≤ 1/8），**且倍数不能只有 [1]**——只有 1 就是节拍器。

### 2 · 放置：随机就够，别自作聪明

参考的 22 次到达，最近邻距离 **CV = 0.507** —— 就是 `Math.random()`，卡片重叠得很凶。
我第一版上了 best-candidate 蓝噪声（CV 0.09–0.19）并且把它写成判据，结果是**参考自己会挂**。

随机重叠之所以成立，靠的是另一条契约：

> **z 序 = 到达顺序。刚出现的那张永远不会被压在别人下面。**

```js
el.style.setProperty('--z', String(++dealt));   // 规则里 z-index: var(--z,1)
```

判据也断言这个（新卡的采样点不许被**更老的卡**盖住），而不是断言散布好看。
真要蓝噪声（内容必须每张可读时），best-candidate k=12–16，但要知道那是**你的**设计决定。

### 3 · 上限：DOM 封顶，计数不封顶

```js
const CAP = 46;
function deal(){ /* … */ if (live.length > CAP) retire(live.shift()); }
```

"已发生"和"在场"必须分开：页面上的数字读 `dealt`（一直涨），DOM 里活着的是 `live.length`（封顶）。
两者相等就说明没有回收。实测 `102 dealt / 46 live / 46 nodes`。节点进池复用。

**没有退休动画的额外好处**：一次性涌入不会让 DOM 短时翻倍。若坚持要淡出，必须限制同时淡出的数量，
否则"上限"是句空话（同步灌 46 张 → DOM 里 92 个节点，真实滴速下肉眼永远看不到）。

### 4 · 前景怎么在堆里活下来

| 前景是什么 | 解法 | 不能用的解法 |
|---|---|---|
| 压在堆**上面**的面板 | 高 z-order + **不透明底**，让堆从它底下穿过去 | 把它的矩形从放置区挖掉 —— 判据全绿，画面上是个洞 |
| **刷在底板上**的大字 | 让它**比压在它上面的东西宽**，从两侧穿出来 | 做得比面板窄 —— 那是一段永远看不见的展示字 |

挖洞这种坏实现能通过任何"前景可读"的单条断言，所以判据要加反向的一条：
**堆里必须真的有 N 件压在前景底下**（实测 37）。

### 失败模式

1. **给每件加入场缓动** —— 3–6 件/秒的时候是糊的。先量参考的静止比例再决定。
2. **行内 `z-index` 杀掉 `:hover` 规则** —— `el.style.zIndex` 压过样式表。用 `--z` 自定义属性。
3. **判据编码自己的口味** —— "不许结块"的 CV 带把参考本身判挂。阈值要么来自实测，要么来自能说清的设计要求。
4. **一条断言混进两件事** —— "新卡不许被埋"若把合法压在上面的面板也算进去，必然误报。
5. **`overflow:hidden` 的容器让越界元素从 `scrollWidth` 里消失** —— 横向溢出去查外面的导航/页脚。
6. **字号地板看不见你的大字** —— 探针跳过"有元素子节点"的元素，`<b>a<br>b</b>` 里的 `<br>` 就够了。
