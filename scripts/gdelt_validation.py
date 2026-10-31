"""Validity test for the keyword rules: precision on a fixed random sample.

1) python scripts/gdelt_validation.py sample   → research/gdelt/validation_sample.csv (seed 2022)
2) Fill the `relevant` column (1 = article is about the Meta/Doppelgänger takedown or the
   campaign, 0 = not) and a short `reason`; a second coder can add `relevant_coder2`.
3) python scripts/gdelt_validation.py score    → precision with Wilson 95% interval and,
   if two coders exist, percent agreement and Cohen's kappa.
The result is embedded in the GDELT snapshot (`validation`) and shown in the deck.
"""
from __future__ import annotations
import csv, json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATCHES = ROOT / 'research/gdelt/gkg_archive/matches.jsonl'
SAMPLE = ROOT / 'research/gdelt/validation_sample.csv'
SNAPSHOT = ROOT / 'research/gdelt/GDELT_HARITA_VERISI.json'
SEED, PER_RULE = 2022, 30
FIELDS = ['rule', 'date', 'language', 'sourcecountry', 'domain', 'title', 'url', 'relevant', 'reason', 'relevant_coder2']


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def kappa(a: list[int], b: list[int]) -> float | None:
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def sample() -> list[dict]:
    seen, hits = set(), []
    for line in MATCHES.read_text().splitlines():
        h = json.loads(line)
        if h['url'] not in seen:
            seen.add(h['url'])
            hits.append(h)
    rng = random.Random(SEED)
    rows = []
    for rule in sorted({h['rule'] for h in hits}):
        pool = [h for h in hits if h['rule'] == rule]
        for h in rng.sample(pool, min(PER_RULE, len(pool))):
            rows.append({'rule': rule, 'date': h['date'], 'language': h['language'], 'sourcecountry': h['sourcecountry'],
                         'domain': h['domain'], 'title': h['title'], 'url': h['url'], 'relevant': '', 'reason': '', 'relevant_coder2': ''})
    return rows


def score(rows: list[dict]) -> dict:
    coded = [r for r in rows if r['relevant'] in ('0', '1')]
    out = {'sample_seed': SEED, 'per_rule_max': PER_RULE, 'coded': len(coded), 'by_rule': {}}
    for rule in sorted({r['rule'] for r in coded}) + ['all']:
        sub = coded if rule == 'all' else [r for r in coded if r['rule'] == rule]
        k = sum(r['relevant'] == '1' for r in sub)
        lo, hi = wilson(k, len(sub))
        out['by_rule'][rule] = {'n': len(sub), 'relevant': k, 'precision': round(k / len(sub), 3) if sub else None, 'wilson95': [round(lo, 3), round(hi, 3)]}
    two = [r for r in coded if r['relevant_coder2'] in ('0', '1')]
    if two:
        a, b = [int(r['relevant']) for r in two], [int(r['relevant_coder2']) for r in two]
        out['two_coders'] = {'n': len(two), 'agreement': round(sum(x == y for x, y in zip(a, b)) / len(two), 3), 'cohen_kappa': kappa(a, b)}
    return out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'score'
    if cmd == 'sample':
        rows = sample()
        with SAMPLE.open('w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, FIELDS)
            w.writeheader()
            w.writerows(rows)
        print(f'{len(rows)} rows → {SAMPLE.relative_to(ROOT)}')
        return
    with SAMPLE.open(encoding='utf-8') as fh:
        result = score(list(csv.DictReader(fh)))
    result['coder_note'] = 'Birinci kodlayıcı: yapay zekâ destekli ön kodlama (Claude), başlık ve URL üzerinden. Sunum öncesi en az bir insan kodlayıcının relevant_coder2 sütununu doldurması önerilir.'
    snap = json.loads(SNAPSHOT.read_text())
    snap['validation'] = result
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=1))
    print(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
