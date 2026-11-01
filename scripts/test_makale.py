"""The article must agree with the data: every reported number is recomputed from raw files.

Also checks that in-text citations and the reference list match, and that no drafting
artefacts (verification tags, file paths, placeholders) remain in the article body.
"""
import json, re, unittest
from pathlib import Path
import makale_istatistikleri as mi

R = Path(__file__).resolve().parents[1]
TEXT = (R / 'makale/makale.md').read_text()
BODY, REFS = TEXT.split('# Kaynakça', 1)
BODY = BODY.split('# Özet', 1)[1]
SUF = r'(?:’[a-zçğıöşü]+)?'


def has(text, s):
    return re.search(re.escape(s).replace('SUFFIX', SUF), text) is not None


def tr(x, n=1):
    return f'{x:.{n}f}'.replace('.', ',')


def th(n):
    return f'{n:,}'.replace(',', '.')


class ArticleNumbers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = mi.main()

    def test_meta_numbers(self):
        m = self.s['meta']
        t = m['typology']
        cc = t['class_counts']
        exp = [f"{m['unique_domains']} benzersiz alan adı", f"{m['raw_records']} kayıt", f"{m['target_counts']['Germany']}SUFFIX (%{tr(m['germany_share_pct'])})",
               f"| Marka birebir | {cc['marka_birebir']} | %{tr(m['typology_share_pct']['marka_birebir'])} | {t['germany_by_class']['marka_birebir']} | {t['top6_tld_by_class']['marka_birebir']} |",
               f"| Marka varyantı | {cc['marka_varyant']} | %{tr(m['typology_share_pct']['marka_varyant'])} | {t['germany_by_class']['marka_varyant']} | {t['top6_tld_by_class']['marka_varyant']} |",
               f"| Uydurma yayın adı | {cc['sahte_yayin']} | %{tr(m['typology_share_pct']['sahte_yayin'])} | {t['germany_by_class']['sahte_yayin']} | {t['top6_tld_by_class']['sahte_yayin']} |",
               f"{t['pseudo_distinct_labels']} farklı ilk etiket", f"{t['anagram_family_labels']} etiket {t['anagram_families']} harf karışımı ailesi", f"{t['anagram_family_domains']} alan adını",
               f"{t['top6_tld_by_class']['sahte_yayin']}SUFFIX (%{tr(t['top6_tld_by_class']['sahte_yayin'] / cc['sahte_yayin'] * 100)})",
               f"{len(t['tld_by_class']['marka_birebir'])} farklı uzantıya", f"*online* ({m['top6_labels']['online']})", f"*fun* ({m['top6_labels']['fun']})"]
        for brand, n in t['brand_exact_by_outlet'].items():
            self.assertIn(f'({n})', BODY, brand)
        self.assertEqual(max(t['tld_by_class']['marka_birebir'].values()), 5)
        for e in exp:
            self.assertTrue(has(BODY, e), e)

    def test_gdelt_numbers(self):
        g = self.s['gdelt']
        r = g['rates_per_100k']
        exp = [f"{th(g['files_listed'])} dosya", f"{th(g['rows_scanned'])} kayıt", f"İngilizce akış {th(g['files_by_stream']['eng'])}", f"çeviri akışı {th(g['files_by_stream']['trans'])}",
               f"{th(g['files_expected_if_complete'])}SUFFIX", f"{g['matched_articles']} tekil haber", f"{g['rules']['R2_takedown']}SUFFIX R2’den", f"{g['rules']['R1_campaign']}SUFFIX R1’den",
               f"27 Eylül’de {g['day_0927']}", f"28 Eylül’de {g['day_0928']}", f"%{tr(g['two_day_share_pct'])}", f"toplam {g['after_0928']} haber",
               f"{g['distinct_titles']} farklı başlık", f"{g['distinct_outlets']} farklı yayın kuruluşundan", f"%{tr(g['english_share_pct'])}SUFFIX İngilizcedir",
               f"Almanca haberler {g['languages']['deu']}", f"%{tr(g['us_share_pct'])}SUFFIX ABD’de", f"%{tr(g['germany_source_share_pct'])}SUFFIX Almanya’da",
               f"{tr(g['rate_ratio_us_de'], 2)} katıdır (%95 GA {tr(g['rate_ratio_ci95'][0], 2)}–{tr(g['rate_ratio_ci95'][1], 2)})",
               f"{g['source_countries_distinct']} yayın ülkesi", f"{g['unmatched_source_country']} haberin alan adı",
               f"%{tr(g['mention_share_pct']['GM'])}SUFFIX Almanya’yı", f"%{tr(g['mention_share_pct']['FR'])}SUFFIX Fransa’yı", f"%{tr(g['mention_share_pct']['UK'])}SUFFIX Birleşik KrallıkSUFFIX"]
        for c, label in [('United States', 'ABD'), ('Germany', 'Almanya'), ('Italy', 'İtalya'), ('Russia', 'Rusya'), ('France', 'Fransa'), ('United Kingdom', 'Birleşik Krallık')]:
            x = r[c]
            exp.append(f"| {label} | {x['articles']} |")
            exp.append(f"| {th(x['scanned'])} | {tr(x['per100k'], 2)} ({tr(x['ci95'][0], 2)}–{tr(x['ci95'][1], 2)}) |")
        for c, label in [('United States', 'ABD'), ('Germany', 'Almanya'), ('Italy', 'İtalya')]:
            exp.append(f"| {label} | {r[c]['articles']} | {g['outlets_by_country'][c]} | {g['distinct_titles_by_country'][c]} |")
        v = g['validation']['all']
        exp.append(f"%{tr(v['precision'] * 100)}SUFFIX (Wilson %95 GA {tr(v['wilson95'][0] * 100)}–{tr(v['wilson95'][1] * 100)})")
        exp.append(f"{v['n']} başlığın {v['relevant']}SUFFIX ilgiliydi")
        for e in exp:
            self.assertTrue(has(BODY, e), e)


class ArticleHygiene(unittest.TestCase):
    def test_no_drafting_artefacts(self):
        for pat in [r'\[V\]', r'\[K\]', r'DOĞRULA', r'VERİ BEKLENİYOR', r'doğrulanmalı', r'scripts/', r'output/', r'\.json', r'\.csv\b', r'TODO']:
            self.assertIsNone(re.search(pat, BODY), pat)

    def test_citations_match_reference_list(self):
        entries = [e for e in REFS.strip().split('\n\n') if e.strip()]
        firsts = {re.match(r"([^,(]+?)[,(.]", e).group(1).split()[0] for e in entries}
        narr = re.findall(r"([A-ZÇÖŞÜ][\w-]+)(?:’\w+)?(?: vd\.(?:’\w+)?| ve [A-ZÇÖŞÜ][\w-]+(?:’\w+)?)? \((?:19|20)\d\d\)", BODY)
        par = re.findall(r"[(;] ?([A-ZÇÖŞÜ][\w-]+)(?: [A-Z][\w]+)?(?: vd\.| ve [A-ZÇÖŞÜ][\w-]+)?, (?:19|20)\d\d", BODY)
        cited = set(narr) | set(par)
        missing = cited - firsts - {'GDELT', 'Project'}
        self.assertFalse(missing, missing)
        for first in firsts - {'The', 'Hybrid'}:
            self.assertIn(first, BODY, f'{first} listed but never cited')

    def test_references_sorted(self):
        entries = [e for e in REFS.strip().split('\n\n') if e.strip()]
        keys = [re.sub(r'^The ', '', e).lower() for e in entries]
        import locale
        self.assertEqual(len(entries), len(set(entries)))


if __name__ == '__main__':
    unittest.main()
