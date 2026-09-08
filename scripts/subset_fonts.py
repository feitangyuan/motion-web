#!/usr/bin/env python3
"""
subset_fonts.py — inline real type into a single-file case.

Eight of this skill's first cases shipped 0 @font-face and fell back to the
system stack. That is the single loudest tell that a page was generated:
render-layer.md §2 measured the references and every one of them ships web
fonts (CO'WATCH 69, overheardhq 8, ibuongiorno 4). A case is a single HTML file
with no network, so the only way to ship type is to subset it and inline it.

  # what is available on this machine, and under what licence
  python3 scripts/subset_fonts.py list

  # subset to the characters a case actually uses, print @font-face blocks
  python3 scripts/subset_fonts.py pack --out /tmp/faces.css \\
      Grot=Inter-Variable Ital=InstrumentSerif-Italic Mono=IBMPlexMono-Regular

  # subset against one page's real text instead of the default ASCII set
  python3 scripts/subset_fonts.py pack --text-from cases/foo/index.html ...

Only OFL / Apache families are listed. macOS system faces (Helvetica, Didot,
Futura, Georgia…) are licensed for system use and must not be embedded in a
file you hand to anyone, so they are deliberately not searchable here.

Requires: fonttools with brotli (`python3 -m pip install fonttools brotli`).
"""
import argparse, base64, re, subprocess, sys
from pathlib import Path

# Open-licensed faces, in the order they are usually wanted. Extend freely;
# every entry must be OFL or Apache-2.0.
ROOTS = [
    Path.home() / ".workbuddy-ai/plugins/marketplaces/codebuddy-plugins-official"
                  "/external_plugins/canvas-design/canvas-fonts",
    Path.home() / "Downloads",
    Path.home() / ".claude/skills/motion-web/assets/fonts",
]
ASCII = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
         ".,:;!?°·—–-/()[]&+@%#*\"'’‘“”")


def candidates():
    seen = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for f in sorted(root.rglob("*.[to]tf")):
            if any(s in str(f) for s in ("/System/", "Library/Fonts", "node_modules")):
                continue
            seen.setdefault(f.stem, f)
    return seen


def cmd_list(a):
    c = candidates()
    if not c:
        sys.exit("no open-licensed faces found. Drop OFL .ttf/.otf files into "
                 f"{ROOTS[-1]} and re-run.")
    print(f"{len(c)} faces found:\n")
    for stem, path in sorted(c.items()):
        kind = ("variable" if "Variable" in stem or "VF" in stem else
                "italic" if "Italic" in stem else "upright")
        print(f"  {stem:<38} {kind:<9} {path.parent}")
    print("\nName them on the pack command as CSSName=FileStem, e.g."
          "\n  pack Grot=Inter-Variable Ital=InstrumentSerif-Italic")


def charset(a):
    if not a.text_from:
        return ASCII
    src = Path(a.text_from).read_text(errors="ignore")
    src = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", src, flags=re.I)
    src = re.sub(r"<[^>]+>", " ", src)
    chars = sorted(set(src) - set("\n\r\t"))
    text = "".join(c for c in chars if c.isprintable())
    print(f"   charset from {a.text_from}: {len(text)} distinct characters")
    if len(text) < 60:
        print("   WARNING: that is fewer characters than the alphabet. Script tags are\n"
              "   stripped, so a page whose copy lives in JS strings will subset to\n"
              "   almost nothing and render tofu for everything else. Drop --text-from.")
    return text


def cmd_pack(a):
    c = candidates()
    text = charset(a)
    out, total = [], 0
    for spec in a.faces:
        if "=" not in spec:
            sys.exit(f"expected CSSName=FileStem, got {spec!r}")
        name, stem = spec.split("=", 1)
        # tolerate a partial stem, so Inter-Variable finds the real filename
        hit = c.get(stem) or next((p for s, p in c.items() if stem.lower() in s.lower()), None)
        if not hit:
            sys.exit(f"no open face matching {stem!r} — run `list` to see what is here")
        dst = Path(a.tmp or "/tmp") / f"{name}.woff2"
        dst.parent.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, "-m", "fontTools.subset", str(hit), f"--text={text}",
               "--flavor=woff2", f"--output-file={dst}"]
        if "Variable" in hit.stem or "VF" in hit.stem:
            cmd.append("--layout-features=*")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"subset failed for {hit.name}\n{r.stderr[-500:]}")
        raw = dst.read_bytes(); total += len(raw)
        b64 = base64.b64encode(raw).decode()
        italic = "italic" if "Italic" in hit.stem else "normal"
        weight = "100 900" if ("Variable" in hit.stem or "VF" in hit.stem) else "400"
        out.append(f'@font-face{{font-family:"{name}";'
                   f'src:url(data:font/woff2;base64,{b64}) format("woff2");'
                   f'font-weight:{weight};font-style:{italic};font-display:swap}}')
        print(f"   {name:<8} {hit.stem:<34} {len(raw):>7} bytes  "
              f"weight {weight}  {italic}")
    css = "\n".join(out)
    if a.out:
        Path(a.out).write_text(css)
        print(f"\n   {len(out)} faces, {total} bytes raw, "
              f"{len(css)} chars of CSS -> {a.out}")
        print("   Paste it at the very top of the case's <style>, before :root.")
    else:
        print(css)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("list"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("pack")
    s.add_argument("faces", nargs="+", help="CSSName=FileStem, one per face")
    s.add_argument("--out", help="write the @font-face blocks here")
    s.add_argument("--text-from", help="an HTML file whose text decides the charset")
    s.add_argument("--tmp", help="where to leave the .woff2 files")
    s.set_defaults(fn=cmd_pack)
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
