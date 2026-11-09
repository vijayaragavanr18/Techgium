"""
Stage 2 — Encode each shot at each ladder rendition and measure real bytes.

For every (shot, rendition) we:
  1. Transcode with FFmpeg at target bitrate (CBR-ish via -maxrate/-bufsize).
  2. Record the ACTUAL file size (this is what a CDN would serve).
  3. Compute VMAF (TV + phone + NEG) from our quality-rate model since libvmaf
     is not compiled into this FFmpeg build. In production, replace this with
     `ffmpeg -lavfi libvmaf=model=version=vmaf_v0.6.1neg`.

Output: content/encodes/{shot_id}_{H}p.mp4   and  manifest/encode_stats.json
"""
import json
import subprocess
from pathlib import Path

from src.quality_model import SHOTS, LADDER, vmaf_tv, vmaf_phone, vmaf_neg

ENCODES = Path("content/encodes")
ENCODES.mkdir(parents=True, exist_ok=True)
MANIFEST = Path("manifest")
MANIFEST.mkdir(exist_ok=True)


def encode(shot_id, src, w, h, kbps):
    out = ENCODES / f"{shot_id}_{h}p.mp4"
    if out.exists():
        return out
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src),
        "-vf", f"scale={w}:{h}",
        "-c:v", "libx264", "-preset", "veryfast",
        "-b:v", f"{kbps}k",
        "-maxrate", f"{int(kbps*1.1)}k",
        "-bufsize", f"{kbps*2}k",
        "-g", "48",            # keyframe interval
        "-pix_fmt", "yuv420p",
        "-an",
        str(out),
    ]
    subprocess.run(cmd, check=True)
    return out


def main():
    stats = []
    for shot in SHOTS:
        src = Path(f"content/{shot.shot_id}_master.mp4")
        if not src.exists():
            raise SystemExit(f"Missing master {src} — run 01_generate_content.py first.")
        pixels = 1920 * 1080  # compute VMAF on native resolution via quality model
        for w, h, kbps in LADDER:
            out = encode(shot.shot_id, src, w, h, kbps)
            actual_bytes = out.stat().st_size
            # VMAF from quality model (would come from libvmaf in production)
            tv  = vmaf_tv(kbps, shot.complexity, h)
            ph  = vmaf_phone(kbps, shot.complexity, h)
            neg = vmaf_neg(tv)
            entry = {
                "shot_id": shot.shot_id,
                "shot_name": shot.name,
                "complexity": shot.complexity,
                "duration_s": shot.duration_s,
                "width": w, "height": h,
                "nominal_kbps": kbps,
                "actual_bytes": actual_bytes,
                "actual_kbps": round(actual_bytes * 8 / shot.duration_s / 1000, 1),
                "vmaf_tv": round(tv, 2),
                "vmaf_phone": round(ph, 2),
                "vmaf_neg": round(neg, 2),
            }
            stats.append(entry)
            print(f"  {shot.shot_id} {h:>4}p  nom={kbps:>4}kbps  real={entry['actual_kbps']:>6.1f}kbps  "
                  f"VMAF TV={tv:5.1f} ph={ph:5.1f} neg={neg:5.1f}")

    (MANIFEST / "encode_stats.json").write_text(json.dumps(stats, indent=2))
    print(f"\nWrote {MANIFEST/'encode_stats.json'} — {len(stats)} encodes")


if __name__ == "__main__":
    main()
