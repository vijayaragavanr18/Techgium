"""
Stage 1 — Generate a synthetic test clip with 6 shots of varying complexity.

Uses FFmpeg's testsrc / mandelbrot / smptebars sources to simulate
a mixed-content title (studio → sports → close-up → credits).

Each shot is encoded as its own segment so keyframes align to shot boundaries —
this matches the paper's "shot-aware encoding" assumption.
"""
import os
import subprocess
from pathlib import Path

from src.quality_model import SHOTS

OUT = Path("content")
OUT.mkdir(exist_ok=True)

SHOT_SOURCES = {
    "s01": "testsrc=size=1920x1080:rate=24:duration={d}",                   # static
    "s02": "testsrc2=size=1920x1080:rate=24:duration={d}",                  # near-static
    "s03": "mandelbrot=size=1920x1080:rate=24:maxiter=200",                 # high motion
    "s04": "mandelbrot=size=1920x1080:rate=24:maxiter=300,hue=H=2*PI*t",    # very high motion
    "s05": "rgbtestsrc=size=1920x1080:rate=24:duration={d}",                # medium
    "s06": "smptebars=size=1920x1080:rate=24:duration={d}",                 # static
}


def encode_shot(shot):
    out = OUT / f"{shot.shot_id}_master.mp4"
    if out.exists() and out.stat().st_size > 1000:
        print(f"  skip (exists): {out}")
        return
    src = SHOT_SOURCES[shot.shot_id].format(d=shot.duration_s)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", src,
        "-t", str(shot.duration_s),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    print(f"  wrote {out} ({out.stat().st_size // 1024} KiB)")


def main():
    print("Generating 6 shots...")
    for shot in SHOTS:
        print(f"  {shot.shot_id} {shot.name}  complexity={shot.complexity}  dur={shot.duration_s}s")
        encode_shot(shot)
    print("Done.")


if __name__ == "__main__":
    main()
