"""Outlet-level Germany/US comparison under minimum-volume thresholds.

Inputs: research/gdelt/gkg_archive/domain_volume.json (scripts/gdelt_domain_volume.py),
matches.jsonl and the GDELT domain-country lookup. Output: output/ESIK_DAYANIKLILIGI.json
"""
import json, math, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gdelt_gkg_archive as g

THRESHOLDS = (1, 5, 10, 25, 50, 100, 250, 500, 1000)


def main():
    dc, _ = g.load_domains()
    vol = json.loads((g.OUT / 'domain_volume.json').read_text())
    hit = defaultdict(set)
    for line in (g.OUT / 'matches.jsonl').read_text().splitlines():
        if line:
            h = json.loads(line); hit[h['sourcecountry']].add(h['domain'])
    rows = []
    for th in THRESHOLDS:
        r = {}
        for c in ('Germany', 'United States'):
            n = sum(1 for d, v in vol.items() if dc.get(d) == c and v >= th)
            k = sum(1 for d in hit[c] if vol.get(d, 0) >= th)
            r[c] = (k, n)
        (a, b), (c2, d2) = r['Germany'], r['United States']
        rr = (a / b) / (c2 / d2); se = math.sqrt(1 / a - 1 / b + 1 / c2 - 1 / d2)
        rows.append({'min_records': th, 'germany': [a, b], 'united_states': [c2, d2],
                     'ratio_de_us': round(rr, 2), 'ci95': [round(rr * math.exp(-1.96 * se), 2), round(rr * math.exp(1.96 * se), 2)]})
        print(rows[-1])
    (g.ROOT / 'output' / 'ESIK_DAYANIKLILIGI.json').write_text(json.dumps(rows, indent=1))


if __name__ == '__main__':
    main()
