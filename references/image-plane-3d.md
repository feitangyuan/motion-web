# Image Planes in a Real Camera — 用图片资产做出真纵深

The route almost nobody takes: **flat PNG cutouts placed as upright planes at real world coordinates,
inside a real `PerspectiveCamera`.** No models, no geometry, no Blender. Perspective, occlusion,
foreshortening and projection are *computed*; only the surface is painted.

> 透视、遮挡、投影都是真算的，只有表面是画的。

This is the missing rung of the stack ladder. It sits far above parallax layers (which fake depth with
translate speeds and break the moment the camera turns) and far below modelling (which costs a pipeline).
**Documented case (2026-08, heritage-ruins scroll scene):** ~52 elements, all 2D art, one perspective camera on a scroll rail.
User verdict: 「把图片资产 2d 的做出了 3d 感，纵深透视都很真实」.

Reach for this when: the art already exists as images (photos, illustration, archival plates, AI stills);
the camera must actually move through the space; the subject is a *scene* rather than one hero object.

---

## §1 Why it works at all

A parallax stack is a lie that only holds from one viewpoint — layers slide at different speeds, and the
instant the camera dollies or rotates the lie is visible. An upright plane at `(x, y, z)` is not a lie:
three.js foreshortens it, sorts it, projects it and lets nearer things cover farther things, all correctly,
because **the only thing that is fake is the texture on the surface**.

What you give up: the silhouette can't change with view angle. So this route ends exactly where the
subject must visibly turn in depth. Everything short of that, it reaches — and it reaches at roughly the
cost of a static page.

| | Parallax layers | **Image planes in a camera** | Models |
|---|---|---|---|
| Camera can move | translate only | **dolly / pan / tilt / park** | anything |
| Occlusion | manual z-index | **real, per-pixel** | real |
| Contact with ground | faked / none | **analytic shadow, see §6** | real |
| Cost of one more element | a div | **one line** | model + bake + export |
| Fails when | camera turns | **subject must rotate in depth** | — |

---

## §2 The asset contract — 素材必须带四个数

An image alone is not placeable. Each asset ships with metadata **measured from its alpha channel**,
never eyeballed (`elements.json` in the case project):

```json
{ "stone-figure": { "w": 1418, "h": 2233, "cx": 0.5358, "baseline": 0.8576 } }
```

| Field | Meaning | What breaks without it |
|---|---|---|
| `w`, `h` | pixel dims | plane aspect wrong, subject stretched |
| `baseline` | where the **ground line** sits in the image, top-down 0–1 | you size the plane by image height, and the faint scree/skirt at the bottom gets counted as body — **the whole object comes out short** |
| `cx` | the **painted centroid** x, 0–1 | `x` means "plane centre", not "the object's centre", so everything you place is offset by its own transparent margin |

Placement then reads in real-world units, which is the point — you say "this is 4.6 m tall and stands at
(7.02, 56)", not "this div is 340px at 62% left":

```js
const planeH = realH / meta.baseline                    // reverse-solve the frame from the visible height
const planeW = planeH * (meta.w / meta.h)
const mesh = new THREE.Mesh(new THREE.PlaneGeometry(planeW, planeH), mat)
mesh.position.set(
  x - (meta.cx - 0.5) * planeW,                          // painted centroid lands on x
  planeH * (meta.baseline - 0.5),                        // ground line lands on y = 0
  z,
)
mesh.renderOrder = order
```

**Where these numbers come from:** `references/image-asset-pipeline.md` — keying, cropping, and the
measuring pass that writes `elements.json`. It is a build artifact; hand-editing a `baseline` to make
something sit right always means the bug is upstream.

**Two different measurements, don't conflate them** — they answer different questions and use different
thresholds:

| number | threshold | why |
|---|---|---|
| `cx` (placement) | alpha-**mass**-weighted centroid, no hard cut | you want the paint's centre of gravity; a hard cut biases it toward the dense side |
| `baseline` (placement) | lowest row with `rowSum > 2% of max` | the lowest row carrying *real* paint — a faint scree skirt must not count as body |
| painted bbox (for marks) | hard `alpha > 200`, ≥1% coverage per row/col | a ring must hug what is *visibly solid*, not the faintest wisp (`affordance.md` §6) |

**And record the crown, not just the foot.** `elements.json` in the case project shipped `baseline` and
nothing about the top — so a dust layer hung at `realH` floated 4.5 m above the mound's summit, because
`planeH = realH / baseline` silently assumes the paint reaches the top of the frame. Anything you attach
to an element needs its own measured anchor (`image-asset-pipeline.md` §4).

**Sprite atlases**: a 4-up sheet is better than four files — same batch means same scale and same light
direction. Rewrite the UVs into atlas space rather than slicing images:
`uv.setX(i, (uv.getX(i) + q) / cols)`. Raycast `hit.uv` then comes back already in atlas space, so
alpha-precise hit testing keeps working for free.

---

## §3 The long lens is the look — `fov 26`, not 50

The single highest-leverage number in the whole scene. A long lens compresses depth, so a 3 m object at
30 m and a 21 m mound at 160 m arrive at **comparable on-screen sizes** and their silhouettes can touch.
A normal 50–60° fov spreads them apart and you get a diorama: big thing near, tiny things far, nothing
relating to anything.

Set it explicitly. `new THREE.PerspectiveCamera(40, …)` then `camera.fov = 26` is not a leftover — it is
the difference between "photographic depth" and "toy set".

---

## §4 Occlusion beats every shader — 剪影必须咬住

Depth is not read from haze or shading. It is read from **one thing covering another**. Place so that
silhouette edges *interlock across depth*:

```
BAD   [mound ..........]        ○ ○ ○        ← three small things standing beside a big thing
GOOD  [mound ....○..○...]  ○                 ← their heads break the mound's outline
```

From the case notes: 摊在空地上量出来是「旁边还站着三个小东西」; pushed until the near figures' heads cut
into the mound's silhouette, **一件三米的石头压住一座二十一米、一百六十米外的土山，大小对比是在同一个
剪影边界上发生的，不再需要观众自己去比**. That last clause is the rule — when the comparison happens *on
one contour*, the viewer doesn't have to do arithmetic, and scale reads instantly.

Depth is also readable from the **foot line**, which is just the ground plane in perspective. In the case
project, measured: `foot_y = 0.576 + 10.03 / (cameraZ − z)`. Nearer things have feet **lower** in frame;
the grading across depths is what says "the ground is flat and going away". Objects placed by eye tend to
land on one horizontal band → a frieze, not a space.

Two derived checks worth keeping:
- **Feet must stay in frame.** A subject whose ground line lands at 0.994 of frame height has its feet
  cut off by the border and reads as "too close" — which the user will report as *size*. Fix by pulling
  back along the view ray, not by scaling (see `affordance.md` §9).
- Pulling back **along the ray** barely moves the horizontal position (`Δx · perMetre` cancels as z
  changes), so you can adjust depth without redoing the composition.

---

## §5 Transparent planes: sort by hand

```js
transparent: true, depthWrite: false, side: THREE.DoubleSide
```
Alpha-blended planes cannot depth-sort themselves. Kill `depthWrite` and assign **explicit `renderOrder`**
to every element. Keep the map as a written document — it *is* the scene's depth structure:

```
cloudBand −1 │ ground 0 │ ridge 1 │ mound 3 │ hall 4 │ walls 4–6 │ gate 6.5
│ pavilion 9 │ horse 9.5 │ towers 10 │ guardian 10.8 │ main figure 11
│ shrubs 30+ │ pebbles 60+ │ outline 70 │ bird 80 │ plate 900+
```

Two planes at nearly the same z with the same renderOrder will flicker; give every element its own number
and leave gaps (that's why 9.5 and 10.8 exist).

**`rotY` is how you get into the scene.** Rotating a plane about y so it runs away from the camera lets
three foreshorten it — that's how courtyard walls become walls rather than a painted facade. Costs
nothing, and it's the cheapest thing that makes a viewer say "wait, is this 3D".

---

## §6 Contact shadow is not optional — and a shadow map won't do it

A plane has no volume, so a shadow map of it is a rectangle on the ground. Instead, **register each
element as a vertical cylinder and solve its shadow analytically inside the ground shader**:

```js
caster(x, z, radius, height)     // → packed into a vec4 array uniform, cap ~48
uLightDir: new THREE.Vector3(-0.90, 0.19, 0.30).normalize()   // y 0.19 ≈ 11° sun, shadow ≈ 5× height
uDepth: 0.55                                                   // how far toward the shadow colour it goes
```

The ground fragment shader draws, per caster, a capsule running from the base along the light direction.
Low sun is worth choosing deliberately: long horizontal shadows tie every object to the same ground and
sweep across the frame, which does more for cohesion than any amount of shading on the objects themselves.

**Without a contact shadow a cutout floats**, no matter how correct its placement is. This is the single
most common reason a well-composed image-plane scene still reads as collage.

---

## §7 「有拼接感」 is a colour-temperature bug — 量，别看

The most transferable finding in the whole project. The user reported 「其中 2 个也没处理好，有拼接感，
不是和其他融为一体的」. The instinct is edges, or feathering, or shadow. **It was neither.**

Measured mean colour over `alpha > 200` pixels, per asset, as `R − B`:

| asset | R−B | reads as |
|---|---|---|
| sand ground | +37 | warm, low sun |
| mound | +52 | warm |
| `stone-figure` | +46 | warm |
| **`spirit-figures`** | **+13** | **near-neutral cold grey — a different sun** |

Nothing under one low raking sun can be neutral. That asset batch was simply lit differently, and the eye
catches it instantly even though nobody can name it. Fix is one uniform multiplied into the sampled colour:

```js
uLight: new THREE.Vector3(1.09, 1.01, 0.90)   // → mean R−B +45, luminance (Rec.601) moves only +2%
```

**Procedure, not taste:** for every asset batch, print mean R, G, B and mean luminance over painted pixels.
Any batch whose R−B (or luminance) is an outlier gets a per-element `uLight` correction until it rejoins
the group. Do not use this as a colour grading knob — an object's own colour is the artist's decision;
this only puts two batches under the same lamp.

---

## §8 One environment pass over everything

Fifty separate images read as one photograph only if the *same* atmosphere crosses all of them:

- **Cloud shadow**, sampled by **world position** — `vCloud = cloudUV((modelMatrix * pos).xyz)`.
  Sampling per element *origin* gives each element one flat brightness, and a wall built from repeated
  segments then shows a hard step at every seam. World-position sampling is continuous by construction,
  and the cloud edge sweeps across a wall exactly the way it should.
- **One gust value** for the whole frame; per-element sway phase/rate on top.
- **Atmospheric perspective as a dissolve into the paper**, not a fog colour:
  ```glsl
  float k = smoothstep(uNear, uFar, vDist);
  c = mix(c, uPaper, k * 0.68);
  ```
  Tune `uNear/uFar` to the **actual depths in your scene**. The first version used 60–620, which
  dissolved 5% at 190 m — i.e. did nothing, while looking like it was configured.
- **Edge treatments as separate uniforms**, each with an off value so 50 elements skip the branch:
  dissolve-above-the-horizon (distant ranges — 远山无脚, mountains standing on paper with no feet),
  chew-the-ends (wall segments), dry-brush-near-camera (the ground plane's near edge).

---

## §9 Vertex motion: uv.y² or it isn't bending

```glsl
sp.x += bend * uSway.x * (0.3 + uGust) * uv.y * uv.y;   // root fixed, tip travels
```
Linear weighting translates the whole image sideways — that reads as *"the picture is drifting"*, not
*"the bush is being bent"*. Square the weight so the base stays nailed to the ground. And make `bend` two
incommensurable sines (`sin(g)*0.62 + sin(g*0.37 + 1.7)*0.38`) so gusts pause and return instead of
metronoming.

Give each instance its own phase and rate. Anything applied globally reads as one sheet of paper moving.

---

## §10 Measure the projection; don't derive it

Before placing anything by number, print the actual world→screen mapping at the scroll position you care
about, and interpolate that table:

```
z=46  foot_y 0.815  per-metre 0.0289  screen-centre = world x 4.48
z=52  foot_y 0.855  per-metre 0.0336  screen-centre = world x 5.10
z=62  foot_y 0.962  per-metre 0.0462  screen-centre = world x 6.14
```

Deriving it from fov by hand is where the bugs are: in this project the same algebra was done twice and
was wrong twice (screen-**width** fraction vs screen-**height** fraction — a 1.78× error that looked
perfectly reasonable). The printed table caught it both times. Ten lines of probe code, and every
placement afterwards is a lookup.

**The exception: when the target itself moves, there is nothing to tabulate.** A table is the right tool
for fixed scene placement. It is the wrong tool for tracking a live DOM rect — a card that reflows, a
heading that scrolls — because the mapping changes every frame. There, derive it, but derive it from
the camera's *own* matrices rather than from hand-written fov trigonometry, which is exactly the algebra
that was wrong twice above:

```js
// NDC from the element's client rect, then a ray to the z-plane the planes live on
const ndc = new THREE.Vector3((cx / innerWidth) * 2 - 1, -(cy / innerHeight) * 2 + 1, 0.5)
ndc.unproject(camera)
const ray  = ndc.sub(camera.position).normalize()
const dist = -camera.position.z / ray.z          // plane at z = 0
const world = camera.position.clone().add(ray.multiplyScalar(dist))
```

**Hard constraint**: `camera.position.z` must be pinned for the lifetime of the mapping. If a parallax or
scroll rig also drifts the camera on z, the DOM↔3D correspondence quietly stretches — this is the same
trap as unprojecting against a moving parallax camera (`light-3d.md` §5), and the same fix applies: do the
unprojection against a static dummy camera and let the visible camera move.

---

## §11 Checklist

- [ ] Every asset went through `image-asset-pipeline.md` — keyed, cropped, `coverage` gated, metadata scripted
- [ ] Per-element on-screen magnification measured at the tightest camera position (image-asset-pipeline.md §6)
- [ ] `fov` set deliberately, long (≈26°) unless there's a reason
- [ ] `depthWrite: false` + a documented `renderOrder` map with gaps
- [ ] Every standing element has a `caster` entry; low sun; shadows visible in frame
- [ ] Mean R−B and luminance printed **per asset batch**; outliers corrected via `uLight`
- [ ] Cloud/atmosphere sampled by **world position**, not element origin
- [ ] `uNear/uFar` checked against the scene's real depth range (print what % dissolves at your farthest element)
- [ ] Silhouettes interlock across depth; foot lines grade instead of sharing one band
- [ ] Feet inside the frame / safe area at every camera position
- [ ] World→screen table printed and used for placement

---

## §12 Two proven topologies — 相机走 vs 世界走

The rung has two shapes, and they are not stylistic variants: they decide what the scene can do.

| | **Camera moves** (heritage-ruins scene, 2026) | **World moves** (SBS *The Boat*, 2015) |
|---|---|---|
| Setup | camera dollies along a path on the scroll rail | `camera.position.z` fixed; `container.position.y = scroller.position` |
| fov | **26** — long lens, silhouettes across depth touch | **50** — normal lens, panels read as layout |
| Reads as | walking into a place | reading a page that has depth |
| Parallax | from the dolly | **free** — a fixed perspective camera + everything sliding in y already separates depths |
| Cost | every element's on-screen magnification changes ⇒ per-element resolution budget (`image-asset-pipeline.md` §6) | scale is constant ⇒ **the resolution question disappears** |
| Needs | a camera path, and a stop for every interaction (`affordance.md` §2) | a layout cursor |

*The Boat*'s numbers, read off the shipped bundle: `PerspectiveCamera(50, aspect, 1, 85000)`,
`camera.position.z = 1200`, never animated except on resize (narrow screens go to z 1700 / fov 73–80).
Scroll writes `containerGL.position.y` **and** `containerCSS.position.y`.

**Pick "world moves" when the piece is read rather than entered.** You lose the dolly and gain a constant
pixel scale, which removes the single hardest constraint of the other topology.

**The camera is still available for punctuation.** *The Boat* keeps the camera parked and then throws it
for one event — the boat taking a wave:

```js
// SeaSick.crash(), sign alternates each call, min 2.5 s apart
camera.position.x  → ±400   over 1.50 s  Power4.easeOut      // thrown out fast
camera.position.x  → 0      over 5.50 s  Power4.easeInOut    // returns slowly
camera.rotation.z  → ±0.3   over 0.75 s  Power4.easeOut
camera.rotation.z  → ±0.05  over 6.75 s  Power2.easeInOut
```

Fast out, slow back — the same asymmetric envelope as an audio duck (`scene-audio.md` §3). A symmetric
in-out reads as a camera move; this reads as an impact. (Disabled entirely on iOS.)

And the continuous version, mouse → world tilt, is deliberately tiny: **±0.035 rad (≈2°)**, lerped at
0.05, applied to the scene *root*, not the camera. One detail worth copying exactly:

```js
beforeUpdate() { this.tmpRY = root.rotation.y; root.rotation.y = 0 }   // measure un-tilted
update()       { root.rotation.y = lerp(this.tmpRY, target, 0.05) }    // then re-apply
```

The screen-position cache, triggers and hit tests all run in the window between those two calls, so the
tilt never pollutes them. Same discipline as pinning a clock before measuring
(`verification-harness.md` §1).

---

## §13 Choose the world unit deliberately — 米 or 栏

Both case projects place things in *real units*; they chose different ones, and the choice propagates
into every number in the codebase.

- **Heritage-ruins scene: metres.** `realH = 4.6`, `position (7.02, 56)`. Right when the subject is a *place* and the
  viewer's question is "how big is that, how far away".
- ***The Boat*: a comic grid.** The world unit system is print layout:

```js
columnsTotal = 12, columnSize = 102, columnGutterSize = 15   // → width 1389
tierSize     = 450, tierGutterSize = 90
```

and a parser takes `"3col"` / `"2tier"` strings straight into world units. Layout is a **typesetting
cursor**: `add()` advances x by half-width + gutter, `wrap()` returns x to the left margin and drops y by
one tier. Verified against the shipped art: `images/013-021/01.png` is **1389 × 450** px — exactly 12
columns by 1 tier. **One world unit = one source pixel**, so "don't enlarge the raster" is structural
rather than a rule someone has to remember.

> Pick the unit the *content* is authored in. If the art comes from a grid, make the grid the world.

---

## §14 How far you get with zero custom shaders

Worth knowing before reaching for GLSL. Measured across *The Boat*'s 117 application modules:

```
ShaderMaterial          0        AdditiveBlending / MultiplyBlending   0
renderOrder             0        MeshBasicMaterial                    19
```

Every plane is `MeshBasicMaterial({ color }) + transparent: true + shading: NoShading`. **No lights, no
custom material, no custom blending, no renderOrder** — atmosphere, depth cueing and mood are all painted
into the textures, and sorting is done with `depthWrite: false` + `depthTest: false` + add order.

Nine years later it still reads as one of the best-looking things on the web. So the honest rule is:

> **A shader is required only when the picture has to change at runtime.**
> The heritage-ruins scene needs shaders because the hand erases, wets, and peels the artwork. *The Boat* needs none
> because the reader only moves through it.

Decide which of those two you are building **before** writing the first material. The shader-heavy route
costs an order of magnitude more, and buys nothing if nobody can touch the picture.

Two cheap tricks that replace shader work outright:

- **Depth cueing by material colour.** *The Boat*'s fifteen wave layers share **one white texture** and
  differ only by `new Color(0.015·i, 0.015·i, 0.015·i)` on the material — a per-layer aerial-perspective
  ramp with no fog and no uniform (see `image-asset-pipeline.md` §10).
- **Motion by UV offset.** `texture.wrapS = RepeatWrapping; texture.offset.x += …` per frame. Combine a
  constant drift with a slow modulation so it never metronomes:
  `offset.x += 0.00075 * (sin(0.01·t) − 0.5) + 0.0011`, and displace y by three incommensurable sines
  multiplied together (`5sin(0.035t) · 3sin(0.015t) · 2sin(0.02t)`). Same anti-metronome principle as §9.

---

## §15 Two scene graphs, one camera — putting real DOM inside the scene

*The Boat* runs `WebGLRenderer` and `CSS3DRenderer` side by side, over two parallel scene graphs, and
renders both **with the same camera** every frame:

```js
rendererGL.render(sceneGL, camera)
rendererCSS.render(sceneCSS, camera)
```

Scroll writes the same y to both containers; each display object may own an `objectGL`, an `objectCSS`,
or both. That is how the body text tilts with the boat while staying selectable, real type — rather than
being baked into a texture or positioned by a projection every frame.

Trade-offs, since this is not free:

- CSS3D transforms are expensive to add/remove. *The Boat* batches those mutations and throttles them to
  **500 ms on desktop / 2500 ms on mobile** (`scene-streaming.md` §3).
- The CSS layer needs `pointer-events: none` and `willChange: transform`.
- No depth interleaving between the two layers — DOM is composited over the canvas as a whole. Anything
  that must be *occluded by* the scene has to be a plane.

If the text never needs to be selectable or reflowable, projecting a DOM overlay onto a painted bbox
(`affordance.md` §6) is cheaper. Reach for CSS3D when the type is part of the picture's geometry.
