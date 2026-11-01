"""Every number reported in the article, recomputed from the raw data files.

    python scripts/makale_istatistikleri.py   -> output/MAKALE_SAYILARI.json

Inputs: Meta CSV analysis (output/IOC_YAPISAL_ANALIZ.json, rebuilt from the CSV by
analyze_ioc_structure.py), domain typology (domain_typology.py), GDELT GKG scan
(research/gdelt/gkg_archive/*), validation sample (research/gdelt/validation_sample.csv).
No external statistics package is needed; exact Poisson intervals use the
gamma-quantile relation computed with a regularized incomplete gamma function.
"""
from __future__ import annotations
import csv, json, math, sys
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
import domain_typology as dt
import gdelt_validation as gv
from gdelt_gkg_archive import dedupe


def _gammainc(a: float, x: float) -> float:
    """Regularized lower incomplete gamma P(a, x)."""
    if x <= 0:
        return 0.0
    if x < a + 1:
        s = term = 1.0 / a
        n = a
        for _ in range(10000):
            n += 1
            term *= x / n
            s += term
            if abs(term) < abs(s) * 1e-15:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    b, c, d = x + 1 - a, 1e300, 1 / (x + 1 - a)
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return 1 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def gamma_ppf(p: float, a: float) -> float:
    lo, hi = 0.0, max(10.0, a * 5 + 50)
    for _ in range(200):
        mid = (lo + hi) / 2
        if _gammainc(a, mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def poisson_ci(k: int, alpha: float = .05) -> tuple[float, float]:
    lo = 0.0 if k == 0 else gamma_ppf(alpha / 2, k)
    return lo, gamma_ppf(1 - alpha / 2, k + 1)


def rnd(x: float, n: int = 1) -> float:
    return round(x, n)


def main() -> dict:
    a = json.loads((R / 'output/IOC_YAPISAL_ANALIZ.json').read_text())
    f = a['findings']
    typ = dt.analyse(a['records'])
    meta = {
        'raw_records': a['audit']['raw_records'], 'domain_rows': a['audit']['domain_rows'], 'unique_domains': a['audit']['unique_domains'],
        'duplicates_removed': a['audit']['duplicate_rows_removed'], 'target_counts': f['target_country_counts'],
        'germany_share_pct': rnd(f['target_country_counts']['Germany'] / a['audit']['unique_domains'] * 100),
        'distinct_last_labels': f['last_dns_label_count'], 'top6_domains': f['top_six_last_dns_label_domains'],
        'top6_share_pct': rnd(f['top_six_last_dns_label_share_percent']),
        'top6_labels': {r['last_dns_label']: r['domain_count'] for r in f['top_six_last_dns_labels']},
        'distinct_first_labels': f['distinct_first_dns_labels'], 'multi_suffix_families': f['multi_suffix_first_label_families'],
        'domains_in_multi_suffix_families': f['domains_in_multi_suffix_first_label_families'],
        'typology': {k: v for k, v in typ.items() if k not in ('rows', 'families')},
        'typology_share_pct': {k: rnd(v / typ['n'] * 100) for k, v in typ['class_counts'].items()},
        'anagram_family_examples': typ['families'][:6],
    }
    m = json.loads((R / 'research/gdelt/gkg_archive/manifest.json').read_text())
    tot = json.loads((R / 'research/gdelt/gkg_archive/totals.json').read_text())
    hits = dedupe([json.loads(l) for l in (R / 'research/gdelt/gkg_archive/matches.jsonl').read_text().splitlines() if l])
    n = len(hits)
    days = Counter(h['day'] for h in hits)
    den = Counter()
    for v in tot['per_source_country'].values():
        den.update(v)
    by_country = Counter(h['sourcecountry'] or 'eşleşmedi' for h in hits)
    rates = {}
    for c in ['United States', 'Germany', 'Italy', 'United Kingdom', 'France', 'Russia']:
        k, d = by_country.get(c, 0), den.get(c, 0)
        lo, hi = poisson_ci(k)
        rates[c] = {'articles': k, 'scanned': d, 'per100k': rnd(k / d * 1e5, 2), 'ci95': [rnd(lo / d * 1e5, 2), rnd(hi / d * 1e5, 2)]}
    us, de = rates['United States'], rates['Germany']
    rr = (us['articles'] / us['scanned']) / (de['articles'] / de['scanned'])
    se = math.sqrt(1 / us['articles'] + 1 / de['articles'])
    outlets = {c: len({h['domain'] for h in hits if h['sourcecountry'] == c}) for c in ['United States', 'Germany', 'Italy']}
    titles_c = {c: len({h['title'].strip().lower() for h in hits if h['sourcecountry'] == c}) for c in ['United States', 'Germany', 'Italy']}
    mention = {cc: sum(any(l['country_code'] == cc for l in h['locations']) for h in hits) for cc in ['GM', 'FR', 'IT', 'UK', 'UP', 'RS', 'US']}
    streams = Counter(e['stream'] for e in m['entries'])
    with (R / 'research/gdelt/validation_sample.csv').open(encoding='utf-8') as fh:
        val = gv.score(list(csv.DictReader(fh)))
    tones = [h['tone'] for h in hits if h['tone'] is not None]
    two = days['20220927'] + days['20220928']
    gd = {
        'window': m['window'], 'files_listed': m['files'], 'files_md5_verified': m['files_md5_verified'], 'files_failed': m['files_failed'],
        'files_by_stream': dict(streams), 'files_expected_if_complete': 22 * 96 * 2, 'rows_scanned': m['rows_scanned'],
        'matched_articles': n, 'rules': dict(Counter(h['rule'] for h in hits)),
        'day_0927': days['20220927'], 'day_0928': days['20220928'], 'two_day_share_pct': rnd(two / n * 100),
        'before_0927': sum(v for d, v in days.items() if d < '20220927'), 'after_0928': sum(v for d, v in days.items() if d > '20220928'),
        'distinct_titles': len({h['title'].strip().lower() for h in hits}), 'distinct_outlets': len({h['domain'] for h in hits}),
        'languages': dict(Counter(h['language'] for h in hits).most_common()), 'english_share_pct': rnd(sum(h['language'] == 'eng' for h in hits) / n * 100),
        'source_country_counts': dict(by_country.most_common()), 'source_countries_distinct': len([c for c in by_country if c != 'eşleşmedi']),
        'unmatched_source_country': by_country.get('eşleşmedi', 0),
        'us_share_pct': rnd(us['articles'] / n * 100), 'germany_source_share_pct': rnd(de['articles'] / n * 100),
        'rates_per_100k': rates, 'rate_ratio_us_de': rnd(rr, 2), 'rate_ratio_ci95': [rnd(math.exp(math.log(rr) - 1.96 * se), 2), rnd(math.exp(math.log(rr) + 1.96 * se), 2)],
        'outlets_by_country': outlets, 'distinct_titles_by_country': titles_c,
        'mentions': mention, 'mention_share_pct': {k: rnd(v / n * 100) for k, v in mention.items()},
        'mean_tone': rnd(sum(tones) / len(tones), 2), 'tone_n': len(tones),
        'validation': val['by_rule'],
    }
    out = {'meta': meta, 'gdelt': gd}
    (R / 'output/MAKALE_SAYILARI.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return out


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False, indent=1)[:6000])
