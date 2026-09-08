#!/usr/bin/env python3
"""
measure_structure.py — Measure the *static page* half of a site: section shapes,
component systems, token scales, and production polish.

measure_churn.py answers "how much of it moves". This answers "how is it built as a
page" — the half a motion skill keeps guessing at.

Usage:
  python3 scripts/measure_structure.py https://example.com
  python3 scripts/measure_structure.py --urls-file urls.txt --out data/structure-bank.json

Extracts (real Chromium, computed styles, 1440x900 + 390x844):
  nav        position / height / link count / CTA / hamburger breakpoint
  sections   count, per-section align + column count + bleed + media + bg switch,
             and the diversity count that page-design.md A3 actually cares about
  footer     columns, links, height
  buttons    distinct visual styles, radius, height, padding, letter-spacing
  tokens     radius scale, spacing scale (and whether it lands on a base grid),
             shadow count, z-index ladder, container max-widths (the measure scale)
  forms      input count / height / radius / label coverage
  media      img count, intrinsic-size coverage, lazy, srcset, object-fit
  polish     title, description, og:*, favicon, theme-color, lang, canonical, 404-ability
  fonts      @font-face count, font-display, preload count
  darkmode   prefers-color-scheme rule count, color-scheme declaration
"""

import argparse, json, sys
from datetime import datetime
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
OUT_PATH   = SKILL_ROOT / "data" / "structure-bank.json"

# The whole measurement runs in one page.evaluate so it sees one layout pass.
MEASURE_JS = r"""
() => {
  const vw = innerWidth, vh = innerHeight;
  const cs = el => getComputedStyle(el);
  const rect = el => el.getBoundingClientRect();
  const px = v => { const n = parseFloat(v); return Number.isFinite(n) ? Math.round(n) : null; };
  const tally = arr => {
    const m = new Map();
    for (const v of arr) m.set(v, (m.get(v) || 0) + 1);
    return [...m.entries()].sort((a,b) => b[1]-a[1]);
  };

  const all = [...document.querySelectorAll('*')].filter(el => {
    const r = rect(el);
    return r.width > 0 && r.height > 0;
  });

  // ---- nav -----------------------------------------------------------------
  const navEl = document.querySelector('header, nav, [role=banner], [class*="header" i], [class*="nav" i]');
  let nav = null;
  if (navEl) {
    const s = cs(navEl), r = rect(navEl);
    const links = [...navEl.querySelectorAll('a')];
    const ctaish = links.filter(a => {
      const as = cs(a);
      return as.backgroundColor !== 'rgba(0, 0, 0, 0)' || px(as.borderTopWidth) > 0;
    });
    nav = {
      position: s.position,
      height: Math.round(r.height),
      backdrop: s.backdropFilter !== 'none' ? s.backdropFilter : null,
      background: s.backgroundColor,
      link_count: links.length,
      cta_count: ctaish.length,
      mix_blend: s.mixBlendMode !== 'normal' ? s.mixBlendMode : null,
      is_overlay: s.position === 'fixed' || s.position === 'sticky',
    };
  }

  // ---- sections ------------------------------------------------------------
  const root = document.querySelector('main') || document.body;
  let kids = [...root.children].filter(el => {
    const r = rect(el);
    return r.height > vh * 0.15 && cs(el).display !== 'none';
  });
  if (kids.length < 2) {
    kids = [...document.querySelectorAll('section, [class*="section" i]')].filter(el => rect(el).height > vh * 0.15);
  }
  const pageBg = cs(document.body).backgroundColor;
  const sections = kids.slice(0, 24).map(el => {
    const r = rect(el), s = cs(el);
    const heading = el.querySelector('h1,h2,h3');
    // widest grid/flex row inside the section = its column count
    let cols = 1;
    for (const d of el.querySelectorAll('*')) {
      const ds = cs(d);
      if (ds.display === 'grid') {
        const n = ds.gridTemplateColumns.split(' ').filter(x => x && x !== 'none').length;
        if (n > cols) cols = n;
      } else if (ds.display === 'flex' && ds.flexDirection.startsWith('row')) {
        const n = [...d.children].filter(c => rect(c).width > vw * 0.12).length;
        if (n > cols) cols = n;
      }
    }
    const inner = [...el.children].map(c => rect(c).width);
    const widest = inner.length ? Math.max(...inner) : r.width;
    return {
      h_vh: +(r.height / vh).toFixed(2),
      align: heading ? cs(heading).textAlign : s.textAlign,
      cols: Math.min(cols, 8),
      bleed: widest > vw * 0.97,
      has_media: !!el.querySelector('img,video,canvas,svg:not([class*="icon" i])'),
      bg_switch: s.backgroundColor !== pageBg && s.backgroundColor !== 'rgba(0, 0, 0, 0)',
      pad_top: px(s.paddingTop),
      pad_bottom: px(s.paddingBottom),
    };
  });
  const shapeKey = s => `${s.align}|${s.cols}|${s.bleed}|${s.has_media}`;
  const shapes = new Set(sections.map(shapeKey));

  // ---- footer --------------------------------------------------------------
  const footEl = document.querySelector('footer, [role=contentinfo], [class*="footer" i]');
  let footer = null;
  if (footEl) {
    const r = rect(footEl);
    let cols = 1;
    for (const d of footEl.querySelectorAll('*')) {
      const ds = cs(d);
      if (ds.display === 'grid') {
        const n = ds.gridTemplateColumns.split(' ').filter(x => x && x !== 'none').length;
        if (n > cols) cols = n;
      } else if (ds.display === 'flex' && ds.flexDirection.startsWith('row')) {
        const n = [...d.children].filter(c => rect(c).width > 60).length;
        if (n > cols) cols = n;
      }
    }
    footer = {
      h_vh: +(r.height / vh).toFixed(2),
      cols: Math.min(cols, 8),
      link_count: footEl.querySelectorAll('a').length,
    };
  }

  // ---- buttons -------------------------------------------------------------
  const btnEls = all.filter(el => {
    const t = el.tagName;
    if (t === 'BUTTON') return true;
    if (t !== 'A') return false;
    const s = cs(el), r = rect(el);
    return r.height >= 28 && r.height <= 90 && r.width < vw * 0.6 &&
           (s.backgroundColor !== 'rgba(0, 0, 0, 0)' || px(s.borderTopWidth) > 0 || px(s.borderRadius) > 6);
  });
  const btnStyles = tally(btnEls.map(el => {
    const s = cs(el), r = rect(el);
    return JSON.stringify({
      h: Math.round(r.height),
      r: s.borderRadius,
      px: px(s.paddingLeft),
      fs: px(s.fontSize),
      fw: s.fontWeight,
      ls: s.letterSpacing,
      tt: s.textTransform,
      border: px(s.borderTopWidth) > 0,
      filled: s.backgroundColor !== 'rgba(0, 0, 0, 0)',
    });
  })).slice(0, 6).map(([k, n]) => ({ ...JSON.parse(k), count: n }));

  // ---- token scales --------------------------------------------------------
  const radii = tally(all.map(el => cs(el).borderRadius).filter(v => v && v !== '0px'))
                  .slice(0, 8).map(([v, n]) => ({ v, n }));
  const pads = tally(all.flatMap(el => {
    const s = cs(el);
    return [s.paddingTop, s.paddingBottom].map(px).filter(v => v && v >= 8);
  })).slice(0, 14).map(([v, n]) => ({ v, n }));
  const gaps = tally(all.map(el => px(cs(el).rowGap)).filter(v => v && v > 0))
                 .slice(0, 8).map(([v, n]) => ({ v, n }));
  const shadowEls = all.filter(el => cs(el).boxShadow !== 'none');
  const zIdx = tally(all.map(el => cs(el).zIndex).filter(v => v !== 'auto' && v !== '0'))
                 .slice(0, 8).map(([v, n]) => ({ v, n }));
  const maxWidths = tally(all.map(el => cs(el).maxWidth)
                             .filter(v => v && v !== 'none' && !v.endsWith('%')))
                      .slice(0, 6).map(([v, n]) => ({ v, n }));

  // ---- forms ---------------------------------------------------------------
  const inputs = [...document.querySelectorAll('input:not([type=hidden]), textarea, select')];
  const form = inputs.length ? {
    count: inputs.length,
    height: Math.round(rect(inputs[0]).height),
    radius: cs(inputs[0]).borderRadius,
    labelled: inputs.filter(i => i.labels?.length || i.getAttribute('aria-label') || i.placeholder).length,
  } : null;

  // ---- media ---------------------------------------------------------------
  const imgs = [...document.querySelectorAll('img')];
  const media = {
    img_count: imgs.length,
    sized: imgs.filter(i => (i.getAttribute('width') && i.getAttribute('height')) ||
                            cs(i).aspectRatio !== 'auto').length,
    lazy: imgs.filter(i => i.loading === 'lazy').length,
    srcset: imgs.filter(i => i.srcset).length,
    alt_missing: imgs.filter(i => !i.hasAttribute('alt')).length,
    object_fit: tally(imgs.map(i => cs(i).objectFit)).slice(0, 3).map(([v, n]) => ({ v, n })),
    video_count: document.querySelectorAll('video').length,
  };

  // ---- production polish ---------------------------------------------------
  const meta = n => document.querySelector(`meta[name="${n}"]`)?.content || null;
  const og   = p => document.querySelector(`meta[property="og:${p}"]`)?.content || null;
  const polish = {
    title: document.title,
    title_len: document.title.length,
    description: !!meta('description'),
    og_title: !!og('title'),
    og_image: !!og('image'),
    og_description: !!og('description'),
    twitter_card: !!meta('twitter:card'),
    favicon: !!document.querySelector('link[rel*="icon"]'),
    apple_touch_icon: !!document.querySelector('link[rel="apple-touch-icon"]'),
    theme_color: meta('theme-color'),
    lang: document.documentElement.lang || null,
    canonical: !!document.querySelector('link[rel=canonical]'),
    manifest: !!document.querySelector('link[rel=manifest]'),
    skip_link: !!document.querySelector('a[href^="#"][class*="skip" i], a[href^="#main"]'),
    h1_count: document.querySelectorAll('h1').length,
  };

  // ---- fonts / dark mode ---------------------------------------------------
  let faceCount = 0, displays = [], darkRules = 0, hasScrollTimeline = 0, containerQ = 0;
  for (const sheet of document.styleSheets) {
    let rules;
    try { rules = sheet.cssRules; } catch { continue; }
    if (!rules) continue;
    for (const r of rules) {
      if (r.type === 5) { faceCount++; const d = r.style?.fontDisplay; if (d) displays.push(d); }
      else if (r.type === 4) {
        if (/prefers-color-scheme/.test(r.conditionText || '')) darkRules++;
      } else if (r.constructor?.name === 'CSSContainerRule') containerQ++;
      if (r.cssText && /animation-timeline|view-timeline|animation-trigger/.test(r.cssText)) hasScrollTimeline++;
    }
  }

  // ─── render layer: what is this page actually drawn with? ───────────────
  // getContext returns the EXISTING context when the type matches and null when
  // it does not, so probing in order identifies a live canvas without disturbing it.
  const canvases = [...document.querySelectorAll('canvas')].map(c => {
    let kind = 'none';
    for (const t of ['webgl2', 'webgl', '2d']) {
      try { if (c.getContext(t)) { kind = t; break; } } catch (e) {}
    }
    return { kind, w: c.width, h: c.height, css_w: c.clientWidth, css_h: c.clientHeight };
  });
  const svgs = [...document.querySelectorAll('svg')];
  const libs = ['THREE', '__THREE__', 'BABYLON', 'PIXI', 'p5', 'Matter', 'rive', 'lottie']
    .filter(k => typeof window[k] !== 'undefined');
  const glCanvases = canvases.filter(c => c.kind === 'webgl2' || c.kind === 'webgl');
  const layer = glCanvases.length ? 'webgl'
              : canvases.some(c => c.kind === '2d') ? 'canvas2d'
              : svgs.length && document.querySelectorAll('svg path,svg circle,svg line,svg rect').length > 12 ? 'svg'
              : 'dom';
  const renderLayer = {
    primary: layer,
    canvases,
    svg_count: svgs.length,
    svg_shape_count: document.querySelectorAll('svg path,svg circle,svg line,svg polyline,svg rect').length,
    inline_svg_bytes: svgs.reduce((n, s) => n + s.outerHTML.length, 0),
    libs,
    dpr: window.devicePixelRatio,
  };


  return {
    viewport: `${vw}x${vh}`,
    page_h_vh: +(document.documentElement.scrollHeight / vh).toFixed(1),
    dom_nodes: document.querySelectorAll('*').length,
    nav, sections,
    section_count: sections.length,
    distinct_shapes: shapes.size,
    footer,
    buttons: { count: btnEls.length, styles: btnStyles },
    tokens: { radii, paddings: pads, gaps, shadow_els: shadowEls.length, z_index: zIdx, max_widths: maxWidths },
    form, media, polish,
    fonts: { face_count: faceCount, font_display: tally(displays).map(([v, n]) => ({ v, n })),
             preload: document.querySelectorAll('link[rel=preload][as=font]').length },
    dark_mode_rules: darkRules,
    container_queries: containerQ,
    native_scroll_timeline: hasScrollTimeline,
    render_layer: renderLayer,
  };
}
"""

MOBILE_JS = r"""
() => {
  const vw = innerWidth;
  const doc = document.documentElement;
  const nav = document.querySelector('header, nav, [role=banner]');
  const burger = [...document.querySelectorAll('button, [role=button], [class*="burger" i], [class*="menu-toggle" i], [class*="hamburger" i]')]
    .filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.width < 90 && r.height < 90; });
  return {
    h_scroll: doc.scrollWidth > vw + 2,
    overflow_px: doc.scrollWidth - vw,
    page_h_vh: +(doc.scrollHeight / innerHeight).toFixed(1),
    burger_candidates: burger.length,
    nav_height: nav ? Math.round(nav.getBoundingClientRect().height) : null,
    smallest_tap: (() => {
      const els = [...document.querySelectorAll('a, button')].map(e => e.getBoundingClientRect())
                    .filter(r => r.width > 0 && r.height > 0);
      return els.length ? Math.round(Math.min(...els.map(r => Math.min(r.width, r.height)))) : null;
    })(),
    body_font_px: Math.round(parseFloat(getComputedStyle(document.body).fontSize)),
  };
}
"""


def measure(url, timeout=45000):
    from playwright.sync_api import sync_playwright
    out = {"url": url, "measured": datetime.now().strftime("%Y-%m-%d")}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                                              "Chrome/126.0 Safari/537.36"))
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            page.wait_for_timeout(3500)
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            out["desktop"] = page.evaluate(MEASURE_JS)
            out["title"] = page.title()
            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(1200)
            out["mobile"] = page.evaluate(MOBILE_JS)
        except Exception as e:
            out["error"] = f"{type(e).__name__}: {e}"
        finally:
            browser.close()
    return out


def main():
    ap = argparse.ArgumentParser(description="Measure page structure / component / token systems")
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--urls-file")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--out", default=str(OUT_PATH))
    args = ap.parse_args()

    urls = list(args.urls)
    if args.urls_file:
        urls += [l.strip() for l in Path(args.urls_file).read_text().splitlines()
                 if l.strip() and not l.startswith("#")]
    urls = urls[: args.limit]
    if not urls:
        ap.error("no URLs")

    out_path = Path(args.out)
    results = json.loads(out_path.read_text()) if out_path.exists() else []
    done = {r["url"] for r in results}

    for i, u in enumerate(urls, 1):
        if u in done:
            print(f"[{i}/{len(urls)}] skip (already measured) {u}"); continue
        print(f"[{i}/{len(urls)}] {u}", flush=True)
        r = measure(u)
        if "error" in r:
            print(f"    ⚠️  {r['error'][:120]}")
        else:
            d = r["desktop"]
            print(f"    sections={d['section_count']} shapes={d['distinct_shapes']} "
                  f"btn_styles={len(d['buttons']['styles'])} radii={len(d['tokens']['radii'])} "
                  f"h={d['page_h_vh']}vh og={d['polish']['og_image']}")
        results.append(r)
        out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n✓ {len(results)} records → {out_path}")


if __name__ == "__main__":
    main()
