"""Contracts for the raw GKG archive scan. All inputs are synthetic fixtures."""
import hashlib, io, json, unittest, zipfile
import gdelt_gkg_archive as g


def gkg_line(gid='20220927120000-1', url='https://example.invalid/a', domain='spiegel.de', title='', locs='', tone='-3.5,1,4', trans=''):
    f = [''] * 27
    f[0], f[1], f[2], f[3], f[4] = gid, gid[:14], '1', domain, url
    f[10], f[15], f[25] = locs, tone, trans
    f[26] = f'<PAGE_TITLE>{title}</PAGE_TITLE>'
    return '\t'.join(f)


class RuleTests(unittest.TestCase):
    def test_r1_requires_russia_context(self):
        self.assertEqual(g.classify('Operation Doppelgänger: Russian hackers', '', set()), 'R1_campaign')
        self.assertEqual(g.classify('Mein Doppelgänger im Urlaub', '', {'RS'}), 'R1_campaign')
        self.assertIsNone(g.classify('Celebrity doppelganger spotted in Paris', '', {'FR'}))

    def test_r2_needs_platform_russia_and_action(self):
        self.assertEqual(g.classify('Meta disables Russian propaganda network targeting Europe', '', set()), 'R2_takedown')
        self.assertEqual(g.classify('Meta stoppt russische Falschinformations-Kampagne', '', set()), 'R2_takedown')
        self.assertIsNone(g.classify('Meta shares fall in New York trading', '', set()))
        self.assertIsNone(g.classify('Russia announces mobilisation', '', set()))

    def test_title_and_language(self):
        self.assertEqual(g.page_title('<PAGE_TITLE>Dom&#xE1;c&#xED;</PAGE_TITLE>'), 'Domácí')
        self.assertEqual(g.language('srclc:deu;eng:GT-DEU 1.0'), 'deu')
        self.assertEqual(g.language(''), 'eng')


class ParseTests(unittest.TestCase):
    def test_parse_rows_extracts_match_and_country(self):
        text = '\n'.join([
            gkg_line(title='Meta disables Russian propaganda network', locs='1#Germany#GM#GM##51#9#GM#12;1#Russia#RS#RS##60#100#RS#40'),
            gkg_line(gid='20220927120000-2', url='https://example.invalid/b', domain='unknown.invalid', title='Weather today'),
        ])
        rows = list(g.parse_rows(text, 'eng', {'spiegel.de': 'Germany'}))
        self.assertEqual([(d, c) for d, c, _, _ in rows], [('20220927', 'Germany'), ('20220927', '')])
        hit = rows[0][2]
        self.assertEqual(hit['rule'], 'R2_takedown')
        self.assertEqual(hit['tone'], -3.5)
        self.assertEqual({l['country_code'] for l in hit['locations']}, {'GM', 'RS'})
        self.assertIsNone(rows[1][2])

    def test_master_entries_filters_window_and_stream(self):
        listing = '\n'.join([
            '10 aaa http://data.gdeltproject.org/gdeltv2/20220919234500.gkg.csv.zip',
            '11 bbb http://data.gdeltproject.org/gdeltv2/20220920000000.gkg.csv.zip',
            '12 ccc http://data.gdeltproject.org/gdeltv2/20220920000000.export.CSV.zip',
            '13 ddd http://data.gdeltproject.org/gdeltv2/20221012000000.gkg.csv.zip',
        ]).encode()
        e = g.master_entries('eng', '20220920', '20221011', transport=lambda url: listing)
        self.assertEqual([(x['stamp'], x['md5'], x['size']) for x in e], [('20220920000000', 'bbb', 11)])
        self.assertTrue(e[0]['url'].startswith(g.MIRROR))

    def test_md5_mismatch_is_rejected(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('x.gkg.csv', gkg_line(title='Meta removes Russian fake network'))
        blob = buf.getvalue()
        good = {'url': 'u', 'stream': 'eng', 'md5': hashlib.md5(blob).hexdigest(), 'size': len(blob)}
        info, per_day, per_country, hits, domains = g.process(good, {}, transport=lambda url: blob)
        self.assertTrue(info['md5_verified'])
        self.assertEqual(len(hits), 1)
        with self.assertRaises(ValueError):
            g.process({**good, 'md5': '0' * 32}, {}, transport=lambda url: blob)

    def test_dedupe_by_url(self):
        self.assertEqual(len(g.dedupe([{'url': 'a'}, {'url': 'a'}, {'url': 'b'}])), 2)


if __name__ == '__main__':
    unittest.main()
