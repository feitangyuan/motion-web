# Scene Streaming — 大场景怎么装得下

A scroll scene with hundreds of plates cannot hold them all. The machinery below is what makes a long
image-plane piece run on a laptop: activate by screen window, upload in slices, scan cooperatively,
dispose completely.

> Documented case: SBS *The Boat* (2015) — 222 hand-painted illustrations, 59 animated sequences, one
> continuous scroll, three.js r70. Numbers below are read off the shipped bundle.
> Credits: art Matt Huynh, development Matt Smith / SBS.

---

## §1 Activate by screen window, not by index

Each display object registers a window in units of **screens**:

```js
activeBetweenScreenPosition = { min: -3, max: 4.5 }   // default
```

A cached screen position per object is compared against it every frame. Entering the window creates the
object's GL/CSS children, starts its loads, and adds it to the container; leaving disposes and removes.

Two things to copy:

- **The window is asymmetric — 4.5 screens ahead, 3 behind.** Loading is a forward bet; the trailing side
  only needs to cover a scroll-back flick.
- **It is per object, overridable.** A cheap caption and a 4096-wide backdrop should not share a policy.

The state lives in one flag with a setter that does the work:

```js
set active(v) {
  if (v && !this._active) { this.createActiveModeObjects(); this.load(); this.draw(); this.update() }
  else if (!v && this._active) { this.disposeActiveModeObjects() }
  this._active = v
}
```

Everything downstream — hit testing, triggers, per-frame updates — iterates only active objects, so the
window is also the performance budget.

---

## §2 Scan cooperatively — yield inside the loop, resume next frame

With hundreds of registered objects, even the *check* is too much for one frame. The scan keeps a cursor
and gives up its slice:

```js
flagActive() {
  if (this.yieldedAtIndex >= this.lookup.length - 1) this.yieldedAtIndex = 0
  const t0 = Date.now()
  for (let i = this.yieldedAtIndex; i < this.lookup.length; i++) {
    /* … activate / deactivate … */
    this.yieldedAtIndex = i
    if (Date.now() - t0 >= 1000 / 240) return      // ~4.17 ms budget, resume here next frame
  }
}
```

The whole list gets visited over a few frames. **Bounded work per frame beats a correct-but-spiky pass** —
and because the window is 7.5 screens wide, being a few frames late costs nothing.

---

## §3 DOM mutations are not frame work — batch and throttle them

Adding or removing a `CSS3DObject` is far more expensive than adding a mesh. So DOM changes are queued
during the scan and drained on a throttle, **much slower than the frame rate**:

```js
processCSSTasks = throttle(processCSSTasks, isDesktop ? 500 : 2500)
```

Half a second on desktop, two and a half on mobile. The GL side reacts immediately; the DOM side catches
up. With a 7.5-screen window there is room for that lag.

---

## §4 Dispose everything, and cache by URL

three.js will not collect GPU resources for you. One dispose path that releases all three, plus a
URL-keyed texture cache so repeated art loads once:

```js
dispose() {
  this.geometry.dispose(); this.material.dispose(); this.texture.dispose()
  if (this.cacheTexture) removeTextureFromCache(this.texture)
  this.geometry = this.material = this.texture = this.mesh = this._img = null
  this.disposed = true
}
```

Note the ordering hazard: an image can finish loading **after** its object was disposed. Guard the load
callback with the `disposed` flag or you will assign a texture to a dead mesh — a leak that only shows up
when someone scrolls fast.

---

## §5 Slice a large plate instead of uploading it whole

A single big texture upload blocks the main thread and can exceed a device's max texture size. Split it:

```js
widthSegments = 6, heightSegments = 6            // 36 sub-planes
drawNext() {                                      // called via setTimeout(…, 1), one slice per turn
  const c = document.createElement('canvas')      // crop the slice out of the loaded <img>
  ctx.drawImage(img, n*iw, o*ih, iw, ih, 0, 0, iw, ih)
  subImage.img = c                                // → its own texture
  subImage.mesh.position.set(n*sw - 0.5*W + 0.5*sw, -(o*sh - 0.5*H + 0.5*sh), 0)
}
```

Each slice becomes its own plane with its own texture, positioned back into the original rectangle. The
slices are produced across turns of the event loop rather than in one pass, so the upload cost is spread
over several frames.

Keep `opacity` and `transparent` as properties on the parent that fan out to every slice — otherwise a
fade will tear the plate into 36 visible tiles.

---

## §6 Stream audio the same way

The same lifecycle applies to sound: create the instance when it becomes audible, destroy it when it
stops. *The Boat*'s ambience layer holds two independent gain factors and multiplies them:

```js
volumeMixed = volumeIn * volumeOut                       // fade-in × fade-out, set independently
if (!instance && volumeMixed > 0) { instance = get(id); instance.load() }
else if (instance && volumeMixed <= 0) { instance.pause(); instance = null }
```

Two factors rather than one means the entering and leaving envelopes can be authored by different
triggers without either having to know about the other. Updates are throttled to 30 fps — nobody hears
the difference, and it stops a gain write per frame per layer.

---

## §7 Checklist

- [ ] Every heavy object has a screen-position window, biased forward
- [ ] Activation creates **and** disposes; nothing is merely hidden
- [ ] The activation scan is time-budgeted and resumes from a cursor
- [ ] DOM/CSS3D mutations batched and throttled well below frame rate
- [ ] `geometry` / `material` / `texture` disposed together; load callbacks guarded by a `disposed` flag
- [ ] Textures cached by URL when the same art appears more than once
- [ ] Oversized plates sliced and uploaded across frames, with opacity fanned out to the slices
- [ ] Audio instances created and destroyed by audibility, not held open for the whole piece
