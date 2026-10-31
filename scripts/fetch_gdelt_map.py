"""Fetch real GDELT data for the presentation map and save a dated snapshot.

Run on your own computer (internet access to api.gdeltproject.org required):

    python scripts/fetch_gdelt_map.py                 # Meta 2022 window (default)
    python scripts/fetch_gdelt_map.py --window recent30
    python scripts/fetch_gdelt_map.py --bigquery --project MY_GCP_PROJECT   # + GKG locations

Output: research/gdelt/GDELT_HARITA_VERISI.json (+ raw responses and SHA-256
manifest). Rebuild afterwards: python scripts/build_interactive.py and
python scripts/export_editorial.py — the map then ships with this snapshot.

No observations are invented: a failed request is logged as failed, and an
all-failed run writes nothing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gdelt_common import (WINDOWS, chunks, doc_url, parse_doc, sha256, snapshot,
                          window_range, MAX_RECORDS)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research' / 'gdelt'
SNAPSHOT = OUT / 'GDELT_HARITA_VERISI.json'
PAUSE = 6.0  # GDELT asks for at most one request every 5 seconds.


def http_get(url: str, timeout: int = 60) -> bytes:
    with urlopen(Request(url, headers={'User-Agent': 'SUNUM-academic-research/3.0'}), timeout=timeout) as r:
        return r.read(20 * 1024 * 1024)


def fetch_doc(window_id: str, transport=http_get, pause: float = PAUSE, today: dt.date | None = None) -> dict:
    start, end = window_range(window_id, today)
    raw_dir = OUT / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    log, articles = [], []
    slices = chunks(start, end, WINDOWS[window_id]['chunk_days'])
    for i, (a, b) in enumerate(slices):
        url = doc_url(a, b)
        entry = {'start': a.isoformat() + 'Z', 'end': b.isoformat() + 'Z', 'endpoint': url}
        for attempt in range(3):
            try:
                raw = transport(url)
                rows = parse_doc(raw)
                name = f'doc_{window_id}_{a:%Y%m%d}_{b:%Y%m%d}.json'
                (raw_dir / name).write_bytes(raw)
                entry.update(status='ok', articles_returned=len(rows), capped=len(rows) >= MAX_RECORDS, raw_file=f'raw/{name}', sha256=sha256(raw))
                articles.extend(rows)
                break
            except Exception as exc:  # network, HTTP or schema problem
                entry.update(status='failed', error=str(exc)[:300])
                if attempt < 2:
                    time.sleep(pause * (attempt + 2))
        print(f'[{i + 1}/{len(slices)}] {entry["start"][:10]} → {entry["status"]} {entry.get("articles_returned", "")}', flush=True)
        log.append(entry)
        if i < len(slices) - 1:
            time.sleep(pause)
    if not any(c['status'] == 'ok' for c in log):
        raise SystemExit('Hiçbir GDELT isteği başarılı olmadı; anlık görüntü yazılmadı. Son hata: ' + log[-1].get('error', ''))
    return snapshot(window_id, start, end, log, articles, origin='python_fetch_gdelt_map')


def sql_literal(value: str) -> str:
    return "'" + value.replace('\\', '\\\\').replace("'", "\\'") + "'"


def fetch_gkg(snap: dict, project: str | None, dry_run: bool = False) -> dict:
    sql = (ROOT / 'scripts' / 'gdelt_gkg_locations.sql').read_text()
    urls = [a['url'] for a in snap.get('articles', [])][:2000]
    sql = sql.replace('__URL_LIST__', '[' + ', '.join(sql_literal(u) for u in urls) + ']' if urls else 'CAST([] AS ARRAY<STRING>)')
    cmd = ['bq', 'query', '--use_legacy_sql=false', '--format=json', '--max_rows=400']
    if project:
        cmd.insert(1, f'--project_id={project}')
    if dry_run:
        cmd.append('--dry_run')
    result = subprocess.run(cmd, input=sql, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise SystemExit('BigQuery sorgusu başarısız: ' + (result.stderr or result.stdout)[:500])
    if dry_run:
        print(result.stdout or result.stderr)
        return snap
    rows = json.loads(result.stdout or '[]')
    snap['locations'] = {
        'provider': 'GDELT GKG 2.0 · gdelt-bq.gdeltv2.gkg_partitioned (BigQuery)',
        'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'sql_sha256': sha256(sql.encode()),
        'matched_by': 'DOC anlık görüntüsündeki URL listesi veya başlık/URL içinde doppelgänger',
        'rows': [{'name': r['name'], 'country_code': r['country_code'], 'location_type': int(r['location_type']),
                  'lat': float(r['lat']), 'lon': float(r['lon']), 'articles': int(r['articles'])} for r in rows],
    }
    (OUT / 'gkg_locations_query.sql').write_text(sql)
    return snap


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--window', choices=sorted(WINDOWS), default='meta2022')
    p.add_argument('--bigquery', action='store_true', help='GKG anılan yer katmanını da üret (bq CLI ve GCP projesi gerekir).')
    p.add_argument('--project', help='BigQuery faturalandırma projesi')
    p.add_argument('--dry-run', action='store_true', help='BigQuery için yalnız taranacak bayt miktarını göster.')
    p.add_argument('--gkg-only', action='store_true', help='Mevcut anlık görüntüye yalnız GKG katmanını ekle.')
    a = p.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.gkg_only:
        snap = json.loads(SNAPSHOT.read_text())
    else:
        snap = fetch_doc(a.window)
    if a.bigquery or a.gkg_only:
        snap = fetch_gkg(snap, a.project, a.dry_run)
    if a.dry_run:
        return
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=1))
    print(f"Kaydedildi: {SNAPSHOT.relative_to(ROOT)} · {snap['unique_articles']} tekil haber · "
          f"{len(snap['source_countries'])} kaynak ülke · sınıra takılan dilim: {snap['capped_chunks']}")
    print('Şimdi sunumu yeniden üretin: python scripts/build_interactive.py && python scripts/export_editorial.py')


if __name__ == '__main__':
    main()
