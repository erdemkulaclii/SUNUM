"""Reproducible scan of the raw GDELT GKG 2.0 archive (English + translingual).

Why the raw archive: it is the same source the academic GDELT literature uses
(Leetaru & Schrodt, 2013), it covers 2022 without the DOC API's 3-month limit,
and every file can be checked against the MD5 GDELT publishes in
masterfilelist.txt. Anyone can rerun this script and must get identical counts.

    python scripts/gdelt_gkg_archive.py                       # 20 Sep – 11 Oct 2022
    python scripts/gdelt_gkg_archive.py --start 20220926 --end 20220929 --workers 8

Outputs (research/gdelt/gkg_archive/):
  manifest.json      every file: url, size, published MD5, verified, rows scanned
  matches.jsonl      matched articles (date, url, domain, title, rule, tone, locations, language)
  totals.json        all scanned articles per day and per source country (denominators)
and research/gdelt/GDELT_HARITA_VERISI.json for the presentation map.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import html
import io
import json
import re
import sys
import threading
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gdelt_common import parse_v2locations

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'gdelt' / 'gkg_archive'
SNAPSHOT = ROOT / 'research' / 'gdelt' / 'GDELT_HARITA_VERISI.json'
MIRROR = 'https://storage.googleapis.com/data.gdeltproject.org/'
MASTER = {'eng': MIRROR + 'gdeltv2/masterfilelist.txt', 'trans': MIRROR + 'gdeltv2/masterfilelist-translation.txt'}
DOMAINS_URL = MIRROR + 'blog/2018-news-outlets-by-country-may2018-update/MASTER-GDELTDOMAINSBYCOUNTRY-MAY2018.TXT'
DOMAINS_FILE = ROOT / 'research' / 'gdelt' / 'MASTER-GDELTDOMAINSBYCOUNTRY-MAY2018.TXT'

# ---- Matching rules (fixed, documented, unit-tested) ----------------------
CAMPAIGN = re.compile(r'doppel[\s\-]?g(?:a|ä|ae)nger', re.I)
RUSSIA = re.compile(r'russ|rusia|rusya|rosj|rosyj|rusk|росс|росі|kreml|moscow|moskau|moscou|mosca|moskwa|putin|путин', re.I)
PLATFORM = re.compile(r'\bmeta\b|facebook|instagram', re.I)
ACTION = re.compile(r'network|netzwerk|réseau|reseau|rete\b|red de|sieć|siec|ağ\b|fake|gefälscht|faux|falsi|falso|disinform|desinform|dezinform|désinform|propagand|inauthentic|campaign|kampagne|campagne|campaña|kampani|operation|operación|opération|takedown|remov|lösch|sperr|supprim|elimin|usun|clon|klon|kopie|imitat|spoof|bot', re.I)
STUDY_START, STUDY_END = '20220920', '20221011'


def classify(title: str, url: str, location_countries: set[str]) -> str | None:
    """R1: campaign name + Russia context (title/URL or GKG location RS).
    R2: platform takedown story: Meta/Facebook + Russia + network/fake/... in title or URL."""
    text = f'{title} {url}'
    if CAMPAIGN.search(text) and (RUSSIA.search(text) or 'RS' in location_countries):
        return 'R1_campaign'
    if PLATFORM.search(text) and RUSSIA.search(text) and ACTION.search(text):
        return 'R2_takedown'
    return None


def page_title(extras: str) -> str:
    m = re.search(r'<PAGE_TITLE>(.*?)</PAGE_TITLE>', extras or '', re.S)
    return html.unescape(m.group(1)).strip() if m else ''


def language(trans_info: str) -> str:
    m = re.match(r'srclc:([a-z]{3})', trans_info or '')
    return m.group(1) if m else 'eng'


def parse_rows(text: str, stream: str, domain_country: dict[str, str]):
    """Yield (row_summary, match_or_None) for each GKG record."""
    for line in text.split('\n'):
        if not line:
            continue
        f = line.split('\t')
        if len(f) < 27:
            continue
        domain = f[3].lower()
        day = f[1][:8]
        country = domain_country.get(domain, '')
        title = page_title(f[26])
        url = f[4]
        locs = parse_v2locations(f[10])
        cc = {l['country_code'] for l in locs}
        rule = classify(title, url, cc)
        hit = None
        if rule:
            tone = f[15].split(',')[0] if f[15] else ''
            hit = {'gkg_id': f[0], 'date': f[1], 'day': day, 'stream': stream, 'url': url, 'domain': domain,
                   'sourcecountry': country, 'title': title, 'rule': rule,
                   'language': language(f[25]) if stream == 'trans' else 'eng',
                   'tone': round(float(tone), 3) if tone else None,
                   'locations': [{k: l[k] for k in ('name', 'country_code', 'lat', 'lon', 'type')} for l in locs][:40]}
        yield day, country, hit


def http_get(url: str, timeout: int = 120) -> bytes:
    for attempt in range(4):
        try:
            with urlopen(Request(url, headers={'User-Agent': 'SUNUM-academic-research/3.0'}), timeout=timeout) as r:
                return r.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))


def master_entries(stream: str, start: str, end: str, transport=http_get) -> list[dict]:
    raw = transport(MASTER[stream]).decode()
    suffix = '.translation.gkg.csv.zip' if stream == 'trans' else '.gkg.csv.zip'
    out = []
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) != 3 or not parts[2].endswith(suffix):
            continue
        stamp = parts[2].rsplit('/', 1)[1][:14]
        if start <= stamp[:8] <= end and (stream == 'trans' or '.translation.' not in parts[2]):
            out.append({'stream': stream, 'stamp': stamp, 'size': int(parts[0]), 'md5': parts[1],
                        'url': parts[2].replace('http://data.gdeltproject.org/', MIRROR)})
    return sorted(out, key=lambda e: e['stamp'])


def load_domains(transport=http_get) -> tuple[dict[str, str], str]:
    if not DOMAINS_FILE.is_file():
        DOMAINS_FILE.parent.mkdir(parents=True, exist_ok=True)
        DOMAINS_FILE.write_bytes(transport(DOMAINS_URL))
    raw = DOMAINS_FILE.read_bytes()
    mapping = {}
    for line in raw.decode('utf-8', 'replace').splitlines():
        p = line.split('\t')
        if len(p) >= 3:
            mapping[p[0].strip().lower()] = p[2].strip()
    return mapping, hashlib.sha256(raw).hexdigest()


def process(entry: dict, domain_country, transport=http_get):
    blob = transport(entry['url'])
    md5 = hashlib.md5(blob).hexdigest()
    if md5 != entry['md5'] or len(blob) != entry['size']:
        raise ValueError(f"MD5/size mismatch for {entry['url']}")
    z = zipfile.ZipFile(io.BytesIO(blob))
    text = z.read(z.namelist()[0]).decode('utf-8', 'replace')
    per_day, per_country, hits, rows = Counter(), Counter(), [], 0
    for day, country, hit in parse_rows(text, entry['stream'], domain_country):
        rows += 1
        per_day[day] += 1
        per_country[country or 'unmatched'] += 1
        if hit:
            hits.append(hit)
    return {'rows': rows, 'md5_verified': True}, per_day, per_country, hits


def run(start: str, end: str, workers: int, streams: list[str]) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    domain_country, domains_sha = load_domains()
    entries = [e for s in streams for e in master_entries(s, start, end)]
    print(f'{len(entries)} archive files to scan ({start}–{end}, streams={streams})', flush=True)
    totals_day = defaultdict(Counter)
    totals_country = defaultdict(Counter)
    hits, manifest, lock, done = [], [], threading.Lock(), [0]
    t0 = time.time()

    def job(e):
        try:
            info, pd, pc, h = process(e, domain_country)
            e = {**e, **info}
        except Exception as exc:  # recorded; never silently counted as zero
            pd, pc, h = Counter(), Counter(), []
            e = {**e, 'error': str(exc)[:200], 'md5_verified': False}
        with lock:
            manifest.append(e)
            totals_day[e['stream']].update(pd)
            totals_country[e['stream']].update(pc)
            hits.extend(h)
            done[0] += 1
            if done[0] % 50 == 0 or done[0] == len(entries):
                rate = done[0] / (time.time() - t0)
                print(f'{done[0]}/{len(entries)} files · {len(hits)} matches · {rate:.1f} files/s', flush=True)

    with cf.ThreadPoolExecutor(workers) as ex:
        list(ex.map(job, entries))
    manifest.sort(key=lambda e: (e['stream'], e['stamp']))
    hits.sort(key=lambda h: (h['date'], h['url']))
    failed = [m for m in manifest if not m.get('md5_verified')]
    (OUT / 'manifest.json').write_text(json.dumps({
        'source': 'GDELT GKG 2.0 raw archive (gdeltv2/*.gkg.csv.zip and *.translation.gkg.csv.zip)',
        'mirror': MIRROR, 'window': [start, end], 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'domain_country_lookup': {'url': DOMAINS_URL, 'sha256': domains_sha},
        'files': len(manifest), 'files_md5_verified': len(manifest) - len(failed), 'files_failed': len(failed),
        'rows_scanned': sum(m.get('rows', 0) for m in manifest), 'entries': manifest}, indent=1))
    (OUT / 'totals.json').write_text(json.dumps({'per_day': {k: dict(sorted(v.items())) for k, v in totals_day.items()},
                                                'per_source_country': {k: dict(v.most_common()) for k, v in totals_country.items()}}, ensure_ascii=False, indent=1))
    with (OUT / 'matches.jsonl').open('w') as fh:
        for h in hits:
            fh.write(json.dumps(h, ensure_ascii=False) + '\n')
    print(f'Done in {time.time() - t0:.0f}s: {len(hits)} matches; {len(failed)} files failed.', flush=True)
    return build_snapshot()


def dedupe(hits: list[dict]) -> list[dict]:
    seen, out = set(), []
    for h in hits:
        if h['url'] in seen:
            continue
        seen.add(h['url'])
        out.append(h)
    return out


def build_snapshot() -> dict:
    manifest = json.loads((OUT / 'manifest.json').read_text())
    totals = json.loads((OUT / 'totals.json').read_text())
    hits = dedupe([json.loads(l) for l in (OUT / 'matches.jsonl').read_text().splitlines() if l])
    start, end = manifest['window']
    loc = defaultdict(lambda: {'articles': 0})
    for h in hits:
        for l in {(x['name'], x['country_code'], x['lat'], x['lon'], x['type']) for x in h['locations']}:
            r = loc[l]
            r.update(name=l[0], country_code=l[1], lat=l[2], lon=l[3], location_type=l[4])
            r['articles'] += 1
    all_country = Counter()
    for v in totals['per_source_country'].values():
        all_country.update(v)
    all_day = Counter()
    for v in totals['per_day'].values():
        all_day.update(v)
    day_hits = Counter(h['day'] for h in hits)
    snap = {
        'schema': 'sunum.gdelt-map/1',
        'provider': 'GDELT GKG 2.0 ham arşivi (İngilizce + çeviri akışı), MD5 doğrulamalı',
        'query': 'R1: doppelgänger + Rusya bağlamı (başlık/URL ya da GKG konumu RS) · R2: Meta/Facebook + Rusya + ağ/sahte/dezenformasyon terimleri (başlık/URL)',
        'window': {'id': 'meta2022', 'label': f'Meta duyuru penceresi · {start[6:]}.{start[4:6]} – {end[6:]}.{end[4:6]}.{end[:4]}',
                   'start': f'{start[:4]}-{start[4:6]}-{start[6:]}', 'end': f'{end[:4]}-{end[4:6]}-{end[6:]}',
                   'note': 'Ham GKG dosyaları GDELT masterfilelist MD5 değerleriyle doğrulandı.'},
        'retrieved_at': manifest['generated_at'],
        'origin': 'gkg_raw_archive',
        'archive': {'files': manifest['files'], 'files_md5_verified': manifest['files_md5_verified'],
                    'files_failed': manifest['files_failed'], 'rows_scanned': manifest['rows_scanned'],
                    'domain_country_lookup': manifest['domain_country_lookup']},
        'chunks': [], 'capped_chunks': 0, 'failed_chunks': manifest['files_failed'],
        'articles': [{k: h[k] for k in ('url', 'title', 'domain', 'sourcecountry', 'language', 'rule', 'tone')} | {'seendate': h['date']} for h in hits],
        'rules': dict(Counter(h['rule'] for h in hits)),
        'distinct_titles': len({h['title'].strip().lower() for h in hits}),
        'language_counts': dict(Counter(h['language'] for h in hits).most_common()),
        'mean_tone': round(sum(h['tone'] for h in hits if h['tone'] is not None) / max(1, sum(h['tone'] is not None for h in hits)), 2),
        'target_mentions': {cc: sum(any(l['country_code'] == cc for l in h['locations']) for h in hits) for cc in ('GM', 'UK', 'FR', 'IT', 'LG', 'UP', 'RS', 'US')},
        'daily': [{'day': d, 'matches': day_hits.get(d, 0), 'all_articles': all_day[d]} for d in sorted(all_day) if start <= d <= end],
        'country_denominators': dict(all_country.most_common()),
        'locations': {'provider': 'GDELT GKG 2.0 V2Locations (aynı eşleşen makaleler)', 'retrieved_at': manifest['generated_at'],
                      'rows': sorted(loc.values(), key=lambda r: -r['articles'])[:400]},
        'warnings': ['sourcecountry, GDELT’in 2018 alan adı–ülke listesinden gelir; haberin yayın ülkesidir, hedef ya da okur ülkesi değildir.',
                     'Eşleşme kurallı anahtar sözcük aramasıdır; geçerlilik örneklem denetimi ayrı raporlanır.',
                     'GKG yalnız GDELT’in izlediği kaynakları kapsar; kapsam ülkeler ve diller arasında eşit değildir.'],
    }
    if SNAPSHOT.is_file():
        old = json.loads(SNAPSHOT.read_text())
        if old.get('validation'):
            snap['validation'] = old['validation']
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=1))
    print(f'Snapshot: {len(hits)} unique articles → {SNAPSHOT.relative_to(ROOT)}')
    return snap


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--start', default=STUDY_START)
    p.add_argument('--end', default=STUDY_END)
    p.add_argument('--workers', type=int, default=12)
    p.add_argument('--streams', default='eng,trans')
    p.add_argument('--snapshot-only', action='store_true', help='Mevcut matches/totals dosyalarından anlık görüntüyü yeniden üret.')
    a = p.parse_args()
    if a.snapshot_only:
        build_snapshot()
    else:
        run(a.start, a.end, a.workers, a.streams.split(','))


if __name__ == '__main__':
    main()
