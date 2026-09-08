# Choreography Arc

Use this reference when designing the full motion narrative of a page — not individual component animations, but how the entire experience moves from entry to exit.

## What Is a Choreography Arc?

A choreography arc defines the **pacing, rhythm, and energy curve** of a page's motion system across time and scroll. Think of it like a film score: individual instruments matter, but the arc determines whether the experience feels tense, euphoric, calm, or cinematic.

---

## Arc Types

### 1. `cold-open` — Slow build, then release
**Pattern**: Quiet entry → increasing complexity → peak moment → resolution  
**Use when**: The product or content speaks for itself; you want the user to discover, not be assaulted.  
**Example shape**: `0%→30%` minimal opacity reveals · `30%→70%` bento grids and data cascade in · `70%→100%` CTA isolated in generous space  
**Reference entries**: Rauno (#4), Cosmos (#5), Studio Freight (#7)  
**Motion tokens to use**:
- Entry: `duration: 1.2s, ease: cubic-bezier(0.16, 1, 0.3, 1), stagger: 0.1s`
- Midpoint: `duration: 0.8s, stagger: 0.06s`
- Peak/CTA: `duration: 0.6s, no stagger — single decisive snap`

---

### 2. `broadside` — Immediate impact, held tension
**Pattern**: Hero asserts itself instantly → sustained visual pressure → late breath  
**Use when**: Brand identity is the message. Award sites, bold studios, product launches.  
**Example shape**: `0%→20%` massive type slams in · `20%→80%` scroll holds viewer in tension with parallax/sticky · `80%→100%` sudden color or layout inversion  
**Reference entries**: Hello Monday (#12), Studio Freight (#7), Sintra (#3)  
**Motion tokens**:
- Entry: `duration: 0.4s, ease: cubic-bezier(0.65, 0, 0.45, 1), stagger: 0`
- Scroll: GSAP ScrollTrigger pinned section, `scrub: 1`
- Transition: instant section swap, color inversion via `mix-blend-mode`

---

### 3. `editorial` — Measured, line-by-line tempo
**Pattern**: Each content block enters like a printed page being revealed · no urgency · reading pace controls animation pace  
**Use when**: Content is the value. Blogs, portfolios, interview sites, long-form.  
**Example shape**: Every scroll viewport triggers a single reveal block · consistent `0.6s` per line · no decorative extras  
**Reference entries**: Made by Folk (#11), Paul Stamatiou (#28)  
**Motion tokens**:
- Line reveal: `clip-path: inset(0 0 100% 0) → inset(0 0 0 0), duration: 0.7s, ease: cubic-bezier(0.77, 0, 0.18, 1)`
- Stagger per line: `0.08s`
- Image: `scale: 1.05 → 1, duration: 1s` inside `overflow: hidden` container

---

### 4. `ambient` — Continuous low-level motion, no scroll trigger
**Pattern**: Background or environment animates continuously · foreground is static · depth is created by the contrast  
**Use when**: The atmosphere IS the product (creative tools, AI platforms, inspiration sites).  
**Example shape**: Particle field or shader runs at all times · UI elements are anchored and unmoving · hover triggers ripple in bg layer  
**Reference entries**: Pro Liquid Shader (#1), Keita Yamada (#8), Joseph Santamaria (#29)  
**Motion tokens**:
- Background loop: `duration: continuous, ease: linear, GPU: yes`
- Foreground reveal: single fade-in on load, `duration: 0.8s`
- Hover bg response: `duration: 0.2–0.3s`
- **Warning**: keep GPU budget under 60fps check; degrade to CSS gradient on mobile

---

### 5. `staccato` — Short, rhythmic, data-dense
**Pattern**: Many small elements snap in with tight stagger · feels systematic, not decorative  
**Use when**: Dashboard-style pages, feature grids, developer tools.  
**Example shape**: Grid of cards enters in `0.05s` stagger waves · no long holds · user interaction triggers micro-confirm animations  
**Reference entries**: Smithery (#2), Layers (#6)  
**Motion tokens**:
- Grid cell entry: `duration: 0.3s, stagger: 0.04s, ease: ease-out`
- Hover: `duration: 0.15s, translateY: -4px, box-shadow: grow`
- Data update: `duration: 0.2s, opacity flicker, ease: linear`

---

## Transition Rhythm Rules

| From arc type | Best slide/page transition |
|---|---|
| `cold-open` | Cross-fade with blur: `opacity 0→1, filter blur(8px)→0, 0.9s` |
| `broadside` | Wipe or instant cut, `0.3s max` |
| `editorial` | Scroll-driven reveal, no discrete transition |
| `ambient` | Background persists; foreground cross-fades |
| `staccato` | Stagger-out current + stagger-in next, `0.4s total` |

---

## Opening Beat Checklist

Before writing any animation code, define:

- [ ] Which arc type does this page follow?
- [ ] What is the first thing the user sees, and what does it communicate in 0–1s?
- [ ] Where is the tension peak? (Usually 40–70% scroll depth)
- [ ] Where is the release/CTA? (Usually the last 20% of scroll)
- [ ] What happens on mobile where scroll is non-linear?

---

## Common Arc Failures

| Failure | Cause | Fix |
|---|---|---|
| Page feels busy and unfocused | Multiple arc types mixed without intent | Pick one dominant arc; treat others as sub-patterns |
| Motion stops mattering after hero | Hero gets all the animation budget | Distribute the arc across sections |
| CTA buried in animation | Decorative effects surround the CTA | Isolate CTA with a motion pause — stillness = emphasis |
| Mobile feels broken | Arc designed only for scroll | Define a viewport-trigger fallback for every scroll pinned section |
| Late sections feel flat | Motion front-loaded in hero | Reserve one payoff moment for 60–80% scroll depth |
