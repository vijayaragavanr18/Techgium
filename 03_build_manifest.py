"""
Stage 3 — Build the quality-targeted DASH-like manifest.

Standard HLS/DASH manifests only list bandwidth. Ours extends every segment
with the per-segment actual byte size AND the per-segment VMAF scores
(phone, TV, NEG) — this is the whole point of the paper.

A standard player can ignore the extra attributes and still play.
Our custom controller reads them to plan quality-first, not bitrate-first.
"""
import json
from collections import defaultdict
from pathlib import Path

ENCODE_STATS = Path("manifest/encode_stats.json")
MANIFEST_OUT = Path("manifest/manifest.json")


def main():
    stats = json.loads(ENCODE_STATS.read_text())

    # group by shot_id -> list of renditions sorted by nominal_kbps
    shots = defaultdict(list)
    for s in stats:
        shots[s["shot_id"]].append(s)
    for sid in shots:
        shots[sid].sort(key=lambda x: x["nominal_kbps"])

    # Build manifest: one segment per shot (shots == segments in our aligned design)
    manifest = {
        "version": "qtas-1.0",
        "comment": "Quality-Targeted Adaptive Streaming manifest.  "
                   "Extends HLS/DASH with per-segment byte size and VMAF (TV/phone/NEG). "
                   "Standard players ignore extra fields and still play.",
        "segments": []
    }
    order = ["s01", "s02", "s03", "s04", "s05", "s06"]
    for i, sid in enumerate(order):
        rends = shots[sid]
        seg = {
            "seg_id": i,
            "shot_id": sid,
            "shot_name": rends[0]["shot_name"],
            "duration_s": rends[0]["duration_s"],
            "complexity": rends[0]["complexity"],
            "renditions": [
                {
                    "label": f"{r['height']}p",
                    "width": r["width"], "height": r["height"],
                    "nominal_kbps": r["nominal_kbps"],
                    "bytes": r["actual_bytes"],
                    "vmaf_tv": r["vmaf_tv"],
                    "vmaf_phone": r["vmaf_phone"],
                    "vmaf_neg": r["vmaf_neg"],
                }
                for r in rends
            ],
        }
        manifest["segments"].append(seg)

    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2))
    total_bytes = sum(r["bytes"] for s in manifest["segments"] for r in s["renditions"])
    print(f"Wrote {MANIFEST_OUT}")
    print(f"  {len(manifest['segments'])} segments, "
          f"{len(manifest['segments'][0]['renditions'])} renditions each, "
          f"total catalog {total_bytes/1024/1024:.1f} MiB")


if __name__ == "__main__":
    main()
