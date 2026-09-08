# WebGL Shaders Specification & Recipes

Fragment shaders (GLSL) are the ultimate design material for high-end organic animations (liquid, fluid, distortion, grain). 

This document defines installation-free integration templates, performance constraints, and optimized GLSL snippets for runtime execution.

---

## 1. Do Shaders Need Installation? (关于安装与依赖)

**No npm installation is required to compile or run shaders.** 
Every modern browser compiles GLSL natively via WebGL/WebGL2. However, raw WebGL context setup is verbose. 

To keep your projects light, avoid importing massive 3D libraries (like Three.js, which adds ~600KB overhead) just to run a 2D fullscreen background. Use this **Zero-Dependency Vanilla WebGL2 Boilerplate** instead:

```javascript
// webgl-runner.js — Zero-dependency Fullscreen Fragment Shader Runner
export function initShader(canvas, fragmentShaderSource) {
  const gl = canvas.getContext('webgl2');
  if (!gl) return console.error('WebGL2 not supported');

  const vs = `#version 300 es
    in vec2 position;
    out vec2 vUv;
    void main() {
      vUv = position * 0.5 + 0.5;
      vUv.y = 1.0 - vUv.y; // Flip Y to match CSS coordinates
      gl_Position = vec4(position, 0.0, 1.0);
    }`;

  const fs = `#version 300 es
    precision highp float;
    in vec2 vUv;
    out vec4 fragColor;
    ${fragmentShaderSource}
    void main() {
      fragColor = mainImage(vUv);
    }`;

  function compileShader(source, type) {
    const s = gl.createShader(type);
    gl.shaderSource(s, source);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error(gl.getShaderInfoLog(s));
      gl.deleteShader(s);
      return null;
    }
    return s;
  }

  const program = gl.createProgram();
  gl.attachShader(program, compileShader(vs, gl.VERTEX_SHADER));
  gl.attachShader(program, compileShader(fs, gl.FRAGMENT_SHADER));
  gl.linkProgram(program);

  // Set up full-screen plane (2 triangles)
  const positionAttributeLocation = gl.getAttribLocation(program, "position");
  const positionBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, -1,1, 1,-1, 1,1]), gl.STATIC_DRAW);
  gl.enableVertexAttribArray(positionAttributeLocation);
  gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);

  // Uniform locations
  const uTimeLoc = gl.getUniformLocation(program, "uTime");
  const uResolutionLoc = gl.getUniformLocation(program, "uResolution");
  const uMouseLoc = gl.getUniformLocation(program, "uMouse");

  let mouseX = 0.5, mouseY = 0.5;
  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX / window.innerWidth;
    mouseY = 1.0 - (e.clientY / window.innerHeight);
  });

  let animationFrameId;
  function render(time) {
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.useProgram(program);
    gl.uniform1f(uTimeLoc, time * 0.001);
    gl.uniform2f(uResolutionLoc, canvas.width, canvas.height);
    gl.uniform2f(uMouseLoc, mouseX, mouseY);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    animationFrameId = requestAnimationFrame(render);
  }
  
  render(0);
  return () => cancelAnimationFrame(animationFrameId);
}
```

---

## 2. WebGL Integration Patterns (集成技术栈对比)

Shaders need a container to run. Choose your container based on the stack:

| Integration Container | Library | Best For | Performance Cost |
|---|---|---|---|
| **Raw WebGL2 Canvas** | Vanilla JS (Boilerplate above) | Fullscreen backgrounds, single-plane effects, Zero-dep | Low (Fastest startup) |
| **Paper Shaders React** | `@paper-design/shaders-react` | **React/Next.js declarative components, mesh/grain presets** | Low-Medium (Highly optimized) |
| **Three.js ShaderMaterial** | Three.js | 3D mesh distortion, scroll camera interactions | Medium (Needs library overhead) |
| **React Three Fiber (R3F)** | `@react-three/fiber` + `@react-three/drei` | React-based interactive canvas grids | High (Needs React reconciliation check) |

---

## 3. React Integration via `@paper-design/shaders-react` (React 集成规范)

For React / Next.js projects, `@paper-design/shaders-react` is the **primary recommended standard**. It provides pre-compiled, highly optimized shader components and presets (MeshGradient, Glass, Noise, Voronoi, Dithering, Halftone, etc.).

### A. Quick Start: Declarative Mesh Gradient
Always ensure the parent container (or the component style) has defined width and height.

```jsx
'use client'; // Required for Next.js App Router (Client component)
import { MeshGradient } from '@paper-design/shaders-react';

export function BackgroundHero() {
  return (
    <div style={{ width: '100vw', height: '100vh', position: 'fixed', zIndex: -1 }}>
      <MeshGradient 
        colors={['#5100ff', '#00ff80', '#ffcc00', '#ea00ff']} 
        speed={0.25} 
        distortion={1.1} 
        swirl={0.8} 
      />
    </div>
  );
}
```

### B. Using Presets for Instant Aesthetics (一键预设)
You can destructure built-in presets (e.g. `Beach`, `Sunset`, `DeepSpace`) directly:

```jsx
'use client';
import { MeshGradient, meshGradientPresets } from '@paper-design/shaders-react';

export function SunsetPanel() {
  const sunset = meshGradientPresets.find(p => p.name === 'Sunset');
  return (
    <MeshGradient 
      {...sunset?.params} 
      style={{ width: '100%', height: '100%' }} 
    />
  );
}
```

### C. SSR & Next.js Safeguards
Because WebGL requires `window` and `document.createElement('canvas')`, rendering these components on the server will crash Next.js.
- **Rule 1**: Always add `'use client';` at the very top of the file containing these components.
- **Rule 2**: If rendering in a Server-Side layout, dynamically import the shader component with `{ ssr: false }`:
```jsx
import dynamic from 'next/dynamic';
const MeshGradient = dynamic(
  () => import('@paper-design/shaders-react').then(mod => mod.MeshGradient),
  { ssr: false }
);
```

---

## 4. Standard Shader Uniforms (控制变量)

Every custom shader must expose these basic uniforms to link DOM states with GPU threads:

```glsl
uniform vec2 uResolution; // Viewport width and height (px)
uniform float uTime;      // Elapsed time in seconds (for animation loop)
uniform vec2 uMouse;      // Normalized mouse coordinates [0.0, 1.0]
uniform float uProgress;  // Transition controller [0.0 to 1.0] (linked to scroll/timeline)
```

---

## 5. The Core GLSL Recipes Catalog (核心算法库)

Use these snippets directly inside your `mainImage(vec2 uv)` fragment function:

### Recipe A: Simplex Noise (2D/3D)
Used for organic waves, liquid movement, and cloud-like flows. *Avoid calling expensive sine/cosine loops; use hash-based noise instead.*

```glsl
// High-performance 2D noise generator (stegu/webgl-noise)
vec3 permute(vec3 x) { return mod(((x*34.0)+1.0)*x, 289.0); }

float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
           -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy) );
  vec2 x0 = v -   i + dot(i, C.xx) ;
  vec2 i1;
  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0) )
  + i.x + vec3(0.0, i1.x, 1.0) );
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
    dot(x12.zw,x12.zw)), 0.0);
  m = m*m ;
  m = m*m ;
  vec3 x = 2.0 * fract(p * C.www) - 1.0 ;
  vec3 h = abs(x) - 0.5 ;
  vec3 a0 = x - floor(x + 0.5);
  vec3 g = sin(a0*15.707) * (1.0 - h*h); // fast trigonometric smooth
  vec3 attr = vec3(dot(g.x, x0), dot(g.yz, x12.xy), dot(g.z, x12.zw));
  return 130.0 * dot(m, attr);
}
```

### Recipe B: Mouse-Responsive Ripple Displacement (鼠标划过波纹)
Warp the background texture or layout based on mouse distance.

```glsl
uniform sampler2D uTexture;

vec4 mainImage(vec2 uv) {
  vec2 mouseDir = uv - uMouse;
  float dist = length(mouseDir);
  
  // Create localized distortion wave within 0.15 radius of cursor
  float radius = 0.15;
  float strength = 0.03;
  
  vec2 distortedUv = uv;
  if (dist < radius) {
    float force = (1.0 - dist / radius) * strength;
    distortedUv += normalize(mouseDir) * force;
  }
  
  return texture(uTexture, distortedUv);
}
```

### Recipe C: Liquid Image Transition (液态转场)
Make two images merge with organic fluid displacement.

```glsl
uniform sampler2D uTextureFrom;
uniform sampler2D uTextureTo;
uniform float uProgress; // Linked to GSAP timeline (0.0 to 1.0)

vec4 mainImage(vec2 uv) {
  // Generate displacement map from noise
  float noise = snoise(uv * 4.0 + uTime * 0.2);
  
  // Warp UV offset based on progress and noise
  vec2 distortedUv1 = uv + vec2(noise * 0.1 * uProgress);
  vec2 distortedUv2 = uv - vec2(noise * 0.1 * (1.0 - uProgress));
  
  vec4 color1 = texture(uTextureFrom, distortedUv1);
  vec4 color2 = texture(uTextureTo, distortedUv2);
  
  return mix(color1, color2, uProgress);
}
```

### Recipe D: Faulty Glitch Effect (电磁故障/噪点故障)
Simulates digital CRT screen anomalies and color splitting.

```glsl
uniform sampler2D uTexture;

float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

vec4 mainImage(vec2 uv) {
  float glitchThreshold = 0.95;
  float timeStep = floor(uTime * 15.0); // Step time
  
  float glitch = random(vec2(timeStep, 1.0));
  vec2 distortedUv = uv;
  
  if (glitch > glitchThreshold) {
    // Slice image horizontally
    float ySplit = random(vec2(timeStep, 2.0));
    if (uv.y > ySplit && uv.y < ySplit + 0.05) {
      distortedUv.x += (random(vec2(timeStep, 3.0)) - 0.5) * 0.1;
    }
  }
  
  // Chromatic Aberration (Color splitting)
  float shift = 0.005 * (random(vec2(timeStep, 4.0)) - 0.5);
  vec4 rCol = texture(uTexture, distortedUv + vec2(shift, 0.0));
  vec4 gCol = texture(uTexture, distortedUv);
  vec4 bCol = texture(uTexture, distortedUv - vec2(shift, 0.0));
  
  return vec4(rCol.r, gCol.g, bCol.b, 1.0);
}
```

### Recipe E: Film Grain Overlay (颗粒感噪点)
Adds a physical, analog film texture to eliminate the digital sterile look. Very cheap and effective.

```glsl
vec4 mainImage(vec2 uv) {
  // Read baseline color (e.g. from background or texture)
  vec4 baseColor = vec4(0.97, 0.95, 0.93, 1.0); // Warm linen background #f7f2ed
  
  // Generates grain value [0.0 to 1.0] changing rapidly in time
  float m = uv.x * uv.y * uTime * 1000.0;
  float grain = fract(sin(m) * 43758.5453);
  
  // Apply subtle grain subtraction (amplitude 0.035 = 3.5%)
  baseColor.rgb -= vec3(grain * 0.035);
  return baseColor;
}
```

### Recipe F: Analytic-Ellipse Fake Depth Portrait (无深度图的 2.5D 人像)

A PNG cutout (portrait, product shot) can fake real parallax/depth response without a depth map or 3D model — sum a few analytic ellipses in the **vertex shader** to approximate "how deep is this pixel" (face nearer than torso, nose nearer than cheeks), then drive both vertex displacement and UV parallax off that value. (✅ 实测 2026-07)

```glsl
// vertex shader
uniform vec2 uPointer;   // -1..1
uniform float uDragging; // 0..1
varying float vDepth;

float ellipse(vec2 uv, vec2 center, vec2 radius) {
  vec2 p = (uv - center) / radius;
  return 1.0 - smoothstep(0.35, 1.0, dot(p, p)); // 1.0 at center, falls off past the ellipse edge
}

void main() {
  // Tune these ellipses to the specific portrait's actual proportions —
  // they're a cheap stand-in for a real depth map, not a generic formula.
  float head  = ellipse(uv, vec2(0.5, 0.64), vec2(0.30, 0.38));
  float face  = ellipse(uv, vec2(0.5, 0.59), vec2(0.20, 0.27));
  float torso = ellipse(uv, vec2(0.5, 0.18), vec2(0.58, 0.42));
  float nose  = ellipse(uv, vec2(0.5, 0.59), vec2(0.07, 0.13));
  float depth = clamp(head * 0.35 + face * 0.48 + nose * 0.24 + torso * 0.09, 0.0, 1.0);
  vDepth = depth;

  vec3 p = position;
  float strength = mix(0.055, 0.12, uDragging); // more displacement while actively dragged
  p.x += uPointer.x * depth * strength;
  p.y -= uPointer.y * depth * strength * 0.52;
  p.z += depth * 0.15;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}
```

```glsl
// fragment shader — UV parallax uses the same vDepth so near parts (face) shift
// more than far parts (torso), which is what actually reads as "depth" rather
// than a flat sticker moving as one rigid piece.
varying float vDepth;
uniform vec2 uPointer;
uniform sampler2D tPortrait;

void main() {
  vec2 parallax = uPointer * vDepth * 0.01;
  vec4 portrait = texture2D(tPortrait, vUv - parallax);
  if (portrait.a < 0.02) discard; // keep the cutout's alpha edge instead of a hard quad
  gl_FragColor = portrait;
}
```

**When to use this over a real depth map**: single portrait/product cutout where the identifiable "near" features (face, nose, held object) map cleanly onto 2-4 ellipses. For a busy scene or an asset where near/far isn't representable by ellipses, use an authored depth map instead.

### Recipe G: Damp-Chain Trail (leader-follower SDF trail)

A trail of N points chases the pointer/target with **per-point exponential lag** — each point trails the one ahead of it at a slower rate, so the tail whips and settles like a rope rather than all points moving in lockstep. Feed the point positions into a segment-distance SDF for a flowing ribbon/liquid-trail look. Pairs with pattern-recipes.md #11 (same leader-follower math drives the SVG goo trail; this is the shader/R3F version).

```js
// R3F / vanilla — MathUtils.damp(current, target, lambda, dt) ≈ exponential ease,
// framerate-independent (unlike a fixed-factor lerp).
import { MathUtils } from 'three'

useFrame((state, delta) => {
  const target = { x: pointerX, y: pointerY }
  // Lambda decreases down the chain — later points react more sluggishly,
  // which is what makes the tail read as trailing rather than parallel-following.
  a.x = MathUtils.damp(a.x, target.x, 16, delta)
  b.x = MathUtils.damp(b.x, a.x, 8.4, delta)
  c.x = MathUtils.damp(c.x, b.x, 5.2, delta)
  d.x = MathUtils.damp(d.x, c.x, 3.1, delta)
  e.x = MathUtils.damp(e.x, d.x, 1.85, delta)
  f.x = MathUtils.damp(f.x, e.x, 1.05, delta)
  // ...mirror for .y — pass each pair as a uTrailN vec2 uniform
})
```

```glsl
// fragment: distance from this pixel to the nearest trail segment
float segmentDistance(vec2 p, vec2 a, vec2 b) {
  vec2 pa = p - a, ba = b - a;
  float h = clamp(dot(pa, ba) / max(dot(ba, ba), 0.0001), 0.0, 1.0);
  return length(pa - ba * h);
}

void main() {
  float d = min(
    segmentDistance(vUv, uTrail0, uTrail1),
    min(segmentDistance(vUv, uTrail1, uTrail2), segmentDistance(vUv, uTrail2, uTrail3))
  );
  float body = 1.0 - smoothstep(0.115, 0.135, d); // ribbon width
  gl_FragColor = vec4(color, body);
}
```

**Lambda tuning**: halving each successive lambda roughly doubles that point's lag — keep the ratio between consecutive points in the 1.5–2x range; too close together and the tail looks stiff/parallel, too spread out and the tail end detaches visually from the head.

### Recipe H: Text-as-Texture (排版进 Shader 的唯一正路)

Any shader effect (liquid, refraction, distortion) that needs to act on **typeset text** should not try to render text in GLSL — draw the text to an offscreen 2D canvas first, then feed that canvas as a texture into the shader like any other image. This is the only practical way to get real font rendering, kerning, and multi-line layout into a WebGL pipeline.

```js
function generateTextTexture(lines, { width, height, font, color, bg }) {
  const dpr = window.devicePixelRatio || 1
  const canvas = document.createElement('canvas')
  canvas.width = width * dpr
  canvas.height = height * dpr
  const ctx = canvas.getContext('2d')
  ctx.scale(dpr, dpr)
  ctx.fillStyle = bg
  ctx.fillRect(0, 0, width, height)
  ctx.fillStyle = color
  ctx.font = font
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  const lineHeight = parseInt(font, 10) * 1.08
  lines.forEach((line, i) => {
    ctx.fillText(line, width / 2, height / 2 + (i - (lines.length - 1) / 2) * lineHeight)
  })
  return canvas.toDataURL('image/png') // feed to loadImage() / new THREE.TextureLoader()
}
```

**Why not render text directly as SDF glyphs in-shader**: it's technically possible (MSDF font atlases) but is a whole separate font-rendering pipeline — not worth it unless the shader needs per-glyph vertex control. For "make this heading ripple/refract/distort," rasterizing once to a texture and letting the shader treat it as pixels is simpler, cheaper, and handles any font/language for free.

## 6. Integration Traps (三个静默失败 + 两个真实配方)

These do not throw. They render something wrong, or render nothing at all, and the console stays clean.

### 6.1 A float literal written as an integer kills the whole shader, silently

Injecting values into a chunk via `onBeforeCompile` (or building GLSL by string concatenation) and
writing `6` where the language wants `6.0` makes `smoothstep`/`mix`/`pow` fail overload resolution.
The program fails to link, the material falls back, and **every mesh using it disappears** — one
documented build lost an entire instanced pine forest this way, with no error surfaced.

```js
const f = (n) => (Number.isInteger(n) ? n.toFixed(1) : String(n));   // 6 -> "6.0"
shader.vertexShader = shader.vertexShader.replace('#include <begin_vertex>',
  `#include <begin_vertex>\n  transformed.x += ${f(amp)} * sin(uTime);`);
```

Route **every** injected number through that function. It costs one line and removes the entire class.

### 6.2 A custom `ShaderMaterial` must re-add tone mapping and colour space

Three.js built-in materials include `tonemapping_fragment` and `colorspace_fragment`. A hand-written
fragment shader does not, so it renders visibly darker than everything beside it and nobody can say why.

```glsl
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
```

With `EffectComposer`, the intermediate render targets are **linear** — tone mapping happens once, in
the final `OutputPass`. A pass that tone-maps in the middle of the chain double-applies it.

### 6.3 `DepthTexture` on WebGL2 only filters as `NEAREST`

Setting `minFilter`/`magFilter` to `LINEAR` on a depth texture makes the framebuffer incomplete; the
sampler then returns **0 everywhere**. Symptom: any depth-driven effect reads "zero depth" over the
whole frame — a water shader flattens into a white sheet. There is no warning.

Three neighbours in the same family, all silent:
- `UniformsUtils.merge` does not deep-clone `Vector4` array uniforms — fill them in by hand after merging.
- `vertexColors: true` on a geometry with no `color` attribute renders **black**, not "ignored". For
  per-instance colour use `setColorAt`.
- An alpha-cutout `InstancedMesh` casts a solid rectangular shadow unless you also supply a
  `customDepthMaterial` with the same alpha test.

### 6.4 High-frequency detail must fall off with view distance, or it shimmers

Any noise, sparkle, or specular term at full strength in the mid-distance aliases into a field of
crawling white dots — the usual report is 「看着不舒适」 rather than "aliasing".

```glsl
float detail    = exp(-vViewZ * 0.028);          // general high-frequency terms
float sparkle   = exp(-vViewZ * 0.05);           // specular / glint, falls off faster
```

Measured on a water surface, but it applies to every high-frequency term: grain, foliage detail,
fabric weave, star fields. This is a *sampling* fix, not an art choice — it belongs in the shader,
not in a distance-fade material.

### 6.5 Instanced wind: phase comes from world position, never from a random seed

Wind is a spatially coherent field: neighbouring plants lean together, distant ones lag. Randomising
each instance's phase produces static-like flicker — the opposite of wind. (This is the counterpart to
the rule for *intermittent* effects, where independent per-instance timers are exactly right; a
continuous field is the other case.)

```glsl
float phase = uWindTime * 1.6 + instanceOrigin.x * 0.35 + instanceOrigin.z * 0.27;
float mask  = smoothstep(hMax * 0.25, hMax, position.y);   // trunk still, crown moves
transformed.x += sin(phase)         * amp        * mask;
transformed.z += sin(phase * 0.83)  * amp * 0.7  * mask;   // different freq + amp, or it swings in one plane
```

Measured: trees `amp 0.05, hMax 6`; grass `amp 0.04, hMax 0.5`. Two axes must differ in **both**
frequency and amplitude, otherwise every instance traces the same flat ellipse. Under
`prefers-reduced-motion`, skip the injection entirely rather than setting `amp = 0` — a zero-amplitude
shader still costs the vertex work.

### 6.6 Flicker light: two sines beat noise, and stay seekable

```glsl
float flicker = 1.0 + 0.1 * sin(t * 13.0) + 0.06 * sin(t * 31.0 + 1.3);
```

Two incommensurate frequencies read as fire; one reads as a pulse; noise costs more and is not a pure
function of `t` — which matters, because this form is **seekable**: the same `t` always gives the same
frame, so it survives the deterministic-render requirement (`verification-harness.md` §3).

---

## 7. Performance & Degradation Rules (性能与降级红线)

### 1. Canvas Dimensions Limit
Never let a WebGL canvas render at absolute native size on Retina screens (DPR = 3 or 4) — it will lag on 4K monitors.
- **Rule**: Cap render resolution at `DPR = 1.5` or `2.0` max.
```js
const dpr = Math.min(window.devicePixelRatio, 2.0);
renderer.setSize(width, height, false); // false keeps CSS styling handling layout
```

### 2. Tab Visibility Pause (不可见暂停)
Do not waste GPU cycles when the user transitions to another tab or scrolls the canvas completely off-screen.
- **Rule**: Use `IntersectionObserver` to pause/resume the shader loop.
```js
const observer = new IntersectionObserver(([entry]) => {
  if (entry.isIntersecting) startShaderLoop();
  else stopShaderLoop();
});
observer.observe(canvasEl);
```

### 3. mobile & Reduced Motion Fallbacks
Shaders can run hot on mobile devices, leading to rapid battery drain.
- **Rule**: If screen width `< 768px` or user prefers reduced motion, either:
  1. Turn off the WebGL render loop completely.
  2. Replace it with a static, CSS-upscaled gradient texture representing the first frame.

