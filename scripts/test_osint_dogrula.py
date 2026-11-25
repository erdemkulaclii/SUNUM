"""OSINT aracının ağsız testleri: bütün HTTP, DNS ve indirme yanıtları sahtedir."""
import hashlib, json, tempfile, unittest
from pathlib import Path
import osint_dogrula as od

CROSSREF_OK = {'message': {'title': ['The disinformation order: Disruptive communication and the decline of democratic institutions'],
                           'issued': {'date-parts': [[2018]]}, 'author': [{'family': 'Bennett'}]}}
RDAP = {'events': [{'eventAction': 'registration', 'eventDate': '2022-05-30T10:00:00Z'}, {'eventAction': 'expiration', 'eventDate': '2023-05-30T10:00:00Z'}],
        'status': ['client transfer prohibited'],
        'entities': [{'roles': ['registrar'], 'vcardArray': ['vcard', [['version', {}, 'text', '4.0'], ['fn', {}, 'text', 'Örnek Registrar']]]}]}


def fake_fetch(url, max_bytes):
    if 'api.crossref.org' in url:
        if '10.1177/0267323118760317' in url:
            return {'status': 200, 'final_url': url, 'body': json.dumps(CROSSREF_OK)}
        return {'status': 404, 'final_url': url, 'body': ''}
    if 'archive.org/wayback/available' in url:
        snap = {'closest': {'available': True, 'url': 'http://web.archive.org/web/20220927000000/x', 'timestamp': '20220927000000'}} if 'disinfo' in url else {}
        return {'status': 200, 'final_url': url, 'body': json.dumps({'archived_snapshots': snap})}
    if 'rdap.org' in url:
        return {'status': 200, 'final_url': url, 'body': json.dumps(RDAP)} if 'spiegel' in url else {'status': 404, 'final_url': url, 'body': ''}
    if 'cdx/search' in url:
        return {'status': 200, 'final_url': url, 'body': json.dumps([['timestamp'], ['20220801120000']]) if 'spiegel' in url else '[]'}
    if 'inmoscowsshadows' in url:
        return {'status': 200, 'final_url': url, 'body': '<title>The Gerasimov Doctrine</title> July 2014'}
    return {'status': None, 'final_url': url, 'body': '', 'error': 'URLError: sahte'}


class Parsing(unittest.TestCase):
    def test_reference_parsing(self):
        refs = od.load_references()
        self.assertEqual(len(refs), 32)
        self.assertGreaterEqual(sum(bool(r['doi']) for r in refs), 10)
        self.assertTrue(all(r['yil'] for r in refs))
        md = '# Kaynakça\n\nBennett, W. L., & Livingston, S. (2018). The disinformation order. *European Journal of Communication, 33*(2), 122–139. https://doi.org/10.1177/0267323118760317\n'
        b = od.parse_references(md)[0]
        self.assertEqual((b['ilk_yazar'], b['yil'], b['doi']), ('Bennett', '2018', '10.1177/0267323118760317'))
        self.assertTrue(all(not u.endswith('.') for r in refs for u in r['urls']))

    def test_title_match(self):
        entry = 'Bennett, W. L., & Livingston, S. (2018). The disinformation order: Disruptive communication and the decline of democratic institutions.'
        self.assertEqual(od.title_match(CROSSREF_OK['message']['title'][0], entry), 1.0)
        self.assertLess(od.title_match('Quantum chromodynamics on the lattice', entry), .3)

    def test_rdap_and_cdx(self):
        r = od.parse_rdap(json.dumps(RDAP))
        self.assertEqual((r['rdap_kayit'], r['rdap_bitis'], r['kayit_sirketi']), ('2022-05-30', '2023-05-30', 'Örnek Registrar'))
        self.assertEqual(od.parse_cdx(json.dumps([['timestamp'], ['20220801120000']])), '20220801')
        self.assertEqual(od.parse_cdx('[]'), '')


class EndToEnd(unittest.TestCase):
    def test_full_run_without_network(self):
        meta_bytes = od.META_LOCAL.read_bytes()

        def fake_bytes(url):
            if url == od.META_URL:
                return meta_bytes
            raise OSError('sahte: GDELT indirilmedi')

        with tempfile.TemporaryDirectory() as d:
            http = od.Http(None, fetch=fake_fetch, min_interval={'web.archive.org': 0, 'archive.org': 0, 'rdap.org': 0, 'api.crossref.org': 0})
            sec = od.main(['--sinir', '3'], http=http, out_dir=Path(d), resolver=lambda n: '', gdelt_fetch=fake_bytes)
            rows, claims = sec['kaynaklar']
            ben = next(r for r in rows if r['ilk_yazar'] == 'Bennett' and r['tur'] == 'DOI')
            self.assertEqual(ben['doi_durum'], 'doğrulandı')
            self.assertTrue(any(r['doi_durum'].startswith('DOI') for r in rows if r['tur'] == 'DOI'))
            self.assertEqual({c['id']: c['sonuc'] for c in claims}['GALEOTTI_2014'], 'DOĞRULANDI')
            self.assertEqual(sec['meta']['sonuc'], 'eşleşiyor')
            self.assertEqual(len(sec['haberler']), 3)
            self.assertEqual(len(sec['alanlar']), 3)
            self.assertTrue(all(r['dns_bugun'] == 'çözülmüyor' for r in sec['alanlar']))
            self.assertTrue(all(r['sonuc'].startswith('indirilemedi') for r in sec['gdelt']))
            rep = (Path(d) / 'OSINT_RAPORU.md').read_text()
            for s in ('## Kaynakça', '## Ek iddialar', '## Eşleşen haberler', '## Meta’nın 311 alan adı', '## Meta gösterge dosyası', '## GDELT örnek dosyaları'):
                self.assertIn(s, rep)
            for f in ('KAYNAK_KONTROL.csv', 'HABER_URL_KONTROL.csv', 'ALAN_ADI_KONTROL.csv', 'META_KONTROL.json', 'GDELT_KONTROL.csv', 'EK_IDDIALAR.json'):
                self.assertTrue((Path(d) / f).is_file(), f)


if __name__ == '__main__':
    unittest.main()
