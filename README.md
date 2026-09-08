# motion-web

> **Build motion-first, high-touch creative websites on vanilla Three.js / Canvas 2D / WebGL / CSS. A Claude Agent Skill with real-world physics, token discipline, and automated headless verification.**  
> **动效即材质：面向 Agent 与前端工程师的高手感交互动效体系。内置 7 大完整案例、物理阻尼求解器、排版规范与自动化 Headless 验证判据。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Type](https://img.shields.io/badge/Type-Agent%20Skill-333.svg)](SKILL.md)
[![Cases](https://img.shields.io/badge/Cases-7%2F7%20PASS-brightgreen.svg)](cases/)
[![Platform](https://img.shields.io/badge/Platform-Vanilla%20JS%20%7C%20Canvas%20%7C%20WebGL2-orange.svg)](cases/)

---

[English](#english) | [中文说明](#chinese)

---

<a name="english"></a>
## English

`motion-web` is a code-first, motion-driven creative web engineering skill. It treats **motion as the core material of the interface** rather than after-the-fact decoration. 

Every case and blueprint enforces real physical laws (spring-damper systems, anisotropic forces, stepped jitter, causal ecosystems) and zero placeholder code. All cases come with automated Playwright headless verification oracles (`verify_case.py`) to mathematically prevent AI slop, synthetic drifts, and dead interactions.

### 🎬 Promo Reel

![motion-web 15s promo](assets/hero.gif)

> 🎥 Full 60fps stereo audio version: [`assets/motion-web-15s.mp4`](assets/motion-web-15s.mp4)

---

### 🌟 Seven Interactive Cases (All 100% Runnable & Verified)

All cases are single-file HTML pages that run standalone without build tools or external CDN dependencies. Every case passes strict assertions in `verify_case.py`.

<table>
  <tr>
    <td width="50%" align="center">
      <b>01 · string-clock (DROOP!)</b><br/>
      <img src="assets/cases/string-clock.gif" width="100%" /><br/>
      <sub>Softbody clock hands with absolute endpoint accuracy</sub><br/>
      <a href="cases/string-clock/index.html">▶ Live Page</a> | <a href="cases/string-clock/README.md">📖 Breakdown</a>
    </td>
    <td width="50%" align="center">
      <b>02 · ink-crowd (Drawn, Not Rendered)</b><br/>
      <img src="assets/cases/ink-crowd.gif" width="100%" /><br/>
      <sub>Procedural WebGL2 ink crowd, depth-discontinuity contours</sub><br/>
      <a href="cases/ink-crowd/index.html">▶ Live Page</a> | <a href="cases/ink-crowd/README.md">📖 Breakdown</a>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <b>03 · press-stack (Lathe)</b><br/>
      <img src="assets/cases/press-stack.gif" width="100%" /><br/>
      <sub>Sticky stacked vinyls, spring overshoot, zero bitmaps</sub><br/>
      <a href="cases/press-stack/index.html">▶ Live Page</a> | <a href="cases/press-stack/README.md">📖 Breakdown</a>
    </td>
    <td width="50%" align="center">
      <b>04 · wheel-rail (Equal Length)</b><br/>
      <img src="assets/cases/wheel-rail.gif" width="100%" /><br/>
      <sub>Wheel-driven curved rail, 3 depth planes, 7× parallax</sub><br/>
      <a href="cases/wheel-rail/index.html">▶ Live Page</a> | <a href="cases/wheel-rail/README.md">📖 Breakdown</a>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <b>05 · toy-flipbook (TOYBOX)</b><br/>
      <img src="assets/cases/toy-flipbook.gif" width="100%" /><br/>
      <sub>Hard-cut yaw frames via spring round + 11Hz stepped jitter</sub><br/>
      <a href="cases/toy-flipbook/index.html">▶ Live Page</a> | <a href="cases/toy-flipbook/README.md">📖 Breakdown</a>
    </td>
    <td width="50%" align="center">
      <b>06 · char-curtain (Curtain)</b><br/>
      <img src="assets/cases/char-curtain.gif" width="100%" /><br/>
      <sub>Cloth as independent Verlet ropes, anisotropic pointer push</sub><br/>
      <a href="cases/char-curtain/index.html">▶ Live Page</a> | <a href="cases/char-curtain/README.md">📖 Breakdown</a>
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <b>07 · lyre-crows (The Lyre & the Ink Crows)</b><br/>
      <img src="assets/cases/lyre-crows.gif" width="60%" /><br/>
      <sub>Causal ecosystem: plucked strings release words, ink crows pursue and rewrite tails</sub><br/>
      <a href="cases/lyre-crows/index.html">▶ Live Page</a> | <a href="cases/lyre-crows/README.md">📖 Breakdown</a>
    </td>
  </tr>
</table>

---

### 📦 Installation

#### As Claude Code Skill
```bash
git clone https://github.com/feitangyuan/motion-web.git ~/.claude/skills/motion-web
```

#### As Codex / Antigravity Skill
```bash
git clone https://github.com/feitangyuan/motion-web.git ~/.agents/skills/motion-web
```

---

### 🧪 Automated Verification

Verify all 7 cases with Playwright headless oracles:
```bash
# Verify all cases
python3 scripts/verify_case.py cases/string-clock/index.html  --strings
python3 scripts/verify_case.py cases/ink-crowd/index.html     --layer webgl --follow
python3 scripts/verify_case.py cases/press-stack/index.html   --stack
python3 scripts/verify_case.py cases/wheel-rail/index.html    --rail
python3 scripts/verify_case.py cases/toy-flipbook/index.html  --min-shapes 1 --flipbook
python3 scripts/verify_case.py cases/char-curtain/index.html  --min-shapes 1 --curtain
python3 scripts/verify_case.py cases/lyre-crows/index.html    --min-shapes 1 --lyre
```

Launch the local interactive gallery:
```bash
python3 -m http.server 8899 -d cases/
# Open http://localhost:8899
```

---

<a name="chinese"></a>
## 中文说明

`motion-web` 是一个面向 Agent 与前端开发者的动效与创意网页工程体系。它坚持**动效即材质（Motion is the Material）**，拒绝浮于表面的装饰性动画，通过真实的物理模拟、严苛的排版与设计系统约束，交付兼具审美手感与生产级代码质量的创意交互页面。

### 核心设计原则

1. **拒绝 AI 塑料感（Anti-AI-Slop）**：
   - 严禁任何无意义的 `opacity: 0 -> 1` 或线性匀速缓动；
   - 采用真实的二阶弹簧阻尼系统（Spring-damper）、各向异性推力与定格阶梯抖动（Stepped Jitter）；
   - 每一个动作都有阻尼、有动量、有过冲回弹。
2. **机械级验收地板（Automated Verification Floor）**：
   - 每个案例均配备专属的无头 Chromium 探针（Oracle），自动模拟真实指针扫掠、滚轮事件与惯性衰减；
   - 只有通过数学断言（位移比、形变误差、回弹锚点、状态收敛）的代码才允许交付。
3. **零外部网络依赖（Self-Contained）**：
   - 案例与模板均采用子集化内联字体与原生 WebGL2 / Canvas 2D 绘制，断网状态下完整可运行。

---

### 7 大实测案例一览

| 案例 | 机制核心 | 技术栈 | 验收判据 |
|---|---|---|---|
| [`string-clock`](cases/string-clock/) | **软体绳索但端点精确**：松弛弹性绳指针，尖端硬弹簧确保读数绝对准确，笔画在撒谎而时间没有。 | Canvas 2D + rAF | `--strings` |
| [`ink-crowd`](cases/ink-crowd/) | **墨线手绘渲染层**：620 个胶囊体实例进 MRT 几何与深度缓冲，全屏 Pass 仅从深度不连续处勾勒墨线。 | WebGL2 (MRT, G-Buffer) | `--layer webgl --follow` |
| [`press-stack`](cases/press-stack/) | **粘性叠层**：九屏各自 sticky top:0，后屏滚动骑压前屏；Canvas 纯矢量手绘唱片封套。 | DOM + Canvas 2D | `--stack` |
| [`wheel-rail`](cases/wheel-rail/) | **输入驱动的轨道编排**：拦截 wheel 缓动平移轨道，三层视差平面（景深比 7×），沿 SVG 曲线钉住标签。 | DOM + Inline SVG | `--rail` |
| [`toy-flipbook`](cases/toy-flipbook/) | **零 DCC 深度旋转**：4 张预渲染 Yaw 角度帧，弹簧位移通过 Math.round 硬切，11Hz 阶梯抖动。 | Canvas 2D / DOM + rAF | `--min-shapes 1 --flipbook` |
| [`char-curtain`](cases/char-curtain/) | **绳排非网布**：576 个字符悬挂在 24 条独立 Verlet 绳上，列间零水平约束，指针掠过如撩开帘幕。 | Canvas 2D + Verlet | `--min-shapes 1 --curtain` |
| [`lyre-crows`](cases/lyre-crows/) | **因果生态闭环**：拨弦抖出词句，墨鸦转向猎食并改写自身尾迹；转向钳制加速度保留转弯半径。 | Canvas 2D + Steering | `--min-shapes 1 --lyre` |

---

### 目录结构

```
motion-web/
├── SKILL.md                 # Agent 核心执行规范与工作流定义
├── LICENSE                  # MIT 开源许可证
├── README.md                # 规范与展示文档
│
├── cases/                   # 7 大完整、可运行、可验证的交互案例
│   ├── index.html           # 案例画廊入口
│   ├── AUTHORING.md         # 案例开发与判据编写规范
│   ├── string-clock/        # 软体弹性绳索时钟
│   ├── ink-crowd/           # 原生 WebGL2 墨线群集
│   ├── press-stack/         # 粘性叠层唱片封面
│   ├── wheel-rail/          # 滚轮驱动视差轨道
│   ├── toy-flipbook/        # 硬切翻页与阶梯抖动
│   ├── char-curtain/        # 独立 Verlet 绳排门帘
│   └── lyre-crows/          # 因果生态文字猎鸟
│
├── references/              # 深入规范：物理阻尼、排版尺度、组件方言、生产级打磨
│   ├── physics.md           # 弹簧阻尼模型与数学求解
│   ├── components.md        # 组件方言与实测基线
│   ├── page-design.md       # 字号梯次与版面比例
│   ├── page-blueprints.md   # 页面架构与叙事蓝图
│   └── production-polish.md # 生产级细节自检清单
│
├── scripts/                 # 自动化无头测量与验收工具链
│   ├── verify_case.py       # 案例 Headless Oracle 验收脚本
│   ├── measure_structure.py # 页面静态结构与 Token 提取
│   ├── measure_churn.py     # 交互变化率与过渡状态测量
│   ├── measure_frames.py    # 逐帧逆向测量工具
│   └── subset_fonts.py      # 字体按需子集化内联工具
│
└── assets/                  # 演示动图、缩略图与宣传视频
    ├── hero.gif
    ├── motion-web-15s.mp4
    └── cases/               # 各案例交互演示动图与快照
```

---

### License

本项目采用 [MIT License](LICENSE) 开源协议。项目内嵌入的第三方开源字体子集保留原各自开源许可（SIL Open Font License）。
