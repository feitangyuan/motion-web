#!/usr/bin/env python3
"""
measure_churn.py — how much of a page actually moves when a person scrolls it.

This is the instrument for the one failure no other check in this skill caught:
a page that has every mechanism the reference has, passes the acceptance floor
and every bespoke oracle, and still reads as completely dead. It happened twice
in a row, on two different cases, and both times the numbers below were what
settled it.

  # characterise a reference before building anything
  python3 scripts/measure_churn.py https://example.com

  # the same measurement on your build, with the reference's number to beat
  python3 scripts/measure_churn.py cases/foo/index.html --target 64

  # both at once
  python3 scripts/measure_churn.py cases/foo/index.html --against https://example.com

What it reports:

  churn        the share of on-screen elements whose transform, opacity or
               stroke-dashoffset changed at least once during a real wheel run.
               Measured references land near 64%. A page where a rail or a
               stack slides while every child holds still lands near 13%.
  mid-flight   the most elements caught part-way through a transition in one
               sample. A page that snaps between states can have high churn and
               still read as a slideshow; this is what separates them.
  idle         elements still changing 1.5 s after the last input, with the
               pointer parked. High is not better — it is a different contract.
               overheardhq is 88% still; the ink crowd is 95% moving. Know which
               one you are building before you read this number as good or bad.

It drives a REAL wheel. scrollTo() teleports past the arriving-and-leaving
window, which is exactly where the motion lives; three separate oracles in this
skill passed dead pages because they used it.

Requires: playwright (chromium), and a URL or a path to an HTML file.
"""
import argparse, sys
from pathlib import Path

SAMPLE = """() => [...document.querySelectorAll('body *')].map(e => {
  const s = getComputedStyle(e), r = e.getBoundingClientRect();
  if (r.width < 2 || r.height < 2) return null;
  return [s.transform, s.opacity, s.strokeDashoffset, s.backgroundColor, s.color];
})"""

MIDFLIGHT = """() => [...document.querySelectorAll('body *')]
  .filter(e => { const o = +getComputedStyle(e).opacity; return o > 0.03 && o < 0.97 })
  .length"""


def target_url(t):
    if t.startswith(("http://", "https://", "file://")):
        return t
    p = Path(t).resolve()
    if not p.exists():
        sys.exit(f"no such file: {t}")
    return p.as_uri()


def run(pg, url, a):
    pg.goto(url, wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(a.settle)
    pg.mouse.move(760, 430)
    pg.wait_for_timeout(300)

    frames, mid = [pg.evaluate(SAMPLE)], 0
    for _ in range(a.bursts):
        for _ in range(a.ticks):
            pg.mouse.wheel(0, a.delta)
            pg.wait_for_timeout(20)
        pg.wait_for_timeout(80)
        mid = max(mid, pg.evaluate(MIDFLIGHT))
        pg.wait_for_timeout(a.dwell)
        frames.append(pg.evaluate(SAMPLE))

    n = min(len(f) for f in frames)
    live = tracked = 0
    per_prop = [0] * 5
    for i in range(n):
        vals = [f[i] for f in frames]
        if any(v is None for v in vals):
            continue
        tracked += 1
        hit = False
        for k in range(5):
            if len({v[k] for v in vals}) > 1:
                per_prop[k] += 1
                if k < 3:
                    hit = True
        if hit:
            live += 1

    # idle: nothing touched, pointer parked
    a0 = pg.evaluate(SAMPLE)
    pg.wait_for_timeout(1500)
    a1 = pg.evaluate(SAMPLE)
    m = min(len(a0), len(a1))
    idle = sum(1 for i in range(m)
               if a0[i] and a1[i] and any(a0[i][k] != a1[i][k] for k in range(3)))

    reached = pg.evaluate("()=>Math.round(scrollY)")
    hijacked = reached == 0
    return {
        "tracked": tracked, "live": live,
        "churn": 100 * live / max(1, tracked),
        "mid": mid, "idle": idle, "scrollY": reached, "hijacked": hijacked,
        "transform": per_prop[0], "opacity": per_prop[1], "stroke": per_prop[2],
        "background": per_prop[3], "color": per_prop[4],
    }


def report(name, r):
    print(f"\n── {name}")
    print(f"   churn        {r['live']}/{r['tracked']} elements moved  "
          f"({r['churn']:.0f}%)")
    print(f"   mid-flight   {r['mid']} caught part-way through a transition")
    print(f"   idle         {r['idle']} still changing 1.5 s after the last input")
    print(f"   scroll       window.scrollY reached {r['scrollY']}"
          + ("  (hijacked — the wheel drives something else)" if r["hijacked"] else ""))
    print(f"   by property  transform {r['transform']}  opacity {r['opacity']}  "
          f"stroke {r['stroke']}  background {r['background']}  color {r['color']}")


def verdict(r, floor):
    lines = []
    if r["churn"] < floor:
        lines.append(f"   churn {r['churn']:.0f}% is under {floor:.0f}%. Whatever moves here, "
                     f"it is the container and not the content.")
    if r["mid"] < 4:
        lines.append(f"   only {r['mid']} elements were ever mid-transition. States are "
                     f"snapping, so this reads as a slideshow however high the churn is.")
    if r["opacity"] < r["tracked"] * 0.1:
        lines.append("   almost nothing changes opacity. On every reference measured for "
                     "this skill that is the dominant device, and it comes from splitting "
                     "copy into per-word spans.")
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="URL, or a path to an HTML file")
    ap.add_argument("--against", help="a second target to measure the same way")
    ap.add_argument("--target", dest="floor", type=float, default=35.0,
                    help="churn %% the first target must reach (default 35)")
    ap.add_argument("--bursts", type=int, default=14)
    ap.add_argument("--ticks", type=int, default=7)
    ap.add_argument("--delta", type=int, default=130)
    ap.add_argument("--dwell", type=int, default=320, help="ms between bursts")
    ap.add_argument("--settle", type=int, default=3800,
                    help="ms to wait after load, for preloaders")
    ap.add_argument("-w", "--width", type=int, default=1440)
    ap.add_argument("-H", "--height", type=int, default=900)
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": a.width, "height": a.height})
        mine = run(pg, target_url(a.target), a)
        report(a.target, mine)
        if a.against:
            ref = run(pg, target_url(a.against), a)
            report(a.against, ref)
            gap = ref["churn"] - mine["churn"]
            print(f"\n   gap          reference moves {gap:+.0f} points "
                  f"{'more' if gap > 0 else 'less'} of its page")
        b.close()

    bad = verdict(mine, a.floor)
    if bad:
        print("\n" + "\n".join(bad))
        sys.exit(1)
    print(f"\n   OK — churn {mine['churn']:.0f}% at or above {a.floor:.0f}%, "
          f"{mine['mid']} elements mid-transition")


if __name__ == "__main__":
    main()
