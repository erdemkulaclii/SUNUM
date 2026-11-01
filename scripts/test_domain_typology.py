"""Rules of the domain typology, and the deck's figures must match the data."""
import json, unittest
from pathlib import Path
import domain_typology as dt
R = Path(__file__).resolve().parents[1]


class TypologyRules(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(dt.classify('spiegel'), ('marka_birebir', 'spiegel'))
        self.assertEqual(dt.classify('spiegeli'), ('marka_varyant', 'spiegel'))
        self.assertEqual(dt.classify('t-onlinr'), ('marka_varyant', 't-online'))
        self.assertEqual(dt.classify('rbk')[0], 'marka_varyant')
        self.assertEqual(dt.classify('rrn')[0], 'sahte_yayin')
        self.assertEqual(dt.classify('dassprachrohr')[0], 'sahte_yayin')

    def test_anagram_signature(self):
        self.assertEqual(dt.signature('dassprachrohr'), dt.signature('dassrpahcorhr'))
        self.assertNotEqual(dt.signature('dknuzsrntch'), dt.signature('denkzuerstnach'))

    def test_damerau(self):
        self.assertEqual(dt.dl('ab', 'ba'), 1)
        self.assertEqual(dt.dl('spiegel', 'spiegel'), 0)

    def test_deck_matches_data(self):
        a = json.loads((R / 'output/IOC_YAPISAL_ANALIZ.json').read_text())
        res = dt.analyse(a['records'])
        deck = {s['id']: s for s in json.loads((R / 'scripts/concise_narrative.json').read_text())}['tlds']
        bars = dict(deck['bars'])
        self.assertEqual(bars['Uydurma yayın adı'], res['class_counts']['sahte_yayin'])
        self.assertEqual(bars['Marka birebir'], res['class_counts']['marka_birebir'])
        self.assertEqual(bars['Marka varyantı'], res['class_counts']['marka_varyant'])
        self.assertIn(f"{res['top6_tld_by_class']['sahte_yayin']}’i", deck['takeaway'])


if __name__ == '__main__':
    unittest.main()
