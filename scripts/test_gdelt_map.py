"""GDELT map contracts. Responses below are synthetic test fixtures, never research data."""
import datetime as dt, json, tempfile, threading, unittest, urllib.error, urllib.request
from pathlib import Path
from unittest.mock import patch
import gdelt_common as g
import fetch_gdelt_map as f
import serve_presentation as s


def fixture(n, country='Germany', prefix='a'):
    return json.dumps({'articles': [{'url': f'https://test.invalid/{prefix}{i}', 'title': 'T', 'sourcecountry': country} for i in range(n)]}).encode()


class CommonTests(unittest.TestCase):
    def test_chunks_cover_window_without_gaps(self):
        parts = g.chunks(dt.date(2022, 9, 20), dt.date(2022, 10, 11), 3)
        self.assertEqual(parts[0][0], dt.datetime(2022, 9, 20))
        self.assertEqual(parts[-1][1], dt.datetime(2022, 10, 12))
        self.assertTrue(all(a[1] == b[0] for a, b in zip(parts, parts[1:])))
        self.assertEqual(len(parts), 8)

    def test_doc_url_fixed_query(self):
        u = g.doc_url(dt.datetime(2022, 9, 20), dt.datetime(2022, 9, 23))
        self.assertIn('mode=artlist', u)
        self.assertIn('startdatetime=20220920000000', u)
        self.assertIn('enddatetime=20220922235959', u)

    def test_parse_rejects_text_and_accepts_empty(self):
        with self.assertRaises(ValueError):
            g.parse_doc(b'Please limit requests to one every 5 seconds')
        self.assertEqual(g.parse_doc(b'{}'), [])

    def test_aggregate_dedupes_urls(self):
        agg = g.aggregate([{'url': 'u1', 'sourcecountry': 'Germany'}, {'url': 'u1', 'sourcecountry': 'Germany'}, {'url': 'u2', 'sourcecountry': 'France'}])
        self.assertEqual(agg['unique_articles'], 2)
        self.assertEqual(agg['source_countries'], [{'name': 'Germany', 'count': 1}, {'name': 'France', 'count': 1}])

    def test_v2locations(self):
        rows = g.parse_v2locations('1#Germany#GM#GM##51#9#GM#12;4#Berlin, Berlin, Germany#GM#GM16#16538#52.5167#13.4#-1746443#40;bad')
        self.assertEqual([r['name'] for r in rows], ['Germany', 'Berlin, Berlin, Germany'])

    def test_chunk_param_validation(self):
        self.assertTrue(g.valid_chunk_params('20220920000000', '20220923000000'))
        self.assertFalse(g.valid_chunk_params('20220920000000', '20230923000000'))
        self.assertFalse(g.valid_chunk_params('x', '20220923000000'))


class FetchTests(unittest.TestCase):
    def test_capped_and_failed_chunks_are_reported(self):
        calls = []

        def transport(url):
            calls.append(url)
            if len(calls) == 2:
                raise OSError('network down')
            return fixture(250 if len(calls) == 1 else 3, prefix=str(len(calls)))
        with tempfile.TemporaryDirectory() as d, patch.object(f, 'OUT', Path(d)):
            snap = f.fetch_doc('meta2022', transport=transport, pause=0)
        self.assertEqual(snap['schema'], g.SCHEMA)
        self.assertEqual(snap['capped_chunks'], 1)
        self.assertEqual(snap['failed_chunks'], 0)  # second call retried successfully
        self.assertEqual(snap['unique_articles'], 250 + 3 * (len(calls) - 2))

    def test_all_failed_writes_nothing(self):
        def transport(url):
            raise OSError('blocked')
        with tempfile.TemporaryDirectory() as d, patch.object(f, 'OUT', Path(d)):
            with self.assertRaises(SystemExit):
                f.fetch_doc('recent30', transport=transport, pause=0, today=dt.date(2026, 10, 31))


class ProxyTests(unittest.TestCase):
    def test_map_chunk_endpoint(self):
        s.Handler.gateway = s.CloudGateway('')
        s.Handler.map_transport = staticmethod(lambda url: fixture(2))
        s.Handler.map_last = 0.0
        http = s.ThreadingHTTPServer(('127.0.0.1', 0), s.Handler)
        s.Handler.port = http.server_port
        t = threading.Thread(target=http.serve_forever, daemon=True)
        t.start()
        base = f'http://127.0.0.1:{http.server_port}'
        try:
            with urllib.request.urlopen(base + '/api/gdelt-map-chunk?start=20220920000000&end=20220923000000') as r:
                body = json.load(r)
            self.assertEqual(body['status'], 'ok')
            self.assertEqual(len(body['articles']), 2)
            self.assertIn('api.gdeltproject.org', body['endpoint'])
            with self.assertRaises(urllib.error.HTTPError) as e:
                urllib.request.urlopen(base + '/api/gdelt-map-chunk?start=bad&end=20220923000000')
            self.assertEqual(e.exception.code, 400)
        finally:
            s.Handler.map_transport = None
            http.shutdown(); http.server_close(); t.join()


if __name__ == '__main__':
    unittest.main()
