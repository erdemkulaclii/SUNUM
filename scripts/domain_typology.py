"""Reproducible typology of the 311 Meta indicator domains (first DNS label).

Classes (fixed rules, unit-tested):
  marka_birebir    first label == label of an impersonated outlet (Tian et al. 2018: wrongTLD when TLD differs)
  marka_varyant    Damerau-Levenshtein distance <= min(2, (len(outlet)-1)//2) to an outlet label (typosquatting)
  sahte_yayin      any other label: a pseudo-outlet name not belonging to an existing brand
Within sahte_yayin, a label belongs to an 'anagram family' if another distinct label has the same
multiset of letters (hyphens removed) - i.e. a letter-permuted spelling of the same phrase.
The outlet list comes from outlets named in Meta (2022) and EU DisinfoLab (2022) reporting.
"""
from __future__ import annotations
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]
# label of the real outlet's registrable domain -> outlet
OUTLETS = {'spiegel': 'Der Spiegel (spiegel.de)', 'bild': 'Bild (bild.de)', 'welt': 'Die Welt (welt.de)', 'faz': 'FAZ (faz.net)',
           'sueddeutsche': 'Süddeutsche Zeitung (sueddeutsche.de)', 't-online': 't-online (t-online.de)', 'tagesspiegel': 'Tagesspiegel (tagesspiegel.de)',
           'nd-aktuell': 'nd (nd-aktuell.de)', 'dailymail': 'Daily Mail (dailymail.co.uk)', 'theguardian': 'The Guardian (theguardian.com)',
           'ansa': 'ANSA (ansa.it)', 'repubblica': 'La Repubblica (repubblica.it)', '20minutes': '20 Minutes (20minutes.fr)',
           'delfi': 'Delfi (delfi.lv/.lt/.ee)', 'rbc': 'RBC Ukraine (rbc.ua)'}


def dl(a: str, b: str) -> int:
    """Damerau-Levenshtein (optimal string alignment) distance."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1): d[i][0] = i
    for j in range(len(b) + 1): d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            c = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + c)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def classify(label: str) -> tuple[str, str | None]:
    if label in OUTLETS:
        return 'marka_birebir', label
    best = min(OUTLETS, key=lambda o: dl(label, o))
    if dl(label, best) <= min(2, (len(best) - 1) // 2):
        return 'marka_varyant', best
    return 'sahte_yayin', None


def signature(label: str) -> str:
    return ''.join(sorted(label.replace('-', '')))


def analyse(records: list[dict]) -> dict:
    rows = []
    for r in records:
        cls, brand = classify(r['first_dns_label'])
        rows.append({**r, 'class': cls, 'brand': brand})
    pseudo = [r for r in rows if r['class'] == 'sahte_yayin']
    sig_labels = defaultdict(set)
    for r in pseudo:
        sig_labels[signature(r['first_dns_label'])].add(r['first_dns_label'])
    for r in rows:
        r['anagram_family'] = r['class'] == 'sahte_yayin' and len(sig_labels[signature(r['first_dns_label'])]) > 1
    cls = Counter(r['class'] for r in rows)
    fam = {s: sorted(v) for s, v in sig_labels.items() if len(v) > 1}
    by_cls_tld = {c: dict(Counter(r['last_dns_label'] for r in rows if r['class'] == c).most_common()) for c in cls}
    top6 = ['online', 'website', 'site', 'space', 'pw', 'fun']
    return {
        'n': len(rows), 'class_counts': dict(cls),
        'brand_exact_by_outlet': dict(Counter(r['brand'] for r in rows if r['class'] == 'marka_birebir').most_common()),
        'brand_variant_labels': dict(Counter(r['first_dns_label'] for r in rows if r['class'] == 'marka_varyant').most_common()),
        'pseudo_distinct_labels': len({r['first_dns_label'] for r in pseudo}),
        'anagram_families': len(fam), 'anagram_family_labels': sum(len(v) for v in fam.values()),
        'anagram_family_domains': sum(r['anagram_family'] for r in rows),
        'families': list(fam.values()),
        'top6_tld_by_class': {c: sum(1 for r in rows if r['class'] == c and r['last_dns_label'] in top6) for c in cls},
        'germany_by_class': {c: sum(1 for r in rows if r['class'] == c and r['source_target_label'] == 'Germany') for c in cls},
        'tld_by_class': by_cls_tld,
        'rows': [{k: r[k] for k in ('canonical_domain', 'first_dns_label', 'last_dns_label', 'source_target_label', 'class', 'brand', 'anagram_family')} for r in rows],
    }


def main():
    a = json.loads((R / 'output/IOC_YAPISAL_ANALIZ.json').read_text())
    res = analyse(a['records'])
    (R / 'output/ALAN_ADI_TIPOLOJISI.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ('rows', 'families', 'tld_by_class')}, ensure_ascii=False, indent=1))
    for f in res['families'][:12]: print(' ', f)


if __name__ == '__main__':
    main()
