"""Records per source domain in the scan window (denominator robustness check).

Output: research/gdelt/gkg_archive/domain_volume.json  {domain: records}
Used to test whether the outlet-level comparison survives a minimum-volume threshold.
"""
import concurrent.futures as cf, hashlib, io, json, sys, zipfile
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gdelt_gkg_archive as g

def count(e):
    blob = g.http_get(e['url'])
    if hashlib.md5(blob).hexdigest() != e['md5']:
        raise ValueError('md5 ' + e['url'])
    z = zipfile.ZipFile(io.BytesIO(blob)); text = z.read(z.namelist()[0]).decode('utf-8', 'replace')
    c = Counter()
    for line in text.split('\n'):
        f = line.split('\t', 4)
        if len(f) >= 5:
            c[f[3].lower()] += 1
    return c

def main():
    entries = [e for s in ('eng', 'trans') for e in g.master_entries(s, g.STUDY_START, g.STUDY_END)]
    total = Counter(); failed = 0
    with cf.ThreadPoolExecutor(16) as ex:
        for i, r in enumerate(ex.map(lambda e: (lambda: count(e))() , entries)):
            total.update(r)
            if i % 500 == 0: print(i, len(entries), flush=True)
    (g.OUT / 'domain_volume.json').write_text(json.dumps(dict(total.most_common())))
    print('done', len(entries), 'files', sum(total.values()), 'rows', len(total), 'domains')

if __name__ == '__main__':
    main()
