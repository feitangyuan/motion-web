#!/usr/bin/env python3
"""
measure_frames.py — deconstruct a VIDEO reference with numbers.

measure_structure.py and measure_churn.py both need a page you can load. A clip
does not have one. This is the instrument for that case (cases/AUTHORING.md
Phase 1): it decodes frames and measures the same axes off pixels.

  python3 scripts/measure_frames.py sheet   ref.mp4 [-n 16]      # look at it first
  python3 scripts/measure_frames.py palette ref.mp4 [-t 8]
  python3 scripts/measure_frames.py bands   ref.mp4 [-t 8] [--right]
  python3 scripts/measure_frames.py trace   ref.mp4 --color red [--fps 3]
  python3 scripts/measure_frames.py grounds ref.mp4 [--fps 30] [--cut 26]
  python3 scripts/measure_frames.py wipe    ref.mp4 --from 7.9 --to 10.1 [--dark]

Always run `sheet` first and actually look at the contact sheet. Every other
subcommand answers a question you can only ask after you have seen the thing.

A screen recording of a retina window is 2x CSS px — halve every length before
writing it into a README, and say in the report that the number came from a
frame, not from a live page.

Requires: ffmpeg/ffprobe on PATH, Pillow, numpy.
"""
import argparse, subprocess, sys, tempfile, collections
from pathlib import Path

import numpy as np
from PIL import Image


def sh(*cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(cmd)}\n{r.stderr.strip()[:600]}")
    return r.stdout.strip()


def duration(mp4):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", str(mp4)))


def hexof(t):
    return "#%02x%02x%02x" % tuple(int(v) for v in t)


def native(mp4, t):
    """One full-resolution frame at t seconds."""
    out = Path(tempfile.mkdtemp()) / "native.png"
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(mp4),
       "-frames:v", "1", str(out))
    return np.asarray(Image.open(out).convert("RGB")).astype(int)


# ── grounds ──────────────────────────────────────────────────────────────────
def cmd_grounds(a):
    """Section changes and their mechanism, from three horizontal band means.

    A page that swaps grounds tells you how it swaps them: if the top band is
    still the old colour while the bottom band is already the new one, the new
    screen is arriving from below and covering the old one. If both change on
    the same frame it is a cut, and if they drift together it is a cross-fade.
    Reading that off stills is guesswork; three numbers per frame settles it."""
    tmp = Path(tempfile.mkdtemp())
    sh("ffmpeg", "-v", "error", "-y", "-i", str(a.mp4),
       "-vf", f"fps={a.fps},scale=320:-1", str(tmp / "g%05d.png"))
    fs = sorted(tmp.glob("g*.png"))
    if not fs: sys.exit("no frames decoded")
    A = np.stack([np.asarray(Image.open(f).convert("RGB")).astype(float) for f in fs])
    N, H, W, _ = A.shape
    # stay inside the recording: a screen capture usually has a desktop border
    inner = A[:, int(H * a.inset):int(H * (1 - a.inset)),
                 int(W * a.inset):int(W * (1 - a.inset))]
    def band(y0, y1):
        return inner[:, int(inner.shape[1]*y0):int(inner.shape[1]*y1)].reshape(N, -1, 3).mean(1)
    top, mid, bot = band(0, .22), band(.4, .6), band(.78, 1.0)

    d = np.abs(np.diff(mid, axis=0)).sum(1)
    runs = []
    for i in np.nonzero(d > a.cut)[0]:
        if runs and i - runs[-1][-1] <= 2: runs[-1].append(int(i))
        else: runs.append([int(i)])
    print(f"{N} frames at {a.fps} fps, {N/a.fps:.1f}s\n")
    print(f"{'t':>7}  {'span':>13}  before -> after (mid band)   mechanism")
    for r in runs:
        i, j = r[0], min(N - 1, r[-1] + 2)
        b4, af = mid[max(0, i - 2)], mid[j]
        # who moved first tells you the direction the new screen came from
        dt = np.abs(top[j] - top[max(0, i-2)]).sum()
        db = np.abs(bot[j] - bot[max(0, i-2)]).sum()
        how = ("cut / crossfade" if abs(dt - db) < 18 else
               "arriving from below" if db > dt else "arriving from above")
        print(f"{i/a.fps:>7.2f}  {len(r):>2}f {len(r)/a.fps*1000:>7.0f}ms  "
              f"{hexof(b4)} -> {hexof(af)}   {how}")
    print("\nground every second (top | mid | bot):")
    step = max(1, int(a.fps))
    for i in range(0, N, step):
        print(f"  {i/a.fps:>5.1f}s  {hexof(top[i])}  {hexof(mid[i])}  {hexof(bot[i])}")
    grounds = {hexof(mid[i]) for i in range(0, N, step)}
    print(f"\n{len(grounds)} distinct grounds sampled: {' '.join(sorted(grounds))}")


# ── wipe ─────────────────────────────────────────────────────────────────────
def cmd_wipe(a):
    """The schedule of a per-word / per-line reveal, as a brightness profile.

    The question a still frame cannot answer is whether unlit type is *hidden*
    or merely *dimmed* — opacity 0 and opacity 0.22 look identical in a
    thumbnail and are completely different devices to build. This prints the
    glyph-only luminance of eight bands down the block, per frame, plus the
    floor: the dimmest the type ever gets while the reveal is running."""
    tmp = Path(tempfile.mkdtemp())
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(getattr(a, "from")),
       "-t", str(a.to - getattr(a, "from")), "-i", str(a.mp4),
       "-vf", "fps=30,scale=1120:-1", str(tmp / "w%04d.png"))
    fs = sorted(tmp.glob("w*.png"))
    if not fs: sys.exit("no frames decoded in that window")
    A = np.stack([np.asarray(Image.open(f).convert("RGB")).astype(float) for f in fs])
    N, H, W, _ = A.shape
    P = A[:, int(H*.07):int(H*.90), int(W*a.inset):int(W*(1-a.inset))]
    print(f"{N} frames, t {getattr(a,'from')}..{a.to}s, page crop {P.shape[2]}x{P.shape[1]}")
    print(f"{'f':>4}{'t':>7}{'peak':>7}{'floor':>7}  eight bands, top of block -> bottom")
    floor_seen, ratios = 1e9, []
    for i in range(0, N, a.every):
        f = P[i]; lum = f.mean(2); ground = np.median(lum)
        # light glyphs on a dark ground, or dark glyphs on a light one
        text = lum > ground + a.delta if a.dark else lum < ground - a.delta
        prof = np.array([lum[r][text[r]].mean() if text[r].sum() > 3 else 0
                         for r in range(f.shape[0])])
        ys = np.nonzero(prof > 0)[0]
        if len(ys) < 6:
            print(f"{i:>4}{getattr(a,'from')+i/30:>7.2f}   (no type found)"); continue
        v = prof[ys]
        bands = [v[int(len(v)*k/8):int(len(v)*(k+1)/8)].mean() for k in range(8)]
        lo, hi = min(bands), max(bands)
        floor_seen = min(floor_seen, lo)
        if hi > 0: ratios.append(lo / hi)
        print(f"{i:>4}{getattr(a,'from')+i/30:>7.2f}{hi:>7.0f}{lo:>7.0f}  "
              + " ".join(f"{b:>4.0f}" for b in bands))
    if ratios:
        r = min(ratios)
        print(f"\ndimmest band / brightest band, worst frame: {r:.2f}")
        print("  ~0.00  the reveal fades from nothing (opacity 0 -> 1)")
        print("  >0.10  unlit type stays readable and the reveal only raises it")
        print("         — build it as opacity {:.2f} -> 1, not 0 -> 1".format(max(r, 0.0)))


# ── sheet ────────────────────────────────────────────────────────────────────
def cmd_sheet(a):
    dur = duration(a.mp4)
    cols = 4
    rows = -(-a.n // cols)
    out = Path(a.out or (Path(a.mp4).stem + "-sheet.jpg"))
    sh("ffmpeg", "-v", "error", "-y", "-i", str(a.mp4),
       "-vf", f"fps={a.n/dur},scale=560:-2,tile={cols}x{rows}:padding=6:margin=6:color=0x202020",
       "-frames:v", "1", str(out))
    print(f"{dur:.2f}s  ->  {out}  ({a.n} frames, {cols}x{rows})")
    print("Look at it before running anything else.")


# ── palette ──────────────────────────────────────────────────────────────────
def cmd_palette(a):
    im = native(a.mp4, a.t)
    H, W, _ = im.shape
    print(f"frame {W}x{H}  (if this is a 2x capture, CSS px = {W//2}x{H//2})")

    c = collections.Counter()
    for y in range(0, H, 3):
        for x in range(0, W, 3):
            c[tuple(im[y, x])] += 1
    tot = sum(c.values())
    print("\ndominant:")
    for col, n in c.most_common(10):
        print(f"  {hexof(col)}  {100*n/tot:6.2f}%")

    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    sat = R.astype(int) - np.minimum(G, B)
    ys, xs = np.nonzero(sat > 40)
    if len(xs):
        k = np.argsort(sat[ys, xs])[-400:]
        print(f"\nwarm accent (mean of 400 most-saturated px): {hexof(im[ys[k], xs[k]].mean(axis=0))}")
    cool = np.minimum(R, G).astype(int) - B
    ys, xs = np.nonzero(cool < -40)
    if len(xs):
        k = np.argsort(cool[ys, xs])[:400]
        print(f"cool accent  (mean of 400 most-saturated px): {hexof(im[ys[k], xs[k]].mean(axis=0))}")

    grey = (abs(R-G) < 8) & (abs(G-B) < 8) & (R > 60) & (R < 215)
    gc = collections.Counter(tuple(v) for v in im[grey][::11])
    print("\nmid greys (ticks / rules / muted text), most common first:")
    for col, n in gc.most_common(6):
        print(f"  {hexof(col)}  n={n}")


# ── bands ────────────────────────────────────────────────────────────────────
def cmd_bands(a):
    """Raised surfaces are near-white. Group them into row bands and the control
    heights and widths fall straight out of the frame."""
    im = native(a.mp4, a.t)
    H, W, _ = im.shape
    white = (im[..., 0] > a.thresh) & (im[..., 1] > a.thresh) & (im[..., 2] > a.thresh)
    x0, x1 = (int(a.frac*W), W) if a.right else (0, int(a.frac*W))
    m = np.zeros_like(white); m[:, x0:x1] = white[:, x0:x1]
    rows = np.nonzero(m.any(axis=1))[0]
    if not len(rows):
        sys.exit("no near-white pixels in that column — try --thresh lower, or --right")

    print(f"frame {W}x{H}; scanning x {x0}-{x1}; assuming a 2x capture (CSS = px/2)\n")
    print(f"{'y range':>14} {'h':>5} {'h css':>6} {'x range':>14} {'w':>5} {'w css':>6}")
    bands, s, prev = [], rows[0], rows[0]
    for r in rows[1:]:
        if r - prev > 3:
            bands.append((s, prev)); s = r
        prev = r
    bands.append((s, prev))
    for y0, y1 in bands:
        if y1 - y0 < 3:
            continue
        xs = np.nonzero(m[y0:y1+1].any(axis=0))[0]
        h, w = y1-y0+1, xs.max()-xs.min()+1
        print(f"{y0:6d}-{y1:<7d} {h:5d} {h/2:6.0f} {xs.min():6d}-{xs.max():<7d} {w:5d} {w/2:6.0f}")
    print("\nDistinct heights = the control scale. Two is a hierarchy; three on one "
          "panel usually means a mistake (components.md §1).")


# ── trace ────────────────────────────────────────────────────────────────────
COLORS = {
    "red":   lambda R, G, B: (R > 110) & (R-G > 55) & (R-B > 55),
    "blue":  lambda R, G, B: (B > 110) & (B-R > 45) & (B-G > 30),
    "green": lambda R, G, B: (G > 100) & (G-R > 35) & (G-B > 25),
    "ink":   lambda R, G, B: (R < 95) & (G < 95) & (B < 95),
}


def centerline(mask):
    ys, xs = np.nonzero(mask)
    if len(xs) < 20:
        return None
    pts = []
    if xs.max()-xs.min() >= ys.max()-ys.min():
        for x in range(xs.min(), xs.max()+1):
            yy = np.nonzero(mask[:, x])[0]
            if len(yy): pts.append((x, yy.mean()))
    else:
        for y in range(ys.min(), ys.max()+1):
            xx = np.nonzero(mask[y, :])[0]
            if len(xx): pts.append((xx.mean(), y))
    return np.array(pts, float)


def cmd_trace(a):
    """Arc length vs chord, per frame. This ratio is what separates an
    inextensible chain from an elastic string, and it is not guessable."""
    dur = duration(a.mp4)
    tmp = Path(tempfile.mkdtemp())
    sh("ffmpeg", "-v", "error", "-y", "-i", str(a.mp4),
       "-vf", f"fps={a.fps},scale=1400:-2", str(tmp/"f%03d.png"))
    test = COLORS[a.color]
    print(f"{'frame':>6} {'end A':>16} {'end B':>16} {'arc':>8} {'chord':>8} {'ratio':>7}")
    ratios, arcs = [], []
    for f in sorted(tmp.glob("f*.png")):
        im = np.asarray(Image.open(f).convert("RGB")).astype(int)
        H, W, _ = im.shape
        m = test(im[..., 0], im[..., 1], im[..., 2])
        if a.crop:
            m[:, :int(a.crop*W)] = False
        p = centerline(m)
        if p is None:
            continue
        d = np.diff(p, axis=0)
        arc = float(np.hypot(d[:, 0], d[:, 1]).sum())
        chord = float(np.hypot(*(p[-1]-p[0])))
        if chord < 1:
            continue
        ratios.append(arc/chord); arcs.append(arc)
        print(f"{f.stem:>6} ({p[0][0]:6.1f},{p[0][1]:6.1f}) ({p[-1][0]:6.1f},{p[-1][1]:6.1f}) "
              f"{arc:8.1f} {chord:8.1f} {arc/chord:7.3f}")
    if not ratios:
        sys.exit(f"no '{a.color}' stroke found — check the contact sheet, or try --crop")
    r = np.array(ratios); ar = np.array(arcs)
    print(f"\nratio  mean={r.mean():.3f}  min={r.min():.3f}  max={r.max():.3f}")
    print(f"arc    mean={ar.mean():.1f}  min={ar.min():.1f}  max={ar.max():.1f}  "
          f"({100*ar.std()/ar.mean():.1f}% variation)")
    print("\nA near-constant arc across frames = inextensible. Arc that grows 2-3x "
          "while something is dragged = elastic; build the solver accordingly "
          "(pattern-recipes.md #19).")
    print("A column/row scan averages a stroke that doubles back, so it UNDER-reports "
          "arc on a looping curve. Cross-check any surprising row against the frame.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sheet");   s.add_argument("mp4"); s.add_argument("-n", type=int, default=16)
    s.add_argument("--out"); s.set_defaults(fn=cmd_sheet)

    s = sub.add_parser("palette"); s.add_argument("mp4"); s.add_argument("-t", type=float, default=1.0)
    s.set_defaults(fn=cmd_palette)

    s = sub.add_parser("bands");   s.add_argument("mp4"); s.add_argument("-t", type=float, default=1.0)
    s.add_argument("--thresh", type=int, default=246)
    s.add_argument("--frac", type=float, default=0.30,
                   help="fraction of the width to scan (default: left 30%%)")
    s.add_argument("--right", action="store_true"); s.set_defaults(fn=cmd_bands)

    s = sub.add_parser("grounds"); s.add_argument("mp4")
    s.add_argument("--fps", type=float, default=30.0)
    s.add_argument("--cut", type=float, default=26.0,
                   help="per-frame colour delta that counts as a section change")
    s.add_argument("--inset", type=float, default=0.10,
                   help="fraction of each edge to ignore (the desktop around a capture)")
    s.set_defaults(fn=cmd_grounds)

    s = sub.add_parser("wipe");    s.add_argument("mp4")
    s.add_argument("--from", type=float, required=True, dest="from")
    s.add_argument("--to", type=float, required=True)
    s.add_argument("--dark", action="store_true",
                   help="light type on a dark ground (default: dark type on light)")
    s.add_argument("--every", type=int, default=4, help="print every Nth frame")
    s.add_argument("--delta", type=float, default=22.0,
                   help="luminance distance from the ground that counts as a glyph")
    s.add_argument("--inset", type=float, default=0.14)
    s.set_defaults(fn=cmd_wipe)

    s = sub.add_parser("trace");   s.add_argument("mp4")
    s.add_argument("--color", choices=sorted(COLORS), default="red")
    s.add_argument("--fps", type=float, default=3.0)
    s.add_argument("--crop", type=float, default=0.0,
                   help="ignore this fraction of the left edge (a UI panel)")
    s.set_defaults(fn=cmd_trace)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
