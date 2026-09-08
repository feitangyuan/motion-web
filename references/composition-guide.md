# Dynamic Composition & Orchestration Guide

This guide defines how to use the motion and visual banks as **raw materials and design logic**, rather than rigid templates. 

When a user drops a vague requirement, you must act as a creative developer: synthesizing custom palettes, engineering bespoke layout hierarchies, and scripting responsive, tactile interactive systems from scratch.

---

## The Agentic Ideation Flow (动态创意合成流)

Instead of matching "A to B" in a table, follow this 4-step creative synthesis:

```
[Vague Prompt] 
      │
      ▼
1. Deconstruct Semantic Vibe (Extract core metaphor, mood, energy)
      │
      ▼
2. Synthesize Design Palette & Typographic Contrast (Blend colors & pairing dynamically)
      │
      ▼
3. Structure Narrative & Grid (Lay out elements to match the conceptual flow)
      │
      ▼
4. Choreograph Dynamic Behavior (Overlay springs, skews, triggers based on user action)
```

---

## 1. Deconstructing the Semantic Vibe

Analyze the user's brief for emotional and physical metaphors:
- *Example 1*: "做个 AI Agent 落地页" 
  - **Metaphor**: Autonomy, flow, processing state, high intelligence, seamless action.
  - **Motion Intent**: continuous low-level ambient threads (flow), snappy data changes (processing), organic warp when hover (autonomy).
- *Example 2*: "做个很酷的个人主页"
  - **Metaphor**: Authorial presence, friction, memory, physical texture.
  - **Motion Intent**: heavy dragging inertia, paper textures, scroll skewing that deforms text (friction).

---

## 2. Dynamic Visual Synthesis (色彩与排版编排)

Do not copy palette presets blindly. Construct a custom visual identity using these rules:

### Custom Palette Generation
Define a triad that supports the metaphor:
1. **The Canvas (60%)**: Define the texture. Is it `#080808` matte lacquer, `#fcfbf9` unbleached linen paper, or a muted concrete gray?
2. **The Structural Ink (30%)**: High-contrast readable typography color.
3. **The Current/Accent (10%)**: A highly targeted color that flashes only on state change (e.g., interactive hover, loading progress).

### Typography Contrasts
Combine font weights to create hierarchy:
- Use a **High-Character Serif** or an **Ultra-Condensed Grotesque** for display/headline text.
- Use a **Strict Monospace** or **Clean Neo-Grotesque** for metadata, interface labels, and micro-copy.
- Keep the body font highly legible (Inter, system-sans) and never animate its line-height or letter-spacing.

---

## 3. Designing Bespoke Narrative Grids (版面结构)

Never stretch elements to fit a generic "Bento grid" unless the product is specifically about modular widgets.
Create layout containers that match the reading rhythm:
- **Asymmetric Tension**: Place a massive headline left-aligned, and push the supporting paragraph to the far right, separated by a thin, scroll-drawn line.
- **Overlapping Layers**: Let images overlap text containers slightly. Use negative margins to invite depth, then animate their z-index and translation speeds differently during scroll (parallax).

---

## 4. Choreographing Tactile Motion (动效与交互编排)

This is where the code becomes alive. Layer animations so they feel responsive and physics-driven:

### The Interaction Loop (Hover & Pointer)
- **Friction & Weight**: Use spring physics (high stiffness, low damping) for micro-interactions to make targets feel physical.
- **Cursor Tracking**: Don't just show a dot. Let the custom cursor shape-shift based on what it hovers over (e.g., expanding into a text tag, warping into a blurred liquid bubble).

### The Scroll Canvas (Scroll-linked)
- **Velocity Deform**: Bind CSS skews or scales to scroll velocity so that the layout physically distorts under the "g-force" of scrolling, then rebounds.
- **Curtain Reveal**: Use `clip-path` with staggered delays so sections reveal themselves like pages of a high-end magazine being turned.

---

## 5. Inventing the Signature Mechanic (每页一个签名交互，发明优先)

Derive the mechanic from the topic's own physics — every subject has a native
action nothing else has (咖啡:倾倒/研磨/蒸汽上升; 打字工具:击键/回车/墨水渗开;
天气 app:气压/凝结/风切). Then apply one or two generative operators:

| Operator | Move | Example seed |
|---|---|---|
| **直译物理** | Implement the subject's literal physical behavior as the interaction | 打字页面:每次滚轮像打字机回车,整页"咔"地行进一格 |
| **输入反转** | Swap what controls what — object drives cursor, page drives mouse feel | 鼠标不动物体,物体的"重心"拖着光标走 |
| **维度替换** | Map an input to an unexpected dimension: scroll→时间流速, mouse Y→重力方向, hover 时长→温度 | 停留越久,页面元素越"融化" |
| **介质想象** | Put the whole page inside a medium: 蜂蜜里/真空中/磁场中/水面倒影 | 所有 UI 元素带磁性,同极相斥 |
| **杂交** | Weld two unrelated primitives: 翻书×重力, 擦洗×音高, 钟摆×打字 | 序列帧擦洗但帧序由"心跳"节律推进 |
| **破坏规则** | Take one web convention (scroll 向下, hover 高亮) and violate it物理化地 | scroll 不滚动页面,而是给页面"充气" |

Rules:
- Generate 3 candidate mechanics via different operators, keep the one that is
  (a) not in the catalog, (b) implementable with handfeel.md physics, (c) 一句话能讲清
- The catalog below is the graveyard of used ideas — check against it, then diverge

### Used-Mechanics Graveyard (查重底线 — 撞车即弃，做完新的往里加)

| Mechanic | What it is | Topic temperament | Proven in |
|---|---|---|---|
| **Turnaround scrub** | Mouse X sweeps pre-rendered rotation frames, hard-cut flipbook; wheel flick spins it | Product hero, single-object showcase, "看这个东西" | phone hero + retro-console hero (2026-07) |
| **Stop-motion jitter** | Low-tick random micro offset/rotation held between re-rolls (11fps feel) | Handmade, toy-like, indie, claymation warmth | Retro-console hero |
| **Pendulum swing** | Loose spring rock with overshoot; wheel kicks angular impulse | Playful physical objects, hanging/floating things | Retro-console hero v1 |
| **Leap carousel** | Items travel a rising diagonal/arc with tangent-following attitude | Nature, food, anything that "moves through space" | Seafood hero |
| **Jelly wobble field** | Primary velocity feeds loose springs on every decoration; squash & stretch + residual jiggle | Underwater, organic, soft-body, liquid brands | Seafood hero decorations |
| **Depth-slice parallax** | One PNG sliced into part layers at real heights (preserve-3d) | Devices, machinery, layered illustration | Retro-console hero parts |
| **Fake-light hero** | Mouse-driven masked gradient highlight/shade on flat cutout | "3D-looking" product from one image | Retro-console hero, seafood hero |
| **Desk-toy physics** | Items sit with contact shadows; fast primary motion makes them hop with squash landing | Studio/workshop scenes, collections | Desk-toy studio scene |
| **Frame-scrub + full-page linkage** | Every layer (headline, blob, chrome) moves at a distinct depth gain off one scrub value | Any hero — this is what makes pages feel alive | All three |
| **Weave-in** | Scroll advances a weft line down a fixed loom canvas; cloth accumulates row by row behind a travelling shuttle, loose warp above the fell line, woven pattern below | Craft, manufacture, anything that is *made* rather than shown; binary/encoding stories | Jacquard scroll demo (2026-08) |
| **Erase-to-reveal** | A held pointer wipes a layer away *along the path the hand actually travelled*; let go and it draws itself back in | Archival, restoration, excavation, "what's underneath" | Heritage-ruins scrollytelling (2026-08) |
| **Verlet text curtain** | Copy hangs as independent vertical chains; scroll injects energy rather than position; the pointer parts it | Editorial, poetry, tactile typography | Editorial long-form page (2026-08) |
| **Traverse-a-world** | The page *is* a place you drive or walk through; sections are locations reached by travelling, not scroll offsets | Portfolio-as-journey, travelogue, a product line as a route | Driving-world portfolio + walkable island scene (2026-08) |
| **Sun-scroll room** | Scroll doesn't page — it moves a directional sun dawn→dusk over a 3D still-life; DOM text-shadows share the same sun via CSS vars; mouse = dim curator torch | Museum-quiet, sculptural, premium showcase | Sculptural product landing (2026-07) |
| **Sediment scroll** | Scroll lets one tank of stirred water settle: global agitation = 1−scrollP, first-order filtered so wheel flicks slosh and scrolling back up re-stirs; every element has a settle window over scrollP (heavy settles early, light drifts late) and lands at true rest (snap below a<0.002); pointer velocity stirs a local radius (repel + boost). Warm tint = turbid, cold = settled. Distinct from sun-scroll (state narrative → energy dissipation with reversal) and from frame-scrub linkage (depth-gain parallax → per-element amplitude decay to zero) | Focus/calm/clarity products, meditation, "chaos→order" narratives, anything whose promise is *less noise* | STILL focus landing (2026-08) |
| **Tuner-sweep dial** | Scroll maps to a radio frequency; static noise clears as lock approaches; detent spring clicks into stations; typography resolves out of blur/jitter at lock | Broadcast, archival, "signal out of noise" narratives | Frequency Museum case (2026-08) |
| **Hanging card chain** | Images strung on a Verlet chain pinned to the pointer; each card is corner-pinned between two nodes so it **bends**, not just rotates, as the chain curves | Work index, gallery, any "the cursor carries the content" browse | Card-chain study (2026-08) — `pattern-recipes.md` #17+#18 |
| **Slack string readout** | A curve with an exact anchor and an exact data-driven endpoint, carrying more length than the straight path so the body must sag; the datum is spring-held *stiff* while the body is deliberately elastic. Grabbable at either end. Distinct from the hanging card chain (content strung on a chain → the chain IS the readout) and from the verlet text curtain (independent hanging strands → one strand between two meaningful points) | Instruments, gauges, anything whose value is real but whose *feel* should read as soft or lagging | String-clock case (2026-09) — `pattern-recipes.md` #19 |
| **Cumulative emergence** | Content dealt onto the ground on a fixed tick (167 ms, with skipped ticks) until the count itself is the composition — **with no entrance animation at all**: the page is still 88 % of the time and its whole motion budget is *when* things appear. Random placement with heavy overlap, made legible by z-order = arrival order; a hard DOM cap with FIFO retirement while the tally keeps climbing; a foreground panel that stays readable **through** the pile rather than being carved out of it. Distinct from a staggered entrance (that reveals a known set, and eases) and from frame-scrub linkage (arrivals add members, not position) | Inbound volume as the proof — messages, activity, submissions, archives; anything whose promise is "it keeps coming" | Quote-wall case (2026-09) — `pattern-recipes.md` #20 |


## 6. Asset Prompt Patterns (需要用户生成图片素材时)

- **Sprite sheet turnaround**: strict 2×4 grid, same object/scale/height per cell,
  equal yaw steps, flat solid contrasting bg, no labels/grid lines. Expect 2–3
  near-duplicate frames — curate a monotonic subset, drop the head-on frame
  (it breaks the 3D illusion), auto-straighten via PCA, sort by silhouette asymmetry.
- **Object set**: single row, evenly spaced, none touching, same style/scale,
  solid bg — slice by alpha-gap segmentation, never fixed fractions.
- **Single hero render**: slight 3/4 angle, baked form shading (AO, gradient),
  NO cast shadow on bg (the page makes the dynamic one), solid contrasting bg.


---

## Output Contract (The Creative Report)

After building the page, summarize your decisions. Do not list code files. Explain the **why** of your orchestration:

1. **The Conceptual Metaphor**: What mood did you extract from the brief?
2. **Visual Synthesis**: Why did you choose this canvas color and typographic pairing?
3. **Interactive Choreography**: What physical triggers (springs, scroll velocity, drag inertia) did you implement to bring the page to life?
