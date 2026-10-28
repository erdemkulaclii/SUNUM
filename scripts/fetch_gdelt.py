"""Download real GDELT DOC responses; never substitute synthetic observations.

Run: python scripts/fetch_gdelt.py --start 20260730000000 --end 20261027235959
DOC API retention is limited: old dates require GKG archives/BigQuery instead.
Network access to api.gdeltproject.org must be enabled in environment settings.
"""
import argparse, datetime, hashlib, json, pathlib, urllib.parse, urllib.request

p = argparse.ArgumentParser()
p.add_argument('--start', required=True)
p.add_argument('--end', required=True)
a = p.parse_args()
for date in (a.start, a.end):
    datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
assert a.start < a.end
root = pathlib.Path(__file__).resolve().parents[1] / 'research' / 'gdelt'
root.mkdir(parents=True, exist_ok=True)
query = '(Doppelganger OR "Doppelgänger" OR "Portal Kombat" OR "Voice of Europe")'
manifest = []
for mode in ('artlist', 'timelinevolraw'):
    params = dict(query=query, mode=mode, format='json', startdatetime=a.start,
                  enddatetime=a.end, maxrecords=250, sort='datedesc')
    url = 'https://api.gdeltproject.org/api/v2/doc/doc?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            raw = r.read()
        obj = json.loads(raw)
        if mode == 'artlist' and not isinstance(obj.get('articles'), list):
            raise ValueError('Response has no articles list; not accepted as data')
        if mode == 'timelinevolraw' and not isinstance(obj.get('timeline'), list):
            raise ValueError('Response has no timeline list; not accepted as data')
    except Exception as exc:
        raise SystemExit(f'GDELT FETCH FAILED ({mode}): {exc}. No observations generated.')
    path = root / f'{mode}_{a.start}_{a.end}.json'
    path.write_bytes(raw)
    manifest.append(dict(url=url, file=path.name, sha256=hashlib.sha256(raw).hexdigest(),
                         fetched_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    print(mode, 'saved; capped article selection is not a complete corpus')
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
print('These responses are not automatically classified as disinformation or target geography.')
