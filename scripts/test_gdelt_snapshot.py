"""Consistency tests for the committed GDELT archive results (real data, no network)."""
import csv, json, unittest
from collections import Counter
from pathlib import Path
import gdelt_gkg_archive as g
import gdelt_validation as v

R = Path(__file__).resolve().parents[1]
SNAP = R / 'research/gdelt/GDELT_HARITA_VERISI.json'


@unittest.skipUnless(SNAP.is_file(), 'GDELT snapshot not generated yet')
class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads(SNAP.read_text())
        cls.m = json.loads((R / 'research/gdelt/gkg_archive/manifest.json').read_text())
        cls.hits = g.dedupe([json.loads(l) for l in (R / 'research/gdelt/gkg_archive/matches.jsonl').read_text().splitlines() if l])

    def test_every_archive_file_md5_verified(self):
        self.assertEqual(self.m['files_failed'], 0)
        self.assertEqual(self.m['files'], self.m['files_md5_verified'])
        self.assertTrue(all(e.get('md5_verified') and len(e['md5']) == 32 for e in self.m['entries']))
        self.assertEqual(self.m['rows_scanned'], sum(e['rows'] for e in self.m['entries']))

    def test_snapshot_matches_raw_matches(self):
        self.assertEqual(len(self.s['articles']), len(self.hits))
        self.assertEqual(sum(r['matches'] for r in self.s['daily']), len(self.hits))
        self.assertEqual(Counter(a['sourcecountry'] for a in self.s['articles']), Counter(h['sourcecountry'] for h in self.hits))

    def test_every_match_satisfies_its_rule(self):
        for h in self.hits:
            cc = {l['country_code'] for l in h['locations']}
            self.assertEqual(g.classify(h['title'], h['url'], cc), h['rule'], h['url'])

    def test_validation_recomputes_from_csv(self):
        with (R / 'research/gdelt/validation_sample.csv').open(encoding='utf-8') as fh:
            res = v.score(list(csv.DictReader(fh)))
        self.assertEqual(res['by_rule'], self.s['validation']['by_rule'])

    def test_sample_is_reproducible(self):
        with (R / 'research/gdelt/validation_sample.csv').open(encoding='utf-8') as fh:
            urls = [r['url'] for r in csv.DictReader(fh)]
        self.assertEqual(urls, [r['url'] for r in v.sample()])

    def test_figures_quoted_in_slides(self):
        n = json.loads((R / 'scripts/concise_narrative.json').read_text())
        text = json.dumps(n, ensure_ascii=False)
        us = sum(a['sourcecountry'] == 'United States' for a in self.s['articles'])
        de = sum(a['sourcecountry'] == 'Germany' for a in self.s['articles'])
        two = sum(r['matches'] for r in self.s['daily'] if r['day'] in ('20220927', '20220928'))
        for fig in [f'ABD {us}', f'Almanya {de}', f"{len(self.hits)} tekil haber", f"{self.s['distinct_titles']} farklı başlık",
                    f"%{two / len(self.hits) * 100:.1f}".replace('.', ','), f"{self.m['files']:,}".replace(',', '.') + ' dosya']:
            self.assertIn(fig, text, fig)


if __name__ == '__main__':
    unittest.main()
