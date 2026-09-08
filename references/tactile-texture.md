# Web Tactile Texture Specification & Technical Stack

To create high-end premium web experiences, motion must be paired with **tactile textures (触觉质感)**. 

This document defines the implementation specifications for the complete "Texture Tech Stack" including SVG Filters, CSS Houdini, Canvas buffering, and offscreen threads.

---

## 1. SVG Filter Engine (粘滞流体与置换噪点)

SVG filters run on the browser's native renderer. They allow you to apply heavy organic distortion and blending to standard DOM elements (like text and buttons) without WebGL.

### Recipe A: The Viscous Liquid / Gooey Filter (液态融合粘滞)
Causes close or overlapping DOM elements to merge seamlessly like mercury drops. Useful for navigation links, floating buttons, and card joints.

```xml
<!-- Place this SVG anywhere in the DOM (hidden) -->
<svg style="visibility: hidden; position: absolute;" width="0" height="0">
  <defs>
    <filter id="gooey-liquid">
      <!-- 1. Blur the borders of elements to make them bleed into each other -->
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
      <!-- 2. Apply high alpha threshold to sharpen the blurred overlap into a liquid bridge -->
      <feColorMatrix in="blur" mode="matrix" 
        values="1 0 0 0 0  
                0 1 0 0 0  
                0 0 1 0 0  
                0 0 0 19 -9" result="goo" />
      <!-- 3. Blend original sharp graphic on top of the liquid shape -->
      <feComposite in="SourceGraphic" in2="goo" operator="atop" />
    </filter>
  </defs>
</svg>
```
CSS Usage:
```css
.button-container {
  filter: url('#gooey-liquid');
}
```

### Recipe B: Fractal Displacement Map (分形几何撕裂/扭曲)
Uses SVG Perlin noise to warp the borders of an image or text element, giving it a torn paper or fluid wave border.

```xml
<svg style="visibility: hidden; position: absolute;" width="0" height="0">
  <defs>
    <filter id="organic-distortion">
      <!-- Generate high-octave fractal noise -->
      <feTurbulence type="fractalNoise" baseFrequency="0.015" numOctaves="4" result="noise" />
      <!-- Distort the shape using the generated noise texture -->
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="30" xChannelSelector="R" yChannelSelector="G" />
    </filter>
  </defs>
</svg>
```

---

## 2. CSS Houdini Paint API (多线程程序噪声)

Houdini runs on an independent paint thread. It allows you to draw dynamic textures (like high-res film grain) procedurally, avoiding huge image assets and keeping the main JS thread free for interactions.

### The Procedural Grain Worklet (`grain-worklet.js`)
```javascript
// Register the paint worklet
class GrainPaint {
  static get inputProperties() {
    return ['--grain-density', '--grain-opacity', '--grain-scale'];
  }
  
  paint(ctx, geom, properties) {
    const density = parseFloat(properties.get('--grain-density').toString()) || 0.3;
    const opacity = parseFloat(properties.get('--grain-opacity').toString()) || 0.08;
    const scale = parseInt(properties.get('--grain-scale').toString()) || 1;
    
    const w = geom.width;
    const h = geom.height;
    
    // Fill background color (transparency allows layer stack)
    ctx.clearRect(0, 0, w, h);
    
    for (let x = 0; x < w; x += scale) {
      for (let y = 0; y < h; y += scale) {
        if (Math.random() < density) {
          const val = Math.floor(Math.random() * 255);
          ctx.fillStyle = `rgba(${val}, ${val}, ${val}, ${opacity})`;
          ctx.fillRect(x, y, scale, scale);
        }
      }
    }
  }
}

registerPaint('grain-texture', GrainPaint);
```

### Main Thread Registration
```javascript
if ('paintWorklet' in CSS) {
  CSS.paintWorklet.addModule('grain-worklet.js');
}
```

### CSS Binding
```css
.card {
  --grain-density: 0.45;
  --grain-opacity: 0.06;
  --grain-scale: 1;
  background-image: paint(grain-texture);
}
```

---

## 3. OffscreenCanvas & Threaded Render (多线程异步渲染)

WebGL and heavy canvas animations can block the main thread, dropping frames during page scrolling. Moving the render loops into a **Web Worker** prevents blocking.

```javascript
// main.js — Transfer control to worker
const canvas = document.querySelector('#webgl-canvas');
const offscreen = canvas.transferControlToOffscreen();

const worker = new Worker('renderer-worker.js');
worker.postMessage({
  type: 'init',
  canvas: offscreen,
  width: canvas.clientWidth,
  height: canvas.clientHeight,
  dpr: Math.min(window.devicePixelRatio, 2.0)
}, [offscreen]); // Transfer ownership of the OffscreenCanvas

// Listen to resize and post updates to worker
window.addEventListener('resize', () => {
  worker.postMessage({
    type: 'resize',
    width: canvas.clientWidth,
    height: canvas.clientHeight
  });
});
```

---

## 4. Canvas Pattern Buffering (高性能静态噪点)

For full-page static textures, rendering noise per frame on canvas wastes CPU. The standard is to draw a tiny tile on an off-screen canvas once, and loop it as a CSS background.

```javascript
// generate-noise-tile.js
export function createNoisePattern(size = 128, opacity = 0.04) {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');
  
  const imgData = ctx.createImageData(size, size);
  const data = imgData.data;
  
  for (let i = 0; i < data.length; i += 4) {
    const val = Math.floor(Math.random() * 255);
    data[i] = val;     // R
    data[i+1] = val;   // G
    data[i+2] = val;   // B
    data[i+3] = Math.floor(Math.random() * 255 * opacity); // A
  }
  
  ctx.putImageData(imgData, 0, 0);
  return canvas.toDataURL(); // Return base64 png pattern
}

// Usage: Set as body background
// document.body.style.backgroundImage = `url(${createNoisePattern(128, 0.05)})`;
```

---

## 5. High-Resolution Display Rules (高分屏与防抖)

- **Retina Defenses**: Always verify render size vs display size to avoid blur on high-DPI screens.
```javascript
function resizeCanvasToDisplaySize(canvas, dprLimit = 2.0) {
  const dpr = Math.min(window.devicePixelRatio, dprLimit);
  const width  = Math.floor(canvas.clientWidth  * dpr);
  const height = Math.floor(canvas.clientHeight * dpr);
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width  = width;
    canvas.height = height;
    return true;
  }
  return false;
}
```
- **Debounced Resize**: Do not re-allocate canvas memory on every pixel change during browser resize. Wait for resize end (150ms debounce) before updating buffers.
