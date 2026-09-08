# Handfeel — Why Motion Feels Dead and How to Fix It

The user saying "手感差 / 太生硬 / 四平八稳 / 不跟手 / 没那种感觉" almost always maps to one of the
mechanical gaps below. Diagnose against this list before touching parameters.

All recipes are vanilla rAF — no library needed. They compose: a good hero uses 3–4 of them at once.

---

## Diagnosis Table

| Symptom (user's words) | Root cause | Fix |
|---|---|---|
| "四平八稳" / "太机械" | Plain lerp toward target — no overshoot, no weight | Underdamped spring (§1) |
| "不跟手" / "没劲" | Element ignores its own velocity | Velocity coupling (§2) |
| "自己在动 / 误触发" | Trackpad momentum keeps firing wheel events | Momentum guard (§3) |
| "画面是死的" | Only the hero element moves; environment is static | Secondary motion / jelly (§4) |
| "假 / 像贴图" (one flat image, static camera) | No light response — flat PNG with static shadow | Fake lighting via alpha mask (§5) |
| "有拼接感 / 没融进去 / 像贴上去的" (a *scene* of images) | Different asset batches lit by different suns, or no contact shadow | Measure mean `R−B` per batch, add analytic ground shadows → `image-plane-3d.md` §6–7 |
| "僵住了" | Nothing moves at idle | Idle breathing (§6) |
| "点不开" / "只有一个能点" / "没反应" | Usually **not** a hit-test bug — no visible invitation, or it expired | → `affordance.md` (audit before touching any hit code) |
| "按住不放太累" / "划过要等好久才还原" | Gesture demands a cost up front, or feedback is on a timer | Down-records/up-decides + instant restore → `affordance.md` §7 |
| "跟手，但总差一点" / 追不上 | Following a *moving* target with a filter — steady-state lag is `speed / k`, by arithmetic | Lead term (§7.2) |
| "一抖一抖" / 追随抖动 | A correction added *after* the filter — the follower undoes it every frame | Bake the correction into the target (§7.3) |
| 姿态 snap，"身体在宣布输入" | Pose read straight off the input device instead of off measured acceleration | Acceleration → critically damped spring (§7.4) |
| 手感在 30 / 60 / 120fps 下不一样 | Per-frame constant lerp (`x += d * 0.1`) is a different filter at each frame rate | `1 - exp(-k·dt)` (§7.1), then prove it (§7.5) |
| 撞击"没冲击力"，或抖成一团糊 | No screen shake at all, or several sources summed | Max-not-sum, split frequencies (§8) |

---

## §1 Underdamped Spring (replaces lerp)

Lerp always decelerates monotonically → reads as "sliding". A spring with damping < critical
overshoots its landing slightly and settles → reads as "jumping / landing with weight".

```js
// per frame, dt in seconds (clamp: const dt = Math.min(rawDt, 1/30))
vel += (target - x) * STIFFNESS * dt;  // STIFFNESS 60–90
vel *= DAMPING;                        // 0.86 = playful bounce, 0.90 = jelly, 0.93 = calm
x += vel * dt;
```

- One spring per animated quantity. Keep `vel` in a ref/closure, never in React state.
- Tune: overshoot too big → raise DAMPING toward 0.92; feels like lerp → lower toward 0.85.

## §2 Velocity Coupling (lean into movement)

The element should react to *how fast* it is moving, not just where it is.
Classic: rotation proportional to velocity — a fish/card/cursor leans into its direction of travel
and straightens as it settles (free secondary animation, since spring velocity decays naturally).

```js
const lean = clamp(vel * GAIN, -MAX, MAX);   // e.g. GAIN 0.5, MAX ±22deg
el.style.transform = `... rotateZ(${baseTilt + lean}deg)`;
```

Also works as: skew for text under scroll, stretch (scaleX) for drag, blur for very fast motion.

For a full multi-point trail (not just one element) where each point should lag the one ahead of it — see `shaders-spec.md` Recipe G (damp-chain trail) and `pattern-recipes.md` #11 (SVG goo trail) — same leader-follower math, DOM/SVG/shader variants.

## §3 Wheel Momentum Guard

Trackpads emit inertial wheel events for ~1s after fingers lift. Naive `offset += deltaY` causes
ghost auto-advance. Accumulate-threshold + cooldown gives exactly one step per gesture:

```js
if (now < lockedUntil) return;                    // eat the momentum tail
if (Math.sign(delta) !== Math.sign(acc)) acc = 0; // direction change resets
acc += delta;
if (Math.abs(acc) >= 90) {                        // ~90px per step
  step(Math.sign(acc));
  acc = 0;
  lockedUntil = now + 600;                        // 550–650ms lock
}
// and decay acc by *0.92 each rAF frame
```

## §4 Secondary Motion / Jelly Wobble

Environment elements (circles, lines, background type) should react to the primary motion's
velocity — like objects submerged in the same fluid. Feed the primary velocity into a *loose*
spring (damping ~0.90) so decorations squash while moving and keep jiggling after the stop:

```js
jVel += (clamp(primaryVel, -1.4, 1.4) - j) * 55 * dt;
jVel *= 0.90;                                  // loose → visible residual wobble
j += jVel * dt;
// volume-preserving squash & stretch:
el.style.transform = `scale(${1 + j * k}, ${1 - j * k}) rotate(${j * few}deg)`;
```

Rules that make it read as organic, not synchronized:
- **Different gain / direction / phase per element** (one squashes X, another Y, amplitudes ×1.0/×1.6/×2.1)
- Cheap tier only: transform + opacity. Add slight translate ("pushed by the current").
- Text blocks: `skewX(j * -3.5deg)` is enough.

## §5 Fake Lighting on Flat Images (2.5D)

When the asset is a PNG cutout and real 3D is overkill, mouse-driven lighting sells depth:

```jsx
// two overlay divs, masked to the image's own alpha
<div className="glow"  style={{ WebkitMaskImage:`url(${src})`, maskImage:`url(${src})` }} />
<div className="shade" style={{ /* same mask */ }} />
```
```css
.glow, .shade { position:absolute; inset:0; pointer-events:none;
  mask-size:contain; mask-repeat:no-repeat; mask-position:center; }
.glow  { background: radial-gradient(46% 46% at var(--light-x) var(--light-y),
         rgba(255,255,255,.55), rgba(255,255,255,.16) 42%, transparent 72%);
         mix-blend-mode: screen; }
.shade { background: radial-gradient(70% 70% at var(--shade-x) var(--shade-y),
         rgba(0,20,50,.38), rgba(0,20,50,.12) 45%, transparent 75%);
         mix-blend-mode: multiply; }
```

- `--light-x/y` chase the mouse (lerp 0.08); `--shade-x/y = 100% − light`.
- Drop-shadow offset moves opposite the light; blur grows with tilt angle.
- Pair with a `rotateX/rotateY` stage tilt (12–16° max) driven by mouse position.

## §6 Idle Breathing

Nothing on screen should be perfectly still. Cheapest life-support, added to existing transforms:

```js
const t = (now - start) / 1000;
const bobY  = Math.sin(t * 1.1) * 1.6;   // % or px
const swayZ = Math.sin(t * 0.7) * 1.2;   // deg — different frequency, never synced
```

Use different frequencies per element (0.7 / 0.9 / 1.1 Hz-ish) so nothing pulses in unison.

## §7 Following — the half that must *not* overshoot

§1 is for things that should land with weight. But a camera trailing a subject, a cursor chasing
the pointer, a panel returning to level, a rail sliding under the active nav item — these must
arrive and *stop*. Same family, different damping. Four independent builds got this wrong in the
same four ways, so all four are written down.

### §7.1 Frame-rate-independent exponential follow

```js
// dt in seconds; k is "tightness" in 1/s — NOT a per-frame fraction
x += (target - x) * (1 - Math.exp(-k * dt));
```

`x += (target - x) * 0.1` is the same line everyone writes, and it is a **different filter at
30 / 60 / 120 fps** — the page feels heavier on a slow frame and twitchy on a fast one. Measured
`k` from a flight/drive scene: camera follow `4.5`, yaw self-centring `2.2`, pitch auto-level `0.35`.
Low `k` is a legitimate design choice, not sloppiness — `0.35` is a horizon that takes ~3 s to settle.

### §7.2 Following a moving target lags by `speed / k` — compute it, don't tune it

A first-order filter chasing a target that is itself moving settles at a **constant** offset behind
it. This is arithmetic, not a tuning failure. Documented case: a chase camera specified at 13.5 m
sat at a measured **20.2 m** at speed. No amount of easing-curve fiddling closes that; a lead term does:

```js
const aim = targetPos + targetVel / k;   // cancels the steady-state lag exactly
x += (aim - x) * (1 - Math.exp(-k * dt));
```

On a page this is the custom cursor that trails a fast pointer, the highlight rail that never quite
reaches the active item while scrolling, the tooltip behind a dragged handle. **"跟手但总差一点" is
this, and the fix is a lead term, not a stiffer spring** — stiffening also removes the softness that
was the point.

### §7.3 A correction applied *after* the filter gets undone next frame

If you filter a value and then add a correction on top, the filter is still aiming at the
uncorrected target, so it pulls back toward it on the next frame — and you get hunting. Documented
case: a chase camera lifting over terrain, corrected after the lerp, oscillated **±0.15–0.45 units
per frame** both in motion and parked; the user's words were 「画面一抖一抖」.

```js
// WRONG — the follower never learns about the lift
cam.y = follow(cam.y, base.y, k);
cam.y += groundLift();

// RIGHT — the correction gets its own filter, then is baked into the target
lift  = follow(lift, sampleGroundLift(), rising ? 18 : 2.2);   // fast up, slow down
desired.y = base.y + lift;
cam.y = follow(cam.y, desired.y, k);                            // one filter, one target
```

**One quantity, one filter, one target.** Anything written to that quantity after the filter runs is
a bug, not a tweak. The asymmetric `k` (18 rising / 2.2 falling) is the second half of the fix: rising
late clips the subject, falling fast reads as the floor dropping away.

### §7.4 Pose is driven by acceleration through a critically damped spring — never by the input

```js
// WRONG — reads the device, so it snaps the frame a key goes down
mesh.rotation.z = -steerInput * LEAN;

// RIGHT — reads what actually happened to the body
const k = 120, c = 2 * Math.sqrt(k);      // c = 2√k is critical damping
v += (-k * (x - lateralAccel * LEAN) - c * v) * dt;
x += v * dt;                               // ≈0.09 s to 63% at k = 120
```

Reading the input makes the body *announce* the input; reading acceleration makes it *react to the
world*. Critical damping is §1's equation with the damping moved to the boundary: still a lag and a
settle, but zero overshoot — right for anything that would look broken wobbling past its mark.
Once pose is acceleration-driven, secondary motion on collisions and direction changes **emerges for
free**, with no extra code. The same form at `k = 200` (~0.14 s) is a good size/scale growth.

### §7.5 Every formula here claims frame-rate independence — prove it

`exp(-k·dt)` is only frame-rate-independent if nothing else in the loop is quietly per-frame. Run the
same input at 30 / 60 / 120 fps and diff the trajectories → `verification-harness.md` §12.

---

## §8 Screen shake

The impact channel most web motion never uses. Two rules make the difference between "有冲击力" and
"抖成一团糊":

```js
// accumulate — the strongest source wins; sources are NEVER summed
shakeAmp = Math.max(shakeAmp, amp);
shakeEnd = Math.max(shakeEnd, now + dur);

// apply — different frequency per axis, amplitude decays linearly to zero
const e = Math.max(0, (shakeEnd - now) / dur);
el.style.translate = `${Math.sin(t * 47) * shakeAmp * e}px ${Math.sin(t * 31 + 1.3) * shakeAmp * e}px`;
```

- **Max, not sum.** Three events landing in one frame must not stack — summing is how a hit turns
  into a seizure.
- **Different frequency per axis.** One frequency on both axes traces a circle, which reads as a
  wobble; `47` vs `31` with a phase offset reads as an impact.
- **Everything is short.** Measured amplitude/duration ladder from a game build: pickup `0.10 / 0.22 s`,
  hard collision `0.35 / 0.35 s`, landing `0.07 / 0.14 s`, drift `0.04 + 0.02·tier / 0.12 s`. Port the
  *ratios*, not the units — biggest event ≈5× the smallest, nothing over 0.35 s.
- Shake a wrapper with `translate`, never a transform the layout depends on. Gate the whole channel on
  `prefers-reduced-motion`, and never shake text the user is currently reading.

---

## Composition Rule

Handfeel = position spring (§1) + velocity coupling (§2) + secondary reaction (§4) + idle life (§6),
with input hygiene (§3) and, for flat assets, light response (§5). Anything that *follows* something
else — camera, cursor, rail, tooltip — uses §7 instead of §1, and impacts get §8.
If a build has only §1, it will still feel "顺但是没劲" — §2 and §4 are what read as *weight* and *fluid*.
