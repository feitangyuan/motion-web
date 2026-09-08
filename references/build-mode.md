# Build Mode

Use `build` only when one of these is true:
1. A `MOTION_SPEC.md` or equivalent approved motion contract exists
2. The user approved a concept in chat (freeform build)
3. The task is an incremental addition to existing built work

---

## Build Order

0. **Project + token layer**: page stack rung, three-level tokens, type/space scales, fonts, `@layer` order — `project-setup.md`. Skipping this means editing every component later.
1. **Semantic structure first**: HTML that works without CSS/JS — correct heading hierarchy, alt text, focusable elements. Which sections exist and what they say comes from `page-blueprints.md`.
2. **Baseline UI layer**: typography, spacing, color, layout. Run `data/visual-bank.json` lookup first. Component vocabulary and the state matrix each one owes → `components.md`.
3. **Motion tokens**: import/define duration, easing, spring config from `references/motion-tokens.md`. Do this before writing animation code.
4. **CSS transitions** for small, predictable state changes (hover, focus, toggle).
5. **Section choreography**: scroll triggers, entrance/exit sequences, arc-level timing.
6. **Interaction states**: hover, pointer, drag, active, keyboard.
7. **Light 3D/canvas/media** last — only if specified in the spec. See `references/light-3d.md`.
8. **Finish**: head/OG/favicon, 404, off-happy-path states, dark-mode decision → `production-polish.md`.
9. **Verify** (see checklist below).

---

## CSS Layering Rules

Stack your CSS in this order to prevent specificity wars:

```css
/* 1. Resets and custom properties */
:root { --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1); ... }

/* 2. Base typography and body */
body { font-family: ...; background: ...; }

/* 3. Layout (grid, flex containers) */
.grid { display: grid; grid-template-columns: ...; }

/* 4. Component structure (no motion yet) */
.card { border-radius: 12px; overflow: hidden; }

/* 5. Motion tokens — transitions on stable state, NOT animation state */
.card { transition: transform 0.28s var(--ease-out-expo); }

/* 6. Interaction states */
.card:hover { transform: translateY(-4px); }

/* 7. JS-controlled classes (added/removed by script) */
.card.in-view { opacity: 1; transform: translateY(0); }
.card.exiting { opacity: 0; }

/* 8. Reduced motion overrides — ALWAYS last */
@media (prefers-reduced-motion: reduce) {
  .card { transition: opacity 0.2s linear; }
  .card:hover { transform: none; }
}
```

**Critical**: Never put `transition: transform` on elements whose `transform` is also written by a RAF loop or GSAP ticker. The CSS transition will fight the JS and cause stuttering. Use one or the other per property.

---

## Tech Stack Decision Ladder (climb only when the lower rung fails)

Pick the **lowest** rung that achieves the visual goal. Escalating stack = escalating cost
(bundle, complexity, iteration speed). Each step up must be justified by a concrete capability gap,
not by "3D would look cooler".

| Rung | Stack | Reaches | Stop here if |
|---|---|---|---|
| 1 | CSS transitions/animations | hovers, toggles, reveals, marquees | state-driven, no continuous input |
| 1.5 | **Native CSS scroll timelines** — `animation-timeline: scroll()/view()`, `animation-trigger` | **scrubbed parallax, progress bars, entrance reveals, scroll-spy — with no JS and no library** | **the driver is scroll position or crossing a scroll boundary, and Firefox gets a static fallback** |
| 2 | Vanilla rAF + springs (see handfeel.md) | mouse-following, wheel carousels, jelly wobble, velocity coupling | continuous input drives continuous output |
| 3 | + alpha-masked gradient overlays (2.5D) | "realistic" light/shadow on flat PNG cutouts, mouse-lit heroes | asset is an image and camera never moves |
| 4 | Framer Motion / GSAP | orchestrated timelines, scroll pinning, route transitions, variants | choreography across many elements/pages |
| 5 | **Three.js + image planes (no geometry)** | **a whole scene with real depth, occlusion, camera dolly/pan — built entirely from 2D cutouts** | **the art exists as images and no silhouette needs to rotate** |
| 5.5 | Three.js + 3D Gaussian splats (Spark) | a real *place* with true parallax, occlusion and free camera movement, from a capture rather than a model | the subject physically exists and can be filmed/scanned, and nothing in it needs re-lighting, rigging or editing |
| 6 | Three.js/R3F + real geometry/models | geometry rotation revealing new faces, PBR materials/env lighting | the *silhouette itself* must change with view angle |

**Rung 5 is the one that gets skipped.** "It needs to look 3D" is normally read as "we need models",
which imports an entire asset pipeline. But a `PerspectiveCamera` doesn't care whether the thing at
`(x, y, z)` is a mesh or a textured plane — perspective, occlusion, sorting and projection are computed
either way. **Documented case (2026-08, heritage-ruins scroll scene): ~52 flat images, one moving camera, zero models;
user verdict 「把图片资产 2d 的做出了 3d 感，纵深透视都很真实」.** Full method in
`references/image-plane-3d.md` — it is not "put PNGs in a scene", there are ~8 things that must be right
(measured baselines, hand-sorted transparency, analytic contact shadows, colour-temperature unification)
and the scene reads as collage until they are. **The step before that** — keying the cutouts, scripting
their metadata, and checking each one's on-screen magnification — is `references/image-asset-pipeline.md`;
the runtime cannot be right if an asset was keyed against the wrong background or is being enlarged.

**Rung 1.5 is new and takes work away from rung 4.** `animation-timeline: scroll()` / `view()` is
Chrome 115+ and Safari 26+; `animation-trigger` (fire a normal timed animation when a scroll boundary
is crossed — the native form of an IntersectionObserver reveal) is Chromium-only, Chrome 146+.
**Firefox implements neither**, and has blocked Baseline for scroll-driven animations since 2025-09 —
so treat the whole rung as progressive enhancement: author the static end-state as the default, add the
timeline inside `@supports (animation-timeline: scroll())`, and let Firefox render the finished state.
For a scrubbed parallax band or a stagger of entrance reveals this is now the correct lowest rung, and
it runs on the compositor — Safari 26.4 moved scroll-driven animations off the main thread, which no
JS scroll library can match. Reach for GSAP/ScrollTrigger (rung 4) when you need pinning, a real
timeline you can seek and label, cross-element orchestration, or Firefox parity.

**Rung 5.5 exists because "a real place" is a third answer, not a harder version of rung 6.** Photogrammetry
used to mean a mesh + textures + a bake; 3D Gaussian splatting skips all of it — you get true parallax and
occlusion from a capture. `@sparkjsdev/spark`'s `SplatMesh` extends `THREE.Object3D`, so it drops into an
ordinary scene and renders in the same `render(scene, camera)` pass as your planes and meshes; it targets
WebGL2 (≈98% device reach) and its 2.0 LOD system streams large scenes on mobile. Use it when the subject
*exists* and the job is to walk through it. Do **not** use it when the thing must be re-lit, animated,
edited, or stylised — a splat is a frozen radiance field, and every one of those needs rung 6.

**The renderer is an orthogonal axis, not a higher rung.** `three/webgpu` + TSL is not "more 3D" than
`three` — it is the same scene with a different backend. TSL compiles one node graph to both WGSL and
GLSL, so a WebGL fallback is a renderer swap rather than a second shader codebase, and the post-processing
chain is expressed as node composition instead of a pass list. Choose it when the scene is compute-heavy
(GPGPU particles, fluids, large instanced fields) or when you want one shader source for both backends;
stay on the classic `WebGLRenderer` when the scene is a handful of planes and a camera, where it buys
nothing. Do not put a WebGPU line in a spec without also writing what the fallback renders.

**Rung 5 has two topologies — decide before the first line** (`image-plane-3d.md` §12):
*camera moves* (dolly on the scroll rail; long lens ≈26; you enter a place; every element needs a
resolution budget) vs *world moves* (camera parked, the container translates in y; normal lens ≈50; you
read a page that has depth; scale is constant so the resolution problem disappears). Both are documented
production cases — the heritage-ruins scene (2026) and SBS *The Boat* 2015.

**Judgment calls that recur:**
- Reference shows "3D-looking" lighting on a product/object → ask: does the camera orbit it?
  No orbit → rung 3 (fake lighting) matches the reference at 1/10 the cost. **Documented case
  (2026-07-06): seafood hero — first instinct was an R3F rebuild; PNG + mouse-driven
  masked gradients hit the target.** Only if the object must visibly rotate in depth → rung 6.
- Camera must move through a *space* → rung 5 before rung 6. Ask what actually has to rotate;
  usually the answer is "nothing, the camera just moves", and that's rung 5.
- "手感差" complaints are almost never solved by climbing the ladder — they're solved at rung 2
  (springs/velocity, handfeel.md). Don't reach for a library to fix feel.
- Mixing rungs is normal: rung 2 input physics + rung 3 lighting + rung 4 page transitions.
- Route to `3d-scene-studio` instead of rung 6 when it's a full scene (terrain, buildings,
  physics, generated models) rather than one hero object — but check rung 5 first, since a scene
  made of images costs a fraction of a scene made of models.

---

## Implementation Rules

- **CSS transitions**: for hover, focus, toggle, small state changes. Fast, simple.
- **Framer Motion**: for React component choreography, route/page transitions, complex variants.
- **GSAP**: for scroll timelines, pinned sequences, imperative multi-step choreography, SplitText.
- **Three.js/R3F**: only for specified canvas layers or hero 3D. Not for decorative geometry.
- **Web Animations API**: acceptable for isolated one-shot animations where GSAP would be overkill.
- **CSS Scroll-Driven Animations** (`animation-timeline: scroll()`): use for simple parallax and progress indicators where browser support is acceptable (check caniuse.com — ~2024 baseline).

Keep motion primitives reusable: CSS custom properties, GSAP helper functions, Framer variants objects.

---

## Performance Rules

### Compositor Budget
- Prefer `transform` and `opacity` — they are compositor-only and never trigger layout.
- `clip-path` is acceptable if the animated area is small (not full viewport).
- `filter: blur()` is acceptable if applied to a small element, not the whole page.
- Never animate `width`, `height`, `top`, `left`, `padding`, `margin` in the hot path.

### Canvas / WebGL Budget
- Cap `devicePixelRatio` at 2 on mobile: `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`.
- Dispose of unused geometries, materials, and textures explicitly.
- Use `renderer.setAnimationLoop(null)` to pause rendering when the canvas is off-screen.
- For noise/particle backgrounds: render at lower resolution and CSS-upscale if needed.

### `will-change` Rule
- Add `will-change: transform` only immediately before a heavy animation starts.
- Remove it (set to `auto`) when the animation completes.
- Never apply `will-change` globally or to static elements.

### scroll Event Rule
- Always use `{ passive: true }` on scroll listeners: `addEventListener('scroll', fn, { passive: true })`.
- Never call `event.preventDefault()` inside a passive listener.
- Debounce or throttle any expensive work inside scroll callbacks.

### RAF Loop Discipline
- One RAF loop per page, not one per component.
- RAF loops that run every frame should do ≤ 1ms of work each frame.
- If work exceeds 1ms, move to Web Workers or reduce scope.

---

## Framework-Specific Rules

### Framer Motion (React)
```jsx
// Always define variants as constants outside the component — prevents re-creation on render
const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] } }
};

// Use useReducedMotion for accessibility
const prefersReduced = useReducedMotion();
<motion.div variants={prefersReduced ? {} : cardVariants} initial="hidden" animate="visible" />
```

### GSAP (Vanilla / React)
```js
// Always register plugins at module level, once
gsap.registerPlugin(ScrollTrigger, SplitText);

// Always use context in React for cleanup
const ctx = gsap.context(() => {
  gsap.from('.card', { opacity: 0, y: 40, stagger: 0.07, ease: 'power4.out' });
}, containerRef);
return () => ctx.revert(); // cleanup on unmount

// Responsive: use matchMedia to disable complex scroll effects on mobile
gsap.matchMedia().add('(min-width: 768px)', () => {
  // Desktop-only heavy scroll setup
});
```

---

## Verification Checklist

**Before declaring build complete, convert every unchecked item below into a TodoWrite task and work through them one at a time.** Do not just eyeball this list and move on — mentally reviewing a checklist without tracking it is how items silently get skipped under time pressure. Mark each todo completed only after you've actually verified it (screenshot, inspect, or explicit check), not because it seems like it should work.

- [ ] Project-native build/type-check/test passes (e.g., `npm run build`, `tsc --noEmit`)
- [ ] Desktop: motion concept is visible and readable
- [ ] Mobile (375px): layout is intact, hover-only motion is replaced or hidden
- [ ] `prefers-reduced-motion`: test in DevTools → Rendering → Emulate. Page is functional, content is accessible, no motion that could trigger vestibular issues.
- [ ] Keyboard: focus states are visible, interactive elements are reachable via Tab
- [ ] Canvas/WebGL: nonblank, correctly framed, fallback does not blank the page
- [ ] Hover-only interactions have touch fallback (long-press or tap)
- [ ] `will-change` is not set on static elements (inspect in DevTools Layers)
- [ ] No scroll listener calling `event.preventDefault()` without `{ passive: true }`
- [ ] FPS target (60fps baseline): test with Chrome DevTools Performance panel on a mid-range mobile profile

### Affordance (every interactive element that isn't an obvious button)

Mechanism checks above all pass while the user still can't find the interaction. Run `references/affordance.md`:

- [ ] **Grid sweep**, not a centre click — every target owns a measurable share of its region (§9)
- [ ] Each target carries a **visible mark**; a cursor change alone is not an invitation (§1)
- [ ] The mark's window **spans the whole pin/dwell** it belongs to (§2)
- [ ] Marks are **inside the frame / safe area** — measure `getBoundingClientRect()`, don't eyeball (§9)
- [ ] Shared-element / FLIP handoff measured at the **handoff frame**, not the end state: `|inH − outH| / outH < 3%` (§10)
- [ ] Copy does not explain the interaction (§8)

### Image-plane scenes (rung 5)

The scene renders and still reads as collage. Run `references/image-plane-3d.md` §11 — the ones that
actually decide it:

- [ ] Mean `R−B` printed **per asset batch**; outliers corrected via a light multiplier (§7)
- [ ] Every standing element has a contact shadow (§6)
- [ ] `depthWrite: false` + explicit `renderOrder` on all of them (§5)
- [ ] Atmosphere sampled by **world position**, not element origin (§8)
- [ ] Distance dissolve checked against the scene's real depth range — print the % at your farthest element (§8)

And upstream of all of it (`references/image-asset-pipeline.md`):

- [ ] `coverage` printed per asset — nothing at ~0% or ~100% shipped (§1)
- [ ] `w/h/cx/baseline` written by a script, never hand-edited (§4)
- [ ] Anything hung on an element uses a **measured** anchor, not the placement height constant (§4)
- [ ] Per-element magnification table re-run after any asset / camera / fov change; the hero of each interaction has headroom (§6)
- [ ] Reused textures re-authored for their new serving distance, not just re-gained (§7)

---

## Numeric Oracles Over Screenshots

Screenshots are expensive and settle nothing — two people look at the same frame and disagree.
Before a visual/interaction fix, decide **what number would prove it**, print that number in one headless
run, and keep the script. Full table in `references/affordance.md` §9.

Two hooks worth building into any page with a non-trivial transition:

```js
window.__hold = (t) => { held = t }          // pin the transition at an arbitrary t
window.__probe = () => ({ /* boxes, windows, hit-test result at the current pointer */ })
```

Without `__hold`, a headless check (≈1s per screenshot) only ever catches the end state — and an
end-state-only test gives a hard cut full marks. This is exactly how a 52%-size jump at the handoff
frame survived a passing test suite (affordance.md §10).

**The opposite failure is worse.** A six-metric composite "frame quality" script gave 6/6 to every version
a human later rejected, and was deleted. An oracle is legitimate only when it encodes **one stated
complaint**; the aesthetic verdict stays with a person looking at the thing.

Full machinery — the probe contract, on/off differencing, why teleporting the timeline and diffing two
screenshots both lie, why any `Math.random()` on a render path destroys a diff, sampling rate, and the
ruler's own resolution floor — in `references/verification-harness.md`.

---

## Failure Patterns to Avoid

| Failure | Cause | Fix |
|---|---|---|
| "有拼接感 / 没融进去" on an image-plane scene | One asset batch was lit by a different sun — measurable as an outlier in mean `R−B` over painted pixels | Print mean RGB per batch; correct the outlier with a per-element light multiplier (image-plane-3d.md §7). Not an edge/feather problem |
| Cutouts look placed *on* the scene, not *in* it | No contact shadow — a plane has no volume so a shadow map yields a rectangle | Analytic capsule shadow solved in the ground shader from a registered cylinder per element (image-plane-3d.md §6) |
| Transparent planes flicker / wrong things in front | Alpha-blended planes can't depth-sort | `depthWrite: false` + explicit `renderOrder` on every element, with gaps (image-plane-3d.md §5) |
| Scene reads as "big thing near, tiny things far" | Wide fov spreads depth apart so silhouettes never touch | Long lens (fov ≈26) + compose so near silhouettes cut into far ones (image-plane-3d.md §3–4) |
| "动效没生效" on a shared-element transition | Two places each hold their own copy of a size/geometry constant; one was updated, the other wasn't | One side reads the other. A comment claiming the two numbers agree is not a mechanism (affordance.md §10) |
| Asset keeps its whole background / reads as a translucent rectangle | Keyed against a hardcoded white paper, but that plate came from a batch on warm paper | Estimate the background per image from its own border median and key on distance; gate on printed `coverage` (image-asset-pipeline.md §1) |
| Cutout reads as "pasted on" despite clean alpha | The draw rect is mostly empty margin — the eye reads the frame | Crop to the alpha bbox + small margin; exempt band elements vertically (image-asset-pipeline.md §2) |
| Line art paints a white wash over half the frame | Canvas 2D `multiply` degrades to plain drawing over a transparent destination | Ship line art as alpha=ink / RGB=one flat ink colour (image-asset-pipeline.md §3) |
| Something attached to an element floats above/below it | Position taken from the `realH` typed at placement, which assumes the paint reaches the top of the plate | Measure the anchor in the texture and ship it like `baseline` (image-asset-pipeline.md §4) |
| A/B comparison shows noise, or a number swings between identical runs | An ambient clock ran on, or a `Math.random()` sample offset shifted every later layer | Pin every clock in both renders; replace random offsets with a per-event deterministic phaser (verification-harness.md §3) |
| Two screenshots subtracted show every silhouette in the scene rimmed | The camera moved half a pixel; the diff is measuring the camera, not the change | Leave the screen — expose state exits and measure those (verification-harness.md §4–5) |
| A stretch of scroll where "nothing happens", but every layer looks fine alone | Several layers' flat sections coincide on that beat | Lay all tracks against one scroll axis and move two of them; check for a layer whose timestamp is simply stale (timeline-orchestration.md §1, §5) |
| Adding easing made a transition *harder* | Easing at two levels multiplies — middle squared, ends flattened | Ease in exactly one layer; keep the driving timeline linear (timeline-orchestration.md §2) |
| A crossfade authored as a soft dissolve reads as one hard cut | The threshold map has a narrow, bell-shaped histogram, and the mapping saturates most of its range | Histogram-equalize the threshold map; use the full range `T = amt*(1+2W) − W` (timeline-orchestration.md §10) |
| An empty frame / rod / caption still on screen after its content is gone | Its exit time was back-derived from the next section's start | Exit containers on their content's schedule (timeline-orchestration.md §6) |
| Interaction sound is heard as ambient noise | It is fed a persistent state value, so it keeps sounding after the hand stops | Feed a per-frame delta with fast decay; assert ≥15 dB drop 0.25 s after release (scene-audio.md §5) |
| A layer's gain change has no measurable effect | The number was copied from a layer with a different filter Q | Read the filter chain before choosing a gain — a narrower band arrives ~7 dB lower (scene-audio.md §6) |
| SVG draw-on stops halfway and stays | `vector-effect: non-scaling-stroke` moved the dash pattern into screen space, so `stroke-dasharray` no longer equals the path perimeter | Drop `vector-effect`; keep the stroke in user space (pattern-recipes #14) |
| Overlay/annotation drifts off its target | Position hardcoded in %, target lives in a moving canvas/3D scene | Project the target's painted bbox every frame (affordance.md §6, light-3d.md §5) |
| Click on an element that also drags fires mid-gesture | Opening on `pointerdown` | Down-records / up-decides with a 6px threshold (affordance.md §7) |
| A whole instanced batch vanishes, console clean | An injected GLSL value was written `6` where the language needs `6.0`; the program failed to link and the material fell back | Route every injected number through an int→float formatter (shaders-spec.md §6.1) |
| A custom `ShaderMaterial` renders darker than everything beside it | Built-in materials include `tonemapping_fragment` + `colorspace_fragment`; a hand-written shader doesn't | Re-add both includes; with `EffectComposer`, tone-map only in the final `OutputPass` (shaders-spec.md §6.2) |
| A depth-driven effect reads zero depth everywhere (water goes flat white) | `DepthTexture` was given a `LINEAR` filter — the framebuffer is incomplete and the sampler returns 0 | `NEAREST` only on WebGL2 depth textures (shaders-spec.md §6.3) |
| A skinned/animated mesh pops out near the frame edge | Three.js culls on the *bind-pose* bounding box, which the animation leaves | `frustumCulled = false` on the skinned mesh (the bone version of the same trap flat planes have) |
| Jumping to a section gives a different result each time | A scrubbed tween and a time-based tween own the same property — whoever rendered last wins | One driver per property: make them all scrubbed and keep their ranges non-overlapping |
| A follower oscillates ±small amounts every frame, moving *and* parked | A correction is applied after the filter, so the filter pulls back toward the uncorrected target | Filter the correction separately, bake it into the target, then run one filter (handfeel.md §7.3) |
| "跟手但总差一点" on anything chasing a moving target | Steady-state lag of a first-order filter is `speed / k` — arithmetic, not tuning | Add a lead term `target + targetVel / k` (handfeel.md §7.2) |
| Something drifts while a modal / pause panel is open | The loop stopped *rendering* but the integrator kept running — gravity, momentum and input state all accumulated | Hard-reset the physics quantities every frame while paused, don't just skip the draw |
| Pale materials turn blue in shadow after adding an environment map | A sky PMREM is strongly blue and tints everything it indirectly lights | Drop `envMapIntensity` to 0.25–0.45 on pale/tinted materials (light-3d.md) |
| Stuttering on scroll | CSS transition fighting JS RAF loop | Remove CSS transition from JS-animated property |
| High CPU on mobile | Per-frame noise canvas redraw | Pre-render noise to offscreen canvas once; use as CSS background pattern |
| Canvas blank on mobile | DPR > 2 causing memory pressure | Cap DPR at `Math.min(devicePixelRatio, 2)` |
| Hover motion inaccessible | Motion only on `:hover` | Duplicate interaction on `touchstart` or `click` for touch devices |
| Scroll trigger fires incorrectly | Images loading after ScrollTrigger init | Add `imagesLoaded` check or call `ScrollTrigger.refresh()` after load |
| Memory leak in React | GSAP animation not reverted on unmount | Use `gsap.context()` with `.revert()` in useEffect cleanup |
| Page blank in reduced-motion | Keyframe animation removed by media query but fallback not set | Add opacity fallback in reduced-motion block |
