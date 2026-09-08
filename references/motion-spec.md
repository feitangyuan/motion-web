# Motion Spec

Use this file whenever a task needs motion extraction, motion design, or implementation handoff.

## Reference Entry Fields

Every reusable motion entry should include:

- `entry_type`: `motion_site`, `motion_component`, or `motion_lead`
- `source`
- `title`
- `captured`
- `source_kind`: `canonical`, `reference`, or `lead`
- `motion_role`: `hero`, `navigation`, `scroll`, `hover`, `transition`, `3d`, `ambient`, `media`, or `system`
- `trigger`: load, scroll, hover, click, drag, pointer, route, or continuous
- `duration`: exact ms/s, range, or continuous
- `easing`: exact cubic-bezier, spring config, named preset, or not applicable
- `stagger`: delay model and order
- `transform`: opacity, translate, scale, rotate, clip-path, shader uniform, camera, material, or media state
- `library`: CSS, Framer Motion, GSAP, Lenis, Three.js, R3F, Lottie, Rive, video, or unknown
- `media`: DOM, SVG, canvas, WebGL, video, Lottie, Rive, or mixed
- `interaction_state`: hover, focus, active, touch fallback, keyboard fallback
- `reduced_motion`: exact fallback behavior or explicitly unconfirmed
- `performance_budget`: FPS target, asset budget, canvas limits, mobile fallback
- `baseline_ui`: typography, spacing, color, layout, and component notes only when visible
- `reuse_rule`: what to borrow
- `do_not_copy`: what not to clone
- `confidence`: `verified`, `partially_verified`, or `lead_only`

If a value is not verified, mark it. Do not invent exact timing, easing, or library choices from a clip.

## `MOTION_SPEC.md` Template

Use this as the execution-facing artifact.

```md
# MOTION_SPEC.md

## 1. Goal
- Page type:
- Audience:
- Primary action:
- Motion concept:
- Baseline UI role:

## 2. Choreography
- Opening beat:
- Scroll rhythm:
- Interaction rhythm:
- Transition rhythm:
- Closing beat:

## 3. Motion Tokens
- Fast interaction:
- Standard transition:
- Slow reveal:
- Primary easing:
- Secondary easing:
- Stagger:
- Spring:

## 4. Interaction Map
- Hover:
- Focus:
- Active:
- Click/tap:
- Pointer/drag:
- Keyboard:
- Touch fallback:

## 5. Scroll Timeline
- Section:
  - Trigger:
  - Start/end:
  - Animated properties:
  - Failure mode:

## 6. 3D / Canvas / Media
- Policy:
- Allowed:
- Forbidden:
- Camera:
- Shader/material:
- Asset budget:
- Mobile fallback:

## 7. Baseline UI
- Typography:
- Layout:
- Spacing:
- Color:
- Components:
- Responsive:

## 8. Accessibility And Performance
- Reduced-motion fallback:
- Focus rule:
- Contrast rule:
- FPS target:
- Expensive areas:
- Do not ship if:

## 9. Stack
- Preferred:
- CSS-only areas:
- JS animation areas:
- 3D/canvas areas:

## 10. References
- Source:
  - Borrow:
  - Do not copy:
  - Confidence:

## 11. Acceptance Criteria
- [ ] Motion concept is visible without hurting readability
- [ ] Timing/easing/stagger are specified
- [ ] Touch and keyboard behavior are defined
- [ ] Reduced motion preserves content and navigation
- [ ] Mobile does not depend on hover-only motion
- [ ] Build/type-check passes
```

## Quality Bar

- Motion should have a job: reveal structure, create spatial memory, explain state, guide scroll, or make interaction feel authored.
- One strong choreography system beats many unrelated effects.
- If the page becomes confusing when motion is removed, the static baseline is underdesigned.
- If the page only works with desktop hover, it is not ready.
- If canvas/WebGL exists, define the fallback before building.
