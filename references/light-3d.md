# Light 3D

Use light 3D when a webpage needs spatial interaction, product staging, shader atmosphere, or camera choreography.

---

## 1. Work Division (工种分工)

| Tasks | `motion-web` Role | `3d-scene-studio` Role |
|---|---|---|
| **Asset Creation** | - Raw load verification only | **3D Modeling, Blender pipeline, material baking, texture export** |
| **Scene Layout** | - R3F Canvas placement, DOM overlay | **Camera positioning, lighting rig setup, environment mapping** |
| **Animation** | **Scroll-tied camera movements (GSAP), click/hover spring reactions** | **Character skeletal bones, physics simulations, particle morphs** |
| **Optimization** | - DPR cap, visibility pause, scroll-throttle | **Mesh simplification, polycount reduction, map compression** |

---

## 2. Cross-Skill Handoff Contract (资产交付契约)

When `motion-web` needs a 3D asset, it must invoke `3d-scene-studio` to generate and compress it. Do not attempt to build 3D assets inside `motion-web`.

**First check whether you need a model at all.** If the art already exists as images and nothing in the scene
has to *rotate*, the entire scene — depth, occlusion, camera movement, contact shadows — can be built from flat
planes with no geometry and no export pipeline. See `image-plane-3d.md`. This handoff contract is for the case
where a silhouette must genuinely change with view angle.

### Model Export Requirements (3D 模型交付指标)
- **Format**: Strictly `.glb` (binary GLTF) with **Draco Compression** enabled.
- **Polycount**: Keep the entire web scene under **60,000 polygons (triangles)**.
- **Materials**: Prefer unlit materials with **Baked Lighting & Shadows (烘焙光影贴图)** inside Blender. Do not rely on WebGL real-time shadow casting (which kills mobile performance).
- **Textures**: All textures must be compressed (WebP/Basis Universal) and capped at `1024x1024` max.
- **Origin Point**: Center the model's pivot at `[0, 0, 0]` before exporting.

### The Integration Workflow
1. `3d-scene-studio` outputs the optimized `.glb` file to the web public folder (e.g., `public/assets/model.glb`).
2. `motion-web` loads it in R3F using `@react-three/drei`'s `useGLTF` hook:
```jsx
import { useGLTF } from '@react-three/drei';
// Loaded asynchronously with Suspense fallback
const { scene } = useGLTF('/assets/model.glb');
```

---

## 3. Implementation Rules

- DOM content must remain readable if the canvas fails.
- Keep canvas behind or clearly separated from critical text.
- Define mobile fallback before coding (render static image if WebGL fails).
- Prefer simple geometry, shaders, or one lightweight model.
- Cap DPR on mobile at `Math.min(window.devicePixelRatio, 2.0)`.
- Avoid scroll hijacking unless the spec explicitly requires it.
- Verify the canvas is nonblank, framed, and not covering HTML interactive controls (use `pointer-events: none` on canvas overlays).

---

## 4. Environment Lighting Tints Everything It Touches

A sky PMREM is not neutral — it is strongly blue, and it lights every material indirectly. Pale and
tinted surfaces pick that up in shadow and read as if they were painted a different colour than they are.

- Drop `envMapIntensity` to **0.25–0.45** on pale/tinted materials. Leave metals alone; they *should* take
  the sky.
- Diagnose it the same way as a plane-scene seam: measure mean `R−B` over the painted pixels of the
  suspect material and compare it against a reference material lit the same way (`image-plane-3d.md` §7).
  「阴影里发蓝」 is a measurable outlier, not a matter of taste.
- One environment pass over everything, always — mixing an env-lit object into an unlit scene is the
  fastest way to make one element look pasted in.

---

## 5. DOM Over a Moving Scene (两套坐标系，撞上只是迟早)

HTML positioned in `%` and objects positioned in world space are two coordinate systems. They collide the
moment the camera moves or the aspect ratio changes — and "it doesn't overlap in this frame" only buys time
until the next one. Documented case (2026-08): a caption tuned three times to dodge scenery was finally
wiped out by objects added later; every round's comment said "checked at four scroll positions".

**Anything that must track a 3D object** — annotation ring, hotspot, tooltip, outline, label — gets its
screen box **projected every frame** from the object's painted bbox. Never a stored `%`.
See `affordance.md` §6 for the projection helper and why it goes through the four corners.

**Anything that must merely avoid the scenery** — body copy, captions, credits — gets placed by measuring
where the frame is *empty*, not by eye:

```py
# grid the rendered frame 6×8, compute per-cell luminance std. Low std = flat = nothing there.
# Run it at 3–4 representative scroll positions and take cells that are flat in ALL of them.
```

That measurement usually reports something the eye argues with — in the case above, the entire lower half
of the frame was never actually empty at any scroll position, and the only structurally flat region was the
sky above the horizon line. Which is, not coincidentally, where a handscroll's colophon has always gone.

**Safe area is an invariant, not a vibe.** If the page has a mat/letterbox/bleed border, assert that
projected overlays stay inside it: `rect.bottom <= innerHeight - safeAreaPx`. A ring clipped by the border
reads as a rendering bug, and a subject whose feet land at 0.994 of frame height reads as "too close" —
neither is a sizing problem, and reaching for the scale knob fixes neither (affordance.md §9).

---

## 6. Spec Fields

- scene purpose
- camera behavior
- object count
- material/shader behavior
- interaction trigger
- fallback
- performance budget

