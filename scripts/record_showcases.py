#!/usr/bin/env python3
import asyncio, os, shutil, time, subprocess, glob
from playwright.async_api import async_playwright
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES_DIR = os.path.join(ROOT, "cases")
ASSETS_DIR = os.path.join(ROOT, "assets", "cases")
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1440, 900

async def smooth_move(pg, x0, y0, x1, y1, dur, steps=25):
    t0 = time.time()
    for s in range(1, steps + 1):
        k = s / steps
        k = k * k * (3 - 2 * k)
        await pg.mouse.move(x0 + (x1 - x0) * k, y0 + (y1 - y0) * k)
        dt = t0 + dur * (s / steps) - time.time()
        if dt > 0:
            await pg.wait_for_timeout(int(dt * 1000))

async def sweep_path(pg, pts, dur):
    n = len(pts) - 1
    per = dur / n
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        await smooth_move(pg, x0, y0, x1, y1, per)

async def record_case(b, name, drive_func):
    d = os.path.join(ASSETS_DIR, f"tmp_{name}")
    shutil.rmtree(d, ignore_errors=True)
    
    html_path = os.path.join(CASES_DIR, name, "index.html")
    ctx = await b.new_context(
        viewport={"width": W, "height": H},
        record_video_dir=d,
        record_video_size={"width": W, "height": H}
    )
    pg = await ctx.new_page()
    await pg.goto("file://" + html_path, wait_until="load")
    
    if name == "press-stack":
        await pg.wait_for_timeout(2500)
    else:
        await pg.wait_for_timeout(1000)
        
    thumb_path = os.path.join(ASSETS_DIR, f"{name}.png")
    await pg.screenshot(path=thumb_path)
    
    await drive_func(pg)
    await pg.wait_for_timeout(1000)
    
    await ctx.close()
    
    webms = [f for f in os.listdir(d) if f.endswith(".webm")]
    if not webms:
        print(f"Error: no webm recorded for {name}")
        shutil.rmtree(d, ignore_errors=True)
        return
    raw_webm = os.path.join(d, webms[0])
    
    gif_path = os.path.join(ASSETS_DIR, f"{name}.gif")
    
    # 720x450 at 16fps with palettegen
    vf_gif = "fps=16,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:reserve_transparent=0[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw_webm, "-vf", vf_gif, gif_path], check=True)
    
    # Generate animated WebP via Pillow for ultra-smooth rendering
    frames_dir = os.path.join(d, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw_webm, "-vf", "fps=18,scale=720:-1:flags=lanczos", f"{frames_dir}/%04d.png"], check=True)
    frame_files = sorted(glob.glob(f"{frames_dir}/*.png"))
    if frame_files:
        imgs = [Image.open(f) for f in frame_files]
        webp_path = os.path.join(ASSETS_DIR, f"{name}.webp")
        imgs[0].save(webp_path, format="WEBP", save_all=True, append_images=imgs[1:], duration=int(1000/18), loop=0, quality=75)
        print(f"Recorded {name} -> {os.path.getsize(gif_path)//1024}KB GIF, {os.path.getsize(webp_path)//1024}KB WebP")
    else:
        print(f"Recorded {name} -> {os.path.getsize(gif_path)//1024}KB GIF")

    shutil.rmtree(d, ignore_errors=True)

async def drive_string_clock(pg):
    await sweep_path(pg, [(720, 650), (1050, 350), (450, 400), (950, 700), (720, 450)], 3.0)

async def drive_ink_crowd(pg):
    await sweep_path(pg, [(250, 350), (1150, 280), (700, 200), (300, 600), (1100, 650)], 3.5)

async def drive_press_stack(pg):
    for _ in range(8):
        await pg.mouse.wheel(0, 300)
        await pg.wait_for_timeout(250)

async def drive_wheel_rail(pg):
    for i in range(7):
        await pg.mouse.wheel(0, 320)
        await pg.mouse.move(500 + i * 50, 400 + (i % 3) * 60)
        await pg.wait_for_timeout(260)

async def drive_toy_flipbook(pg):
    await sweep_path(pg, [(260, 450), (1180, 450), (350, 450), (900, 450)], 3.2)

async def drive_char_curtain(pg):
    await sweep_path(pg, [(180, 470), (1260, 430), (320, 520), (800, 450)], 3.2)

async def drive_lyre_crows(pg):
    await sweep_path(pg, [(280, 300), (1120, 450), (320, 580)], 2.5)
    await pg.mouse.move(60, 60)
    await pg.wait_for_timeout(1800)

DRIVERS = {
    "string-clock": drive_string_clock,
    "ink-crowd": drive_ink_crowd,
    "press-stack": drive_press_stack,
    "wheel-rail": drive_wheel_rail,
    "toy-flipbook": drive_toy_flipbook,
    "char-curtain": drive_char_curtain,
    "lyre-crows": drive_lyre_crows,
}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, fn in DRIVERS.items():
            print(f"Recording {name}...")
            await record_case(b, name, fn)
        await b.close()
    print("All showcases recorded successfully.")

if __name__ == "__main__":
    asyncio.run(main())
