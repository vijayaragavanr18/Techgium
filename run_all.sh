#!/usr/bin/env bash
# Full PoC pipeline — one command.
set -euo pipefail
cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    PYTHON="python"
fi

echo "==[1/7]== Generate content (FFmpeg, 6 shots)"
"$PYTHON" 01_generate_content.py

echo "==[2/7]== Encode ladder (6 shots x 5 renditions)"
"$PYTHON" 02_encode_ladder.py

echo "==[3/7]== Build QTAS manifest"
"$PYTHON" 03_build_manifest.py

echo "==[4/7]== Simulate A/B/C/D across 8 traces x 2 devices"
"$PYTHON" 04_simulate_abr.py

echo "==[5/7]== Charts + headline"
"$PYTHON" 05_plot_results.py

echo "==[6/7]== Trace visualization"
"$PYTHON" 06_plot_traces.py

echo "==[7/7]== Equal-quality check + Pareto frontier"
"$PYTHON" 07_equal_quality.py

echo "==== Bake fresh manifest into demo.html ===="
"$PYTHON" -c "
import json, re
m = json.load(open('manifest/manifest.json'))
html = open('demo.html').read()
if '__MANIFEST_JSON__' in html:
    html = html.replace('__MANIFEST_JSON__', json.dumps(m))
else:
    html = re.sub(r'const MANIFEST = \{.*?\};', 'const MANIFEST = ' + json.dumps(m) + ';', html)
open('demo.html', 'w').write(html)
print('demo.html: fresh manifest baked in')
"

echo
echo "DONE."
echo "  results/results.csv       — full table"
echo "  results/headline.md       — key numbers"
echo "  results/equal_quality.md  — equal-quality check"
echo "  charts/*.png              — 7 charts"
echo "  demo.html                 — interactive controller demo"
