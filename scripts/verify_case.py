#!/usr/bin/env python3
"""
verify_case.py — acceptance floor for a case (or any built page).

A case's README claims it was verified. This is the thing that makes the claim
re-runnable; without it the claim rots the first time anyone edits the file.

Usage:
  python3 scripts/verify_case.py cases/press-stack/index.html --stack
  python3 scripts/verify_case.py cases/wheel-rail/index.html --rail
  python3 scripts/verify_case.py http://localhost:5173 --no-js-expected

Always checks (the floor every page owes — baseline-ui.md, production-polish.md):
  console/page errors, horizontal overflow at 320/375/414/768/1440, one <h1>,
  lang, landmarks, distinct section shapes >= 3 (design-slop.md A3), the
  type-scale ratio display/body >= 4 (page-design.md §2), no referenced-but-
  undefined custom property, a body that paints its own ground, and one real
  wheel + one real hover that change something.

--strings drives a REAL pointer at a slack-string control and asserts the
data-driven endpoint stays exact while the body still sags.

Two of these catch the same species of silent failure: CSS that is discarded
without logging anything.
  * clamp(2.75rem,1.1rem+6.6vw,7.5rem) — the + needs whitespace, or the whole
    declaration is dropped and the element falls back to a UA default. The
    type-scale ratio is what notices.
  * one stray */ inside a comment closes it early; the parser then eats the
    NEXT rule block as the garbage rule's body. A swallowed :root{} leaves
    every var() undefined and the page renders on UA defaults. The dead-token
    and transparent-ground checks are what notice (cases/string-clock, 坑 #1).
"""
import argparse, math, sys
from pathlib import Path

WIDTHS = (320, 375, 414, 768, 1440)


def to_url(target):
    return target if target.startswith("http") else "file://" + str(Path(target).resolve())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--no-js-expected", action="store_true", help="assert 0 <script> tags")
    ap.add_argument("--detent", action="store_true",
                    help="check a detent/snap control lands exactly and reaches every slot")
    ap.add_argument("--beats", action="store_true",
                    help="sweep the scroll axis and report dead beats (needs __probe.seek/tracks)")
    ap.add_argument("--strings", action="store_true",
                    help="slack-string hands: tip still tells the time AND the curve still sags")
    ap.add_argument("--layer", choices=["dom", "svg", "canvas2d", "webgl"],
                    help="assert the render layer the case README declares. Implies the "
                         "web-font gate: a case authored under render-layer.md may not ship "
                         "on the system stack without saying so in the README.")
    ap.add_argument("--draws-own-type", action="store_true",
                    help="with --layer: the page draws its own letterforms (ink-crowd does), "
                         "so 0 @font-face is correct rather than a default.")
    ap.add_argument("--stack", action="store_true",
                    help="a sticky stack on native scroll: every screen must pin at top 0 "
                         "while window.scrollY keeps advancing, the type wipe must show a "
                         "gradient rather than a switch, and unlit type must stay readable")
    ap.add_argument("--rail", action="store_true",
                    help="the wheel is hijacked: it must move a rail while window.scrollY "
                         "stays 0, the rail must lag rather than snap, and the pointer must "
                         "move far layers further than near ones")
    ap.add_argument("--curtain", action="store_true",
                    help="a hanging character cloth: a real pointer must PART it "
                         "sideways while barely disturbing it vertically, and the "
                         "strings must stay at their rest length while it does.")
    ap.add_argument("--lyre", action="store_true",
                    help="a causal ecology: strumming must RELEASE words, the "
                         "release must stay RATE LIMITED under abuse, hunters must "
                         "close on what was released, and a capture must rewrite "
                         "the hunter's own tail.")
    ap.add_argument("--flipbook", action="store_true",
                    help="stop-motion turnaround: the cut must be HARD (one frame at "
                         "opacity 1, no in-between) while the scrub stays CONTINUOUS "
                         "(a real sweep visits every frame in order, skipping none).")
    ap.add_argument("--follow", action="store_true",
                    help="pointer-led crowd: aim at several points across the canvas and "
                         "require the centroid to CLOSE ON the aim from every one of them. "
                         "A counter that ticks is not evidence that anything walked.")
    ap.add_argument("--beat-samples", type=int, default=140)
    ap.add_argument("--max-dead", type=float, default=8.0,
                    help="longest allowed dead run, as %% of total scroll")
    ap.add_argument("--min-ratio", type=float, default=4.0)
    ap.add_argument("--min-shapes", type=int, default=3)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright
    url = to_url(args.target)
    fails = []

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(url); pg.wait_for_timeout(600)
        print("errors:", errs or "none")
        if errs: fails.append("console/page errors")

        floor = {}
        for w in WIDTHS:
            pg.set_viewport_size({"width": w, "height": 860}); pg.wait_for_timeout(150)
            floor[w] = pg.evaluate("()=>document.documentElement.scrollWidth-innerWidth")
        print("h-overflow:", floor)
        if any(v > 1 for v in floor.values()): fails.append("horizontal overflow")
        pg.set_viewport_size({"width": 1440, "height": 900}); pg.wait_for_timeout(250)

        ty = pg.evaluate("""()=>{const body=parseFloat(getComputedStyle(document.body).fontSize);
          let max=0,el=null;
          for(const e of document.querySelectorAll('*')){
            if(!e.textContent.trim()||e.children.length) continue;
            const f=parseFloat(getComputedStyle(e).fontSize);
            if(f>max){max=f; el=e.className||e.tagName;}}
          return {body,display:Math.round(max),el,ratio:+(max/body).toFixed(1)};}""")
        print("type scale:", ty)
        if ty["ratio"] < args.min_ratio: fails.append(f"type ratio {ty['ratio']} < {args.min_ratio}")

        shapes = pg.evaluate("""()=>{const S=[...document.querySelectorAll('section')];
          const key=s=>{const cs=getComputedStyle(s);
            const cols=cs.gridTemplateColumns.split(' ').filter(Boolean).length;
            const h=s.querySelector('h1,h2,h3');
            return `${cols}|${h?getComputedStyle(h).textAlign:'-'}|${cs.backgroundColor}`;};
          return {sections:S.length, distinct:new Set(S.map(key)).size};}""")
        print("sections:", shapes)
        if shapes["sections"] >= args.min_shapes and shapes["distinct"] < args.min_shapes:
            fails.append(f"only {shapes['distinct']} distinct section shapes")

        # A stylesheet that fails to parse does not error — the parser recovers by
        # swallowing whatever comes next, which is usually the :root token block.
        # Every var() then resolves to nothing and the page silently renders on UA
        # defaults. Measured 2026-09-01: one stray `*/` inside a banner comment ate
        # an entire :root{} and the page still passed every other check here.
        tok = pg.evaluate("""()=>{
          const names=new Set();
          for(const sh of document.styleSheets){
            let rules; try{rules=sh.cssRules}catch(e){continue}
            for(const r of rules||[]) for(const m of (r.cssText||'').matchAll(/var\\(\\s*(--[\\w-]+)/g)) names.add(m[1]);
          }
          const root=getComputedStyle(document.documentElement);
          const dead=[];
          for(const n of names){
            if(root.getPropertyValue(n).trim()) continue;
            let found=false;
            for(const el of document.querySelectorAll('*')){
              if(getComputedStyle(el).getPropertyValue(n).trim()){found=true;break}}
            if(!found) dead.push(n);
          }
          return {referenced:names.size, dead,
                  ground:getComputedStyle(document.body).backgroundColor};}""")
        print("tokens:", {k: v for k, v in tok.items() if k != "dead"},
              "dead:", tok["dead"] or "none")
        if tok["dead"]:
            fails.append(f"custom properties referenced but never defined: {tok['dead']} "
                         f"(a swallowed rule block? check for a stray */ in a comment)")
        if tok["ground"] == "rgba(0, 0, 0, 0)":
            fails.append("body background is transparent — the page paints no ground of its own")

        page = pg.evaluate("""()=>({h1:document.querySelectorAll('h1').length,
          lang:document.documentElement.lang||null,
          desc:!!document.querySelector('meta[name=description]'),
          title:document.title.length,
          landmarks:['header','main'].filter(t=>document.querySelector(t)).length,
          scripts:document.querySelectorAll('script').length})""")
        print("page:", page)
        if page["h1"] != 1: fails.append(f"{page['h1']} <h1> (must be exactly 1)")
        if not page["lang"]: fails.append("no lang on <html>")
        if args.no_js_expected and page["scripts"]: fails.append("expected zero <script> tags")

        if args.beats:
            if not pg.evaluate("()=>!!(window.__probe && __probe.seek && __probe.tracks)"):
                fails.append("--beats given but __probe.seek/tracks is missing")
            else:
                S = args.beat_samples
                series = []
                for i in range(S):
                    pg.evaluate("(p)=>__probe.seek(p)", i/(S-1))
                    pg.wait_for_timeout(24)   # let the scroll timeline resolve
                    series.append(pg.evaluate("()=>__probe.tracks()"))

                # flatten each track into one scalar series
                def scalars(name):
                    out = []
                    for s_ in series:
                        v = s_[name]
                        out.append(v if isinstance(v, (int, float))
                                   else v["o"] * 200 + abs(v["x"]) + abs(v["y"]))
                    return out
                names = list(series[0].keys())
                norm = {}
                for n in names:
                    v = scalars(n); lo, hi = min(v), max(v)
                    rng = (hi - lo) or 1.0
                    norm[n] = [(x - lo) / rng for x in v]

                eps = 0.004                      # per-step change below this = flat
                dead = []
                for i in range(1, S):
                    mx = max(abs(norm[n][i] - norm[n][i-1]) for n in names)
                    dead.append(mx < eps)
                # longest consecutive run of dead steps
                best = run = 0; start = best_start = 0
                for i, d in enumerate(dead):
                    if d:
                        if run == 0: start = i
                        run += 1
                        if run > best: best, best_start = run, start
                    else:
                        run = 0
                pct = best / len(dead) * 100
                at  = best_start / len(dead) * 100
                moving = {n: round(sum(abs(norm[n][i]-norm[n][i-1]) for i in range(1,S)), 2)
                          for n in names}
                print(f"beats: tracks={names}")
                print(f"       total travel per track (normalised): {moving}")
                print(f"       longest dead run = {pct:.1f}% of scroll, starting at {at:.0f}%")
                if pct > args.max_dead:
                    fails.append(f"dead beat: {pct:.1f}% of scroll with no track moving "
                                 f"(starts at {at:.0f}%)")
                flat = [n for n, v in moving.items() if v < 0.5]
                if flat: fails.append(f"track(s) that never move: {flat}")
                pg.evaluate("()=>__probe.seek(0)")

        # ── real-input smoke test ────────────────────────────────────────
        # Everything else here can be driven through __probe, which bypasses the
        # event handlers entirely. A dial whose wheel handler was sign-inverted
        # and swallowed page scroll passed every probe-driven check. So: send
        # ONE real wheel and ONE real hover and require the page to react.
        # The signature has to cover more than computed style: a page whose hover
        # lives in a canvas, or shows up as a changed readout, reacted just as
        # much as one that moved a div. Both used to read as "nothing happened".
        sig = """()=>{const b=document.body;
          const vis=[...document.querySelectorAll('body *')].slice(0,400)
            .map(e=>{const c=getComputedStyle(e);
              return c.transform+'|'+c.opacity+'|'+c.backgroundColor;}).join(';');
          const txt=(b.innerText||'').replace(/\\s+/g,' ');
          return Math.round(scrollY)+'#'+vis.length+'#'+vis+'#'+txt;}"""
        before = pg.evaluate(sig)
        pg.mouse.move(720, 450); pg.wait_for_timeout(120)
        pg.mouse.wheel(0, 400); pg.wait_for_timeout(700)
        after_wheel = pg.evaluate(sig)
        # first HITTABLE candidate: an element with pointer-events:none can never
        # receive a hover, so picking it guarantees a false "nothing happened".
        target = None
        for cand in pg.query_selector_all("a[href], button, [role=option], .row, .card, "
                                          "summary, canvas, [data-hover]"):
            try:
                ok = cand.evaluate("e=>{const c=getComputedStyle(e),r=e.getBoundingClientRect();"
                                   "return c.pointerEvents!=='none' && c.visibility!=='hidden' "
                                   "&& r.width>4 && r.height>4;}")
            except Exception:
                ok = False
            if ok:
                target = cand; break
        hovered = before
        if target:
            try:
                target.hover(); pg.wait_for_timeout(500)
                hovered = pg.evaluate(sig)
            except Exception:
                pass
        reacted_wheel = after_wheel != before
        reacted_hover = hovered != after_wheel and hovered != before
        print(f"real input: wheel changed something={reacted_wheel} "
              f"hover changed something={reacted_hover}")
        if not reacted_wheel:
            fails.append("a real wheel event changed nothing — page does not scroll "
                         "and no handler responded")
        pg.evaluate("()=>scrollTo(0,0)"); pg.wait_for_timeout(300)

        if args.detent:
            if not pg.evaluate("()=>!!(window.__probe && __probe.settle && __probe.set)"):
                fails.append("--detent given but __probe.set/settle is missing")
            else:
                meta = pg.evaluate("()=>({step:__probe.step,count:__probe.count})")
                step, count = meta["step"], meta["count"]
                # 1. released anywhere, it must land EXACTLY on a slot
                worst = 0.0; overshoot = 0
                for frac in (0.12, 0.3, 0.49, 0.51, 0.7, 0.88):
                    for slot in range(count - 1):
                        a = -(slot + frac) * step
                        pg.evaluate("(a)=>__probe.set(a)", a)
                        pg.evaluate("()=>__probe.settle(1200)")
                        r = pg.evaluate("()=>({a:__probe.angle(), i:__probe.index(), v:__probe.vel()})")
                        err = abs(r["a"] - round(r["a"]/step)*step)
                        worst = max(worst, err)
                        if abs(r["v"]) > 1e-3: overshoot += 1
                print(f"detent: worst landing error = {worst:.4f}deg, "
                      f"never-settled cases = {overshoot}")
                if worst > 0.02: fails.append(f"detent lands {worst:.3f}deg off a slot")
                if overshoot:    fails.append(f"{overshoot} cases still moving after settle")

                # 2. every slot must be reachable, and the ends must clamp
                reached = set()
                for slot in range(count):
                    pg.evaluate("(a)=>__probe.set(a)", -slot*step)
                    pg.evaluate("()=>__probe.settle(400)")
                    reached.add(pg.evaluate("()=>__probe.index()"))
                # Overshooting the range must STOP at an end slot, not wrap or
                # escape. Drive this through whatever the page's real commit path
                # is — __probe.go for a slot-driven control, __probe.push for a
                # momentum one. Testing the path nobody takes is how a broken
                # control passes (verification-harness.md §0).
                ends = []
                slot_driven = pg.evaluate("()=>!!(window.__probe && __probe.go)")
                for far in (-99, 99):
                    if slot_driven:
                        pg.evaluate("(i)=>__probe.go(i)", far)
                    else:
                        pg.evaluate("(s)=>{__probe.set(-(__probe.count-1)*__probe.step/2);"
                                    " __probe.push(s);}", far)
                    pg.evaluate("()=>__probe.settle(2000)")
                    ends.append(pg.evaluate("()=>__probe.index()"))
                print(f"        commit path = {'slot (go)' if slot_driven else 'momentum (push)'}")
                print(f"        slots reached = {len(reached)}/{count}, "
                      f"hard shove lands on = {ends}")
                if len(reached) != count: fails.append(f"only {len(reached)}/{count} slots reachable")
                if set(ends) != {0, count-1}:
                    fails.append(f"overshooting did not clamp to both ends: {ends}")
                pg.evaluate("()=>__probe.set(0)")

        if args.layer:
            probe = pg.evaluate("""() => {
              const cs = [...document.querySelectorAll('canvas')].map(c => {
                for (const t of ['webgl2','webgl','2d']) { try { if (c.getContext(t)) return t; } catch(e){} }
                return 'none';
              });
              const shapes = document.querySelectorAll('svg path,svg circle,svg line,svg polyline,svg rect').length;
              const faces = [...document.styleSheets].reduce((n, ss) => {
                try { for (const r of ss.cssRules) if (r.constructor.name === 'CSSFontFaceRule') n++; } catch(e){}
                return n;
              }, 0);
              const gl = cs.filter(k => k === 'webgl2' || k === 'webgl').length;
              return {
                primary: gl ? 'webgl' : cs.includes('2d') ? 'canvas2d' : shapes > 12 ? 'svg' : 'dom',
                contexts: cs, svg_shapes: shapes, faces,
                remote_faces: document.querySelectorAll('link[href*="fonts.googleapis"],link[rel=preload][as=font]').length,
              };
            }""")
            print(f"        render layer = {probe['primary']} (declared {args.layer}), "
                  f"canvas ctx {probe['contexts'] or '-'}, svg shapes {probe['svg_shapes']}, "
                  f"@font-face {probe['faces']}")
            if probe["primary"] != args.layer:
                fails.append(f"declared layer {args.layer!r} but the page renders as "
                             f"{probe['primary']!r} (canvas ctx {probe['contexts']}, "
                             f"{probe['svg_shapes']} svg shapes)")
            webfonts = probe["faces"] + probe["remote_faces"]
            if not webfonts and not args.draws_own_type:
                fails.append("0 @font-face and no font preload: the page runs on the system "
                             "stack. Ship a real face, or pass --draws-own-type if the page "
                             "draws its letterforms (references/render-layer.md §2).")

        if args.follow:
            need = ("centroid", "aim", "following")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--follow given but __probe is missing one of {need}")
            else:
                pg.evaluate("()=>scrollTo(0,0)"); pg.wait_for_timeout(250)
                box = pg.evaluate("()=>{const c=document.querySelector('canvas');"
                                  "const r=c.getBoundingClientRect();"
                                  "return [r.x,r.y,r.width,r.height];}")
                bx, by, bw, bh = box
                # spread the aims over the canvas, including bare ground: a dead zone
                # anywhere reads to a person as "they ignore me".
                spots = [("centre", .50, .50), ("upper right", .80, .38),
                         ("upper left", .28, .40), ("lower left", .22, .80),
                         ("lower right", .88, .70)]
                worst = None
                for name, fx, fy in spots:
                    x, y = bx + bw*fx, by + bh*fy
                    pg.mouse.move(x, y); pg.wait_for_timeout(90)
                    aim = pg.evaluate("()=>__probe.aim()")
                    if not aim:
                        fails.append(f"--follow: pointer at {name} produced no aim point")
                        continue
                    c0 = pg.evaluate("()=>__probe.centroid()")
                    for i in range(40):
                        pg.mouse.move(x + (i % 2), y); pg.wait_for_timeout(45)
                    c1 = pg.evaluate("()=>__probe.centroid()")
                    d0 = math.dist(c0, aim); d1 = math.dist(c1, aim)
                    moved = math.dist(c0, c1)
                    closed = d0 - d1
                    print(f"        follow {name:12s} aim {aim}  "
                          f"gap {d0:.2f}->{d1:.2f}  moved {moved:.2f}")
                    if moved < 0.4:
                        fails.append(f"--follow: pointer at {name} moved the crowd {moved:.2f} "
                                     f"units — nothing visibly walks there")
                    elif closed <= 0:
                        fails.append(f"--follow: pointer at {name} moved the crowd {moved:.2f} "
                                     f"units but the gap grew ({d0:.2f}->{d1:.2f})")
                    if worst is None or closed < worst[1]: worst = (name, closed)
                if worst: print(f"        weakest response: {worst[0]} closed {worst[1]:.2f}")

        if args.curtain:
            need = ("count", "cols", "rows", "rowX", "rowY", "linkLengths", "rest", "anchors")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--curtain given but __probe is missing one of {need}")
            else:
                rows = pg.evaluate("()=>__probe.rows()")
                mid = rows // 2
                # WAIT FOR ACTUAL STILLNESS, do not guess a duration. The
                # smoke test above sends a real wheel, this page turns that
                # into a gust, and the gust takes ~2.7s to decay. A fixed
                # 2.6s settle put the baseline inside that decay, so the
                # cloth kept drifting on its own and the oracle credited the
                # movement to the pointer — a copy with the pointer force set
                # to ZERO passed. Poll the probe instead.
                pg.mouse.move(60, 60)
                still = False
                for _ in range(80):
                    st = pg.evaluate("()=>({v:Math.max(...__probe.speeds()),"
                                     "g:Math.abs(__probe.gust?__probe.gust():0)})")
                    if st["v"] < 0.30 and st["g"] < 0.01: still = True; break
                    pg.wait_for_timeout(120)
                if not still:
                    fails.append("--curtain: the cloth never settled — cannot measure a "
                                 "pointer response against a moving baseline")
                x0 = pg.evaluate("(r)=>__probe.rowX(r)", mid)
                y0 = pg.evaluate("(r)=>__probe.rowY(r)", mid)
                span0 = max(x0) - min(x0)
                gaps0 = [b - a for a, b in zip(x0, x0[1:])]

                # Drive a real pointer straight through the middle of the cloth.
                cx = sum(x0) / len(x0)
                cy = sum(y0) / len(y0)
                # Sample DURING the sweep, not after it. The cloth is elastic —
                # by the time the pointer has left, most of the gap has closed,
                # and measuring the settled state reports a parting that did
                # happen as one that did not.
                x1, y1, span1 = x0, y0, span0
                for i in range(30):
                    pg.mouse.move(cx - 260 + i * (520/29), cy)
                    pg.wait_for_timeout(22)
                    xs = pg.evaluate("(r)=>__probe.rowX(r)", mid)
                    sp = max(xs) - min(xs)
                    if sp > span1:
                        span1 = sp
                        x1 = xs
                        y1 = pg.evaluate("(r)=>__probe.rowY(r)", mid)

                # ── legs 1+2 · the pair. It must open sideways, and it must
                # NOT crush vertically. An isotropic push satisfies neither
                # cleanly: it moves both, and the rows collapse into blobs.
                dx = sorted(abs(b - a) for a, b in zip(x0, x1))
                dy = sorted(abs(b - a) for a, b in zip(y0, y1))
                mdx = dx[len(dx)//2]; mdy = dy[len(dy)//2]
                aniso = mdx / mdy if mdy > 0.01 else 999
                # Total span is NOT the measure: the sweep pushes the middle
                # columns apart while the outer ones are pulled back by their
                # own links, so the cloth's overall width barely changes even
                # as every glyph in the path moves 50px. Per-column
                # displacement is what "it parted" actually means.
                print(f"        cloth: median |dx| {mdx:.2f}px  |dy| {mdy:.2f}px  "
                      f"(anisotropy {aniso:.2f}x), span {span0:.0f} -> {span1:.0f}px")
                if mdx < 6:
                    fails.append(f"--curtain: a full pointer sweep moved the median column "
                                 f"{mdx:.2f}px sideways — the cloth is not reacting")
                # NOTE: an x/y displacement ratio is NOT a usable test of the
                # anisotropic push. The vertical links absorb y motion by
                # sliding nodes along the string, so the ratio stays high
                # whatever the y gain is — a copy with the bias set to 1.0
                # measured HIGHER than the real case. Assert the structural
                # claim instead: the columns are independent strings, so
                # poking one must leave a distant one alone. Add horizontal
                # links and this is what collapses.
                if "colOffsets" in pg.evaluate("()=>Object.keys(__probe)"):
                    pg.mouse.move(60, 60)
                    for _ in range(60):
                        q = pg.evaluate("()=>({v:Math.max(...__probe.speeds()),"
                                        "g:Math.abs(__probe.gust?__probe.gust():0)})")
                        if q["v"] < 0.30 and q["g"] < 0.01: break
                        pg.wait_for_timeout(120)
                    cols = pg.evaluate("()=>__probe.cols()")
                    xs = pg.evaluate("(r)=>__probe.rowX(r)", mid)
                    ys = pg.evaluate("(r)=>__probe.rowY(r)", mid)
                    poke = 2
                    px, py = xs[poke], ys[poke]
                    for i in range(26):
                        pg.mouse.move(px + (14 if i % 2 else -14), py + (i % 5) * 3)
                        pg.wait_for_timeout(26)
                    off = pg.evaluate("()=>__probe.colOffsets()")
                    near = max(off[0:5])
                    far = max(off[cols-5:cols])
                    spread = (far / near) if near > 0.01 else 1.0
                    print(f"        independence: poked col {poke} -> near {near:.2f}px, "
                          f"far {far:.2f}px (bleed {spread*100:.0f}%)")
                    if near < 4:
                        fails.append(f"--curtain: poking a column displaced it {near:.2f}px — "
                                     f"the pointer is not reaching individual strings")
                    if spread > 0.20:
                        fails.append(f"--curtain: poking one column moved the far side of the "
                                     f"cloth {spread*100:.0f}% as much — the strings are linked "
                                     f"to each other and this is a sheet, not a curtain")

                # ── leg 3 · the solver still holds. Parting is not tearing.
                rest = pg.evaluate("()=>__probe.rest()")
                lens = pg.evaluate("()=>__probe.linkLengths()")
                worst = max(abs(l - rest) / rest for l in lens)
                print(f"        links: worst deviation {worst*100:.1f}% of {rest}px rest length")
                if worst > 0.35:
                    fails.append(f"--curtain: a link is {worst*100:.0f}% off its rest length — "
                                 f"the cloth is tearing, not parting")

                # ── leg 4 · the top row is sprung, not nailed: it must be
                # displaced during the sweep and back home afterwards.
                pg.mouse.move(60, 60); pg.wait_for_timeout(1200)
                anc = pg.evaluate("()=>__probe.anchors()")
                off = max(abs(a["x"] - a["ix"]) for a in anc)
                print(f"        anchors home after release: worst {off:.2f}px off peg")
                if off > 2.0:
                    fails.append(f"--curtain: an anchor settled {off:.2f}px from its peg — "
                                 f"the curtain does not return to its rail")

        if args.lyre:
            need = ("strings", "words", "crows", "caught", "stringNodes",
                    "stringRestY", "maxAloft", "cooldown")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--lyre given but __probe is missing one of {need}")
            else:
                n_str = pg.evaluate("()=>__probe.strings()")
                cap = pg.evaluate("()=>__probe.maxAloft()")
                tails_before = [c["tail"] for c in pg.evaluate("()=>__probe.crows()")]
                nodes0 = pg.evaluate("()=>__probe.stringNodes(0)")
                sx0 = min(n["x"] for n in nodes0); sx1 = max(n["x"] for n in nodes0)
                sy = pg.evaluate("()=>__probe.stringRestY(0)")
                last = pg.evaluate("()=>__probe.stringNodes(%d)" % (n_str - 1))
                sy_last = max(n["y"] for n in last)

                # ── legs 1+2 · the pair. Strumming must release words, and the
                # release must stay rate limited while being abused. A dead
                # instrument passes the cap; an unlimited one passes release.
                peak, seen_any = 0, 0
                for sweep in range(14):
                    yy = sy + (sy_last - sy) * ((sweep % 5) / 4.0)
                    for i in range(16):
                        fx = sx0 + (sx1 - sx0) * (i/15 if sweep % 2 == 0 else 1 - i/15)
                        pg.mouse.move(fx, yy)
                        pg.wait_for_timeout(12)
                    w = pg.evaluate("()=>__probe.words().length")
                    peak = max(peak, w); seen_any = max(seen_any, w)
                print(f"        strumming: peak words aloft {peak} (cap {cap})")
                if seen_any == 0:
                    fails.append("--lyre: fourteen real strum sweeps released no words at all — "
                                 "the strings are decorative")
                if peak > cap:
                    fails.append(f"--lyre: {peak} words aloft against a stated cap of {cap} — "
                                 f"the rate limiter does not hold and the scene floods")

                # ── leg 3 · the hunters close on what was released. A crow that
                # merely moves is not evidence it is steering toward anything.
                pg.mouse.move(40, 40)
                gaps, hunts = [], 0
                for _ in range(46):
                    st = pg.evaluate("()=>({w:__probe.words(),c:__probe.crows()})")
                    live = [w for w in st["w"] if not w["eaten"] and w["life"] > 0]
                    if live:
                        hunts += sum(1 for c in st["c"] if c["hunting"])
                        d = min(math.dist((c["x"], c["y"]), (w["x"], w["y"]))
                                for c in st["c"] for w in live)
                        gaps.append(d)
                    pg.wait_for_timeout(70)
                # Sampling starts mid-chase, so an absolute pixel threshold is
                # meaningless — the gap may already be small. Measure the close
                # as a FRACTION of where it started.
                ratio = (min(gaps) / gaps[0]) if len(gaps) >= 3 and gaps[0] > 0 else 1.0
                print(f"        hunt: {len(gaps)} samples with prey, gap {gaps[0]:.0f}->"
                      f"{min(gaps):.0f}px ({(1-ratio)*100:.0f}% closed), hunting flags {hunts}"
                      if gaps else "        hunt: no prey was ever aloft to hunt")
                if not gaps:
                    fails.append("--lyre: no word stayed aloft long enough to be hunted")
                elif hunts == 0:
                    fails.append("--lyre: words were aloft but no crow ever entered a hunting "
                                 "state — the steering target is never acquired")
                elif ratio > 0.7:
                    fails.append(f"--lyre: the nearest crow closed only {(1-ratio)*100:.0f}% of its "
                                 f"gap to the prey — it is drifting, not steering")

                # ── leg 4 · the loop closes. A capture must rewrite the
                # hunter's own tail; a counter going up proves nothing.
                caught = pg.evaluate("()=>__probe.caught()")
                tails = [c["tail"] for c in pg.evaluate("()=>__probe.crows()")]
                # Two independent signs that the capture had a consequence: the
                # tail differs from the one it started with, and it carries the
                # marker word. Do NOT match the full replacement sentence — a
                # tail holds a fixed number of nodes and the tail end of a long
                # word is simply truncated (README §踩过的坑 #2).
                changed = sum(1 for a, b in zip(tails_before, tails) if a != b)
                marked = sum(1 for t in tails if "LINES" in t)
                print(f"        captures: {caught} total, {changed}/{len(tails)} tails changed, "
                      f"{marked} carry the marker")
                if caught and not changed:
                    fails.append(f"--lyre: {caught} captures were counted but no crow's tail "
                                 f"changed at all — the counter is the only consequence")
                if caught and not marked:
                    fails.append(f"--lyre: {caught} captures were counted but no tail carries the "
                                 f"caught text — the rewrite is not using the word it caught")

        if args.flipbook:
            need = ("frameCount", "active", "opacities", "scrub", "scrubV",
                    "jitter", "toyTransforms")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--flipbook given but __probe is missing one of {need}")
            else:
                r = pg.evaluate("()=>{const s=document.querySelector('.tb-hero');"
                                "const b=s.getBoundingClientRect();"
                                "return [b.x,b.y,b.width,b.height];}")
                bx, by, bw, bh = r
                n_frames = pg.evaluate("()=>__probe.frameCount()")

                # ── legs 1+2 · the pair. Sweep a REAL pointer across the stage
                # and watch the frame stack: every sample must be a hard cut
                # (exactly one frame lit, nothing in between) AND the sequence
                # must be continuous (every frame visited, no skipped step).
                # A crossfade passes continuity and fails the cut; a page that
                # jumps straight to the end frame passes the cut and fails
                # continuity. Only a real flipbook passes both.
                pg.mouse.move(bx + bw*0.04, by + bh*0.5); pg.wait_for_timeout(700)
                seen, bad_cut = [], 0
                for i in range(60):
                    fx = 0.04 + (0.92 * i / 59)
                    pg.mouse.move(bx + bw*fx, by + bh*0.5)
                    pg.wait_for_timeout(28)
                    ops = pg.evaluate("()=>__probe.opacities()")
                    lit = [o for o in ops if o > 0.001]
                    if len(lit) != 1 or abs(lit[0] - 1) > 0.001:
                        bad_cut += 1
                    seen.append(pg.evaluate("()=>__probe.active()"))

                visited = sorted(set(seen))
                steps = [abs(b - a) for a, b in zip(seen, seen[1:])]
                skipped = sum(1 for d in steps if d > 1)
                print(f"        sweep: frames visited {visited} of {n_frames}, "
                      f"skipped steps {skipped}, soft frames {bad_cut}/60")
                if bad_cut:
                    fails.append(f"--flipbook: {bad_cut}/60 samples had a frame part-way lit — "
                                 f"this is a crossfade, not a cut")
                if len(visited) < n_frames:
                    fails.append(f"--flipbook: a full sweep only reached {len(visited)} of "
                                 f"{n_frames} frames — part of the turnaround is unreachable")
                if skipped:
                    fails.append(f"--flipbook: {skipped} transitions jumped more than one frame — "
                                 f"the scrub is snapping, not scrubbing")

                # ── leg 3 · the jitter is HELD between re-rolls. Continuous
                # noise reads as a vibration; the stop-motion read comes from a
                # low re-roll rate against a 60fps render.
                vals = pg.evaluate("""()=>new Promise(res=>{
                    const v=[]; const t0=performance.now();
                    const id=setInterval(()=>{
                      const j=__probe.jitter();
                      v.push(j.x.toFixed(4)+','+j.y.toFixed(4)+','+j.r.toFixed(4));
                      if(performance.now()-t0>1500){clearInterval(id);res(v);}
                    },14);
                  })""")
                rerolls = sum(1 for a, b in zip(vals, vals[1:]) if a != b)
                hz = rerolls / 1.5
                print(f"        jitter re-rolls: {rerolls} in 1.5s = {hz:.1f} Hz "
                      f"over {len(vals)} samples")
                if hz > 25:
                    fails.append(f"--flipbook: the jitter re-rolls at {hz:.1f} Hz — that is "
                                 f"per-frame noise, which reads as vibration not stop-motion")
                if hz < 4:
                    fails.append(f"--flipbook: the jitter re-rolls at {hz:.1f} Hz — effectively "
                                 f"frozen, so the console sits dead still between poses")

                # ── leg 4 · a fast spin has to reach the desk toys. Parallax
                # alone would satisfy "something moved"; the squash is what says
                # they were kicked rather than slid.
                pg.mouse.move(bx + bw*0.5, by + bh*0.5); pg.wait_for_timeout(300)
                airborne, squashed, peak_v = set(), 0, 0.0
                for k in range(26):
                    pg.mouse.wheel(0, 520 if k % 2 == 0 else -520)
                    for _ in range(6):
                        pg.wait_for_timeout(22)
                        st = pg.evaluate("()=>({h:__probe.hops(),v:__probe.scrubV(),"
                                         "t:__probe.toyTransforms()})")
                        peak_v = max(peak_v, abs(st["v"]))
                        for i, hy in enumerate(st["h"]):
                            if hy < -0.5: airborne.add(i)
                        squashed = max(squashed, sum(1 for t in st["t"]
                                       if "scale(" in t
                                       and not t.split("scale(")[1].startswith("1, 1)")))
                    if len(airborne) >= 2 and squashed: break
                print(f"        spin peak |scrub v| {peak_v:.1f}; desk toys airborne "
                      f"{len(airborne)}/5, squashed {squashed}/5")
                if peak_v < 2.2:
                    fails.append(f"--flipbook: the wheel only reached |v| {peak_v:.1f}, under the "
                                 f"2.2 kick threshold — this leg never tested anything")
                elif not airborne:
                    fails.append("--flipbook: spinning the console never lifted a desk toy off the "
                                 "table — they are sliding with parallax, not being kicked")
                elif not squashed:
                    fails.append("--flipbook: desk toys leave the table but never squash on landing "
                                 "— the hop is a translate, not a body with weight")

        if args.stack:
            need = ("sections", "tops", "vh", "progress", "stickyTops", "grounds",
                    "words", "wordKeys", "drawn", "dim")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--stack given but __probe is missing one of {need}")
            else:
                pg.wait_for_timeout(3600)          # let the preloader finish
                vh   = pg.evaluate("()=>__probe.vh()")
                n    = pg.evaluate("()=>__probe.sections()")
                sec_tops = pg.evaluate("()=>__probe.tops()")

                # 1. native scroll, and every screen pins. This is the opposite
                #    contract to --rail: scrollY MUST move here.
                pg.evaluate("()=>scrollTo(0,0)"); pg.wait_for_timeout(300)
                pinned, moved = 0, []
                for i in range(n):
                    pg.evaluate("(y)=>scrollTo(0,y)", sec_tops[i] + 8); pg.wait_for_timeout(220)
                    sy = pg.evaluate("()=>Math.round(scrollY)")
                    rects = pg.evaluate("()=>__probe.stickyTops()")
                    moved.append(sy)
                    if abs(rects[i]) <= 2: pinned += 1
                print(f"        stack: {pinned}/{n} screens pinned at top 0, "
                      f"scrollY reached {max(moved)}")
                if pinned < n:
                    fails.append(f"--stack: only {pinned} of {n} screens pinned at top 0. "
                                 f"Without sticky the screens just scroll past and the "
                                 f"overlay that defines this page never happens")
                if max(moved) < vh:
                    fails.append("--stack: window.scrollY never advanced a screen. This "
                                 "page is supposed to use native scroll, not hijack it")

                # 2. the grounds must actually differ, or stacking is invisible
                grounds = pg.evaluate("()=>__probe.grounds()")
                uniq = len(set(grounds))
                print(f"        grounds: {uniq} distinct across {n} screens")
                if uniq < 3:
                    fails.append(f"--stack: only {uniq} distinct grounds; one screen "
                                 f"sliding over another the same colour reads as nothing")

                # 3. the wipe. A gradient at some moment, in reading order, and
                #    unlit type that stays readable rather than vanishing.
                keys = pg.evaluate("()=>__probe.wordKeys()")
                order = sorted(range(len(keys)), key=lambda i: keys[i])
                best_spread, floor, inversions = 0.0, 1.0, 0
                for f in [x / 16 for x in range(17)]:
                    pg.evaluate("(y)=>scrollTo(0,y)", sec_tops[1] + f * vh); pg.wait_for_timeout(150)
                    w = pg.evaluate("()=>__probe.words()")
                    floor = min(floor, min(w))
                    best_spread = max(best_spread, max(w) - min(w))
                    seq = [w[i] for i in order]
                    inversions += sum(1 for a, b in zip(seq, seq[1:]) if b > a + 0.02)
                print(f"        wipe: widest spread {best_spread:.2f}, dimmest word "
                      f"{floor:.2f}, out-of-order pairs {inversions}")
                if best_spread < 0.35:
                    fails.append(f"--stack: the block's widest spread of word brightness was "
                                 f"{best_spread:.2f}. Everything lights at once, so this is a "
                                 f"switch, not a wipe")
                if floor < 0.12:
                    fails.append(f"--stack: the dimmest word reached {floor:.2f}. On the "
                                 f"reference unlit type sits at 0.22 and stays readable; "
                                 f"fading from zero is a different device")
                if inversions > 2:
                    fails.append(f"--stack: {inversions} pairs lit out of reading order. The "
                                 f"wipe has to travel through the block, not scatter")

                # 4. real wheel input, because scrollTo teleports past exactly the
                #    thing being tested. A stack whose screens never dwell is fully
                #    pinned, fully wiped and completely dead to anyone scrolling it.
                SAMPLE = """() => [...document.querySelectorAll('body *')].map(e => {
                  const s = getComputedStyle(e), r = e.getBoundingClientRect();
                  if (r.width < 2 || r.height < 2) return null;
                  return [s.transform, s.opacity, Math.round(r.top)];
                })"""
                pg.evaluate("()=>scrollTo(0,0)"); pg.wait_for_timeout(400)
                pg.mouse.move(760, 430)
                frames, mid = [pg.evaluate(SAMPLE)], 0
                for _ in range(18):
                    for _ in range(7):
                        pg.mouse.wheel(0, 130); pg.wait_for_timeout(20)
                    pg.wait_for_timeout(80)
                    mid = max(mid, pg.evaluate("""()=>[...document.querySelectorAll('body *')]
                        .filter(e=>{const o=+getComputedStyle(e).opacity; return o>0.03 && o<0.97}).length"""))
                    pg.wait_for_timeout(300)
                    frames.append(pg.evaluate(SAMPLE))
                m = min(len(f) for f in frames)
                live = tracked = 0
                for i in range(m):
                    vals = [f[i] for f in frames]
                    if any(v is None for v in vals): continue
                    tracked += 1
                    if any(len({v[k] for v in vals}) > 1 for k in (0, 1)): live += 1
                pct = 100 * live / max(1, tracked)
                reached = pg.evaluate("()=>Math.round(scrollY)")
                print(f"        real wheel: {live}/{tracked} elements moved ({pct:.0f}%), "
                      f"peak mid-transition {mid}, scrollY {reached}")
                if pct < 30:
                    fails.append(f"--stack: under a real wheel only {pct:.0f}% of elements "
                                 f"changed transform or opacity. Screens sliding past each "
                                 f"other is not the same as anything happening inside them")
                if mid < 4:
                    fails.append(f"--stack: at most {mid} elements were caught part-way "
                                 f"through a transition under a real wheel. Every screen is "
                                 f"either arriving or leaving, with no window to play in")

                # 5. the artwork is drawn, not fetched
                drawn = pg.evaluate("()=>__probe.drawn()")
                imgs  = pg.evaluate("""()=>document.querySelectorAll('img,picture,svg image').length
                  + [...document.querySelectorAll('*')].filter(e=>{
                      const b = getComputedStyle(e).backgroundImage;
                      return b && b !== 'none' && b.includes('url(');
                    }).length""")
                print(f"        artwork: {drawn} canvases, {imgs} image elements")
                if drawn < 8:
                    fails.append(f"--stack: only {drawn} canvases. This case exists because "
                                 f"the art is generated; grey rectangles are what it replaces")
                if imgs:
                    fails.append(f"--stack: {imgs} elements pull a bitmap. Nothing here may "
                                 f"depend on an asset that is not drawn by the page")

        if args.rail:
            need = ("railY", "pageScrollY", "scroll", "target", "max", "blobXY",
                    "panelXY", "label", "jump")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--rail given but __probe is missing one of {need}")
            else:
                pg.evaluate("()=>{__probe.jump(0); scrollTo(0,0);}"); pg.wait_for_timeout(250)

                # 1. the wheel must drive the rail, and must not drive the page
                y0 = pg.evaluate("()=>__probe.railY()")
                for _ in range(8):
                    pg.mouse.wheel(0, 120); pg.wait_for_timeout(30)
                pg.wait_for_timeout(700)
                y1 = pg.evaluate("()=>__probe.railY()")
                sy = pg.evaluate("()=>__probe.pageScrollY()")
                print(f"        wheel: railY {y0:.0f} -> {y1:.0f}   window.scrollY {sy}")
                if abs(y1 - y0) < 200:
                    fails.append(f"--rail: 8 wheel ticks moved the rail {abs(y1-y0):.0f}px — "
                                 f"the wheel is not driving anything")
                if sy != 0:
                    fails.append(f"--rail: window.scrollY reached {sy}; the wheel was not "
                                 f"hijacked, so the browser will scroll past the choreography")
                # overflow:hidden also pins scrollY, so it alone does not prove a hijack.
                # The event itself has to be cancelled or the trackpad still overscrolls.
                cancelled = pg.evaluate("""()=>{
                  const e = new WheelEvent('wheel',
                    {deltaY:120, cancelable:true, bubbles:true});
                  window.dispatchEvent(e);
                  return e.defaultPrevented;
                }""")
                print(f"        wheel event cancelled: {cancelled}")
                if not cancelled:
                    fails.append("--rail: the wheel event is not cancelled. overflow:hidden "
                                 "pins scrollY but the trackpad still overscrolls and rubber-"
                                 "bands, so the hijack is only half done")

                # 2. it has to lag. A rail that lands on the same frame as the wheel
                #    event is a jump cut, which is what this whole device exists to avoid.
                pg.evaluate("()=>__probe.jump(0)"); pg.wait_for_timeout(300)
                pg.mouse.wheel(0, 900)
                pg.wait_for_timeout(40)
                gap = pg.evaluate("()=>__probe.target() - __probe.scroll()")
                pg.wait_for_timeout(900)
                rest = pg.evaluate("()=>__probe.target() - __probe.scroll()")
                print(f"        lag: gap 40 ms after the tick {gap:.0f}px, "
                      f"after 900 ms {rest:.0f}px")
                if gap < 30:
                    fails.append(f"--rail: the rail was already within {gap:.0f}px of target "
                                 f"40 ms after the wheel — it snaps instead of easing")
                if abs(rest) > 6:
                    fails.append(f"--rail: 900 ms after the wheel the rail is still {rest:.0f}px "
                                 f"from target — it never settles")

                # 3. parallax needs depth: the far wash must out-travel the near card,
                #    or the pointer is just sliding one flat plane around
                pg.mouse.move(200, 700); pg.wait_for_timeout(900)
                fa = pg.evaluate("()=>__probe.blobXY()[0]"); na = pg.evaluate("()=>__probe.panelXY()")
                pg.mouse.move(1240, 180); pg.wait_for_timeout(900)
                fb = pg.evaluate("()=>__probe.blobXY()[0]"); nb = pg.evaluate("()=>__probe.panelXY()")
                far  = math.dist(fa, fb)
                near = math.dist(na, nb)
                print(f"        pointer sweep: far layer {far:.1f}px, near layer {near:.1f}px")
                if far < 20:
                    fails.append(f"--rail: the pointer moved the far layer {far:.1f}px — "
                                 f"mouse movement produces nothing a person would notice")
                if near < 3:
                    fails.append(f"--rail: the near layer moved {near:.1f}px; only one plane "
                                 f"responds, so there is no depth")
                if far <= near * 1.5:
                    fails.append(f"--rail: far layer {far:.1f}px vs near {near:.1f}px — the "
                                 f"planes move together, which reads as a flat slide")

                # 4. the elements themselves have to move. A rail that translates
                #    while every child holds still is a normal scroll wearing a
                #    hijack — it passed every earlier assertion here and read as
                #    completely dead to the person looking at it.
                SAMPLE = """() => [...document.querySelectorAll('body *')].map(e => {
                  const s = getComputedStyle(e), r = e.getBoundingClientRect();
                  if (r.width < 2 || r.height < 2) return null;
                  return [s.transform, s.opacity, s.strokeDashoffset];
                })"""
                pg.evaluate("()=>__probe.jump(0)"); pg.wait_for_timeout(500)
                pg.mouse.move(720, 450)
                frames, midflight = [pg.evaluate(SAMPLE)], 0
                for _ in range(8):
                    for _ in range(5):
                        pg.mouse.wheel(0, 110); pg.wait_for_timeout(24)
                    pg.wait_for_timeout(90)
                    midflight = max(midflight, pg.evaluate("""()=>[...document.querySelectorAll('body *')]
                        .filter(e=>{const o=+getComputedStyle(e).opacity; return o>0.02 && o<0.98}).length"""))
                    pg.wait_for_timeout(380)
                    frames.append(pg.evaluate(SAMPLE))
                n = min(len(f) for f in frames)
                live = tracked = 0
                for i in range(n):
                    vals = [f[i] for f in frames]
                    if any(v is None for v in vals): continue
                    tracked += 1
                    if any(len({v[k] for v in vals}) > 1 for k in (0, 1, 2)): live += 1
                pct = 100 * live / max(1, tracked)
                print(f"        element churn: {live}/{tracked} moved ({pct:.0f}%), "
                      f"peak mid-flight {midflight}")
                if pct < 35:
                    fails.append(f"--rail: only {pct:.0f}% of elements changed transform, "
                                 f"opacity or stroke across the whole run. The rail moves and "
                                 f"the content rides it — that is a scrollbar, not choreography")
                if midflight < 4:
                    fails.append(f"--rail: at most {midflight} elements were ever caught "
                                 f"part-way through a transition. States are snapping, so the "
                                 f"page reads as a slideshow no matter how many of them change")

                # 5. with the mouse completely still, the signature shape still has
                #    to live. Input-driven and ambient are not alternatives — the
                #    reference has both, and a page with only the first reads as
                #    frozen to anyone who looks at it before touching it.
                pg.evaluate("()=>__probe.jump(0)"); pg.wait_for_timeout(700)
                SIG = """() => [...document.querySelectorAll('body *')].map(e => {
                  const s = getComputedStyle(e);
                  return s.background + '|' + s.transform + '|' + s.left + '|' + s.top;
                })"""
                idle = [pg.evaluate(SIG)]
                for _ in range(3):
                    pg.wait_for_timeout(520); idle.append(pg.evaluate(SIG))
                m = min(len(f) for f in idle)
                breathing = sum(1 for i in range(m) if len({f[i] for f in idle}) > 1)
                print(f"        untouched for 1.5 s: {breathing} elements still moving")
                if breathing < 2:
                    fails.append(f"--rail: with no input at all, {breathing} elements changed "
                                 f"over 1.5 s. Everything on the page waits for the mouse, so "
                                 f"the first thing anyone sees is a still image")

                # 6. the run has to reach its end and change what it says on the way
                labels, mx = [], pg.evaluate("()=>__probe.max()")
                for f in (0.0, 0.3, 0.6, 0.95):
                    pg.evaluate("(v)=>__probe.jump(v)", mx * f); pg.wait_for_timeout(220)
                    labels.append(pg.evaluate("()=>__probe.label()"))
                uniq = len(set(labels))
                print(f"        section labels across the run: {labels} ({uniq} distinct)")
                if uniq < 3:
                    fails.append(f"--rail: only {uniq} distinct section labels across the whole "
                                 f"run — the rail moves but the page never announces where it is")

        if args.strings:
            need = ("setTime", "settle", "hand", "tipXY", "mode", "slack", "reset")
            if not pg.evaluate("(n)=>!!window.__probe && n.every(k=>k in __probe)", list(need)):
                fails.append(f"--strings given but __probe is missing one of {need}")
            else:
                pg.evaluate("()=>scrollTo(0,0)"); pg.wait_for_timeout(200)
                keys = pg.evaluate("()=>__probe.keys")

                # 1. The two conditions that pull against each other. A slack string
                #    clock is only the design if BOTH hold: the endpoint is still on
                #    the true angle, and the stroke between the ends is visibly not a
                #    line. Over-damp it and (2) dies; under-constrain it and (1) does.
                pg.evaluate("()=>{__probe.mode('strings'); __probe.slack(0.5);}")
                worst_err = 0.0; least_sag = 9.0
                for (h, m, sec) in [(12,0,0),(1,30,15),(3,0,30),(4,45,45),
                                    (6,0,7),(7,20,52),(9,0,22),(10,10,38)]:
                    pg.evaluate("(t)=>{__probe.setTime(t[0],t[1],t[2]); __probe.reset();"
                                " __probe.settle(2600);}", [h, m, sec])
                    for k in keys:
                        r = pg.evaluate("(k)=>__probe.hand(k)", k)
                        worst_err = max(worst_err, r["angleErr"])
                        least_sag = min(least_sag, r["slack"])
                        if r["bad"]: fails.append(f"{k}: {r['bad']} non-finite nodes at {h}:{m}")
                print(f"strings: worst tip-angle error = {worst_err:.2f}deg over 8 times x "
                      f"{len(keys)} hands; least sag = {least_sag:.3f}x chord")
                if worst_err > 1.5:
                    fails.append(f"tip is {worst_err:.2f}deg off the true angle — "
                                 f"the endpoint no longer tells the time")
                if least_sag < 1.12:
                    fails.append(f"least sag {least_sag:.3f}x — a hand straightened out, "
                                 f"which is the rigid clock the design exists to refuse")

                # 2. The control that removes the slack must actually remove it.
                pg.evaluate("()=>{__probe.mode('rods'); __probe.reset(); __probe.settle(1800);}")
                rods = [pg.evaluate("(k)=>__probe.hand(k)", k) for k in keys]
                rod_sag = max(r["slack"] for r in rods)
                rod_err = max(r["angleErr"] for r in rods)
                print(f"         rods mode: max sag = {rod_sag:.3f}x, max angle error = {rod_err:.2f}deg")
                if rod_sag > 1.03: fails.append(f"rods still sag {rod_sag:.3f}x")
                if rod_err > 1.0:  fails.append(f"rods point {rod_err:.2f}deg off")
                pg.evaluate("()=>{__probe.mode('strings'); __probe.reset(); __probe.settle(2000);}")

                # 3. A REAL pointer drag, three speeds. Not __probe — the probe has no
                #    method that moves a string, on purpose: a probe that bypasses the
                #    handlers tests a path nobody takes (cases/AUTHORING.md 硬教训 1).
                key = keys[-1]
                rest_arc = pg.evaluate("(k)=>__probe.hand(k)", key)["arc"]
                worst_arc = 0.0; escaped = 0
                for speed in (12, 60, 240):
                    t = pg.evaluate("(k)=>__probe.tipXY(k)", key)
                    pg.mouse.move(t["x"], t["y"]); pg.mouse.down()
                    if not pg.evaluate("()=>__probe.grabbing()"):
                        fails.append(f"pointerdown on the {key} tip did not grab it")
                        pg.mouse.up(); break
                    x, y = t["x"], t["y"]
                    for f in range(48):
                        x += speed * math.cos(f/5.0); y += speed * math.sin(f/3.0)
                        pg.mouse.move(x, y)
                        r = pg.evaluate("(k)=>__probe.hand(k)", key)
                        worst_arc = max(worst_arc, r["arc"] / rest_arc)
                        escaped += r["escaped"]
                        if r["bad"]:
                            fails.append(f"non-finite node while dragging at {speed}px/step"); break
                    pg.mouse.up()
                    pg.evaluate("()=>__probe.settle(2800)")
                back = pg.evaluate("(k)=>__probe.hand(k)", key)
                ret = abs(back["arc"] - rest_arc) / rest_arc
                print(f"         real drag: worst stretch = {worst_arc:.2f}x rest arc, "
                      f"nodes off-canvas = {escaped}, arc after release = "
                      f"{ret*100:.1f}% from rest")
                if worst_arc > 3.2:
                    fails.append(f"string stretched {worst_arc:.2f}x rest — the per-segment "
                                 f"cap is not holding")
                if escaped:
                    fails.append(f"{escaped} node-samples left the dial box during a drag")
                if ret > 0.04:
                    fails.append(f"arc is {ret*100:.1f}% off rest after release — it does not "
                                 f"come back")
                # 4. FREE-RUNNING. Everything above pins the clock and settles, which
                #    is exactly the regime a real page is never in. Unpin and watch:
                #    a tip that drifts, or a body that never stops sloshing, shows up
                #    here and nowhere else.
                pg.evaluate("()=>{__probe.unpin(); __probe.reset();}")
                pg.wait_for_timeout(3500)                      # let the load transient die
                run_err = 0.0; run_sag = []; run_v = 0.0
                for _ in range(6):
                    pg.wait_for_timeout(500)
                    for k in keys:
                        r = pg.evaluate("(k)=>__probe.hand(k)", k)
                        run_err = max(run_err, r["angleErr"])
                        run_sag.append(r["slack"]); run_v = max(run_v, r["maxV"])
                print(f"         free-running 3s: worst tip error = {run_err:.2f}deg, "
                      f"sag {min(run_sag):.3f}-{max(run_sag):.3f}, peak node speed = {run_v:.0f}/s")
                if run_err > 1.5:
                    fails.append(f"free-running tip drifts {run_err:.2f}deg off the true angle")
                if min(run_sag) < 1.12 or max(run_sag) > 1.60:
                    fails.append(f"free-running sag {min(run_sag):.3f}-{max(run_sag):.3f} "
                                 f"outside [1.12, 1.60] — it never calms down, or it went taut")
                if run_v > 400:
                    fails.append(f"free-running node speed {run_v:.0f}/s — the body is still "
                                 f"sloshing with no input")
                pg.evaluate("()=>__probe.reset()")

        ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        p2 = ctx.new_page(); p2.goto(url); p2.wait_for_timeout(500)
        rm = p2.evaluate("""()=>{const sel='h1,h2,h3,p,[class*=num]';
          const all=[...document.querySelectorAll(sel)];
          const hid=all.filter(e=>{const cs=getComputedStyle(e);
            return cs.opacity==='0'||cs.visibility==='hidden'
                || cs.clipPath==='inset(0px 100% 0px 0px)';});
          return {hidden:hid.length,total:all.length};}""")
        print("reduced-motion:", rm)
        if rm["hidden"]: fails.append(f"{rm['hidden']} elements stuck hidden under reduced-motion")
        b.close()

    if fails:
        print("\nVERDICT: FAIL"); [print("  -", f) for f in fails]; sys.exit(1)
    print("\nVERDICT: PASS")


if __name__ == "__main__":
    main()
