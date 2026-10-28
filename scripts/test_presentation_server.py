"""Server contracts use dummy credentials and bounded synthetic API responses."""
import unittest,json,tempfile,threading,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
import serve_presentation as s
class ServerTests(unittest.TestCase):
 def test_cloud_budget_cache_and_redaction(self):
  calls=[];key='TEST_ONLY_PRIVATE_VALUE'
  def transport(path,params,provided):
   self.assertEqual(provided,key);calls.append(params)
   return {'data':[{'id':'TEST_EVENT','summary':key}],'applied_filters':{k:params[k] for k in ['search','date_start','date_end']},'pagination':{'next_cursor':None}},{'fetched_at_utc':'2026-10-28T10:00:00Z'}
  with tempfile.TemporaryDirectory() as d,patch.object(s,'O',Path(d)):
   g=s.CloudGateway(key,transport);a=g.get();b=g.get();self.assertEqual(len(calls),1);self.assertEqual(calls[0]['limit'],10);self.assertTrue(b['gateway_cache']);self.assertNotIn(key,json.dumps(a));self.assertEqual(a['status'],'ok')
 def test_no_key_no_calls(self):
  with tempfile.TemporaryDirectory() as d,patch.object(s,'O',Path(d)):
   a=s.CloudGateway('').get();self.assertEqual(a['status'],'key_not_configured');self.assertNotIn('result',a)
 def test_error_not_empty_data(self):
  def fail(*args):raise s.CloudError('HTTP 401: Anahtar reddedildi.')
  with tempfile.TemporaryDirectory() as d,patch.object(s,'O',Path(d)):
   a=s.CloudGateway('TEST_ONLY',fail).get();self.assertEqual(a['status'],'credential_rejected');self.assertNotIn('result',a)
 def test_http_secret_and_origin_boundary(self):
  with tempfile.TemporaryDirectory() as d,patch.object(s,'O',Path(d)):
   s.Handler.gateway=s.CloudGateway('TEST_ONLY');http=s.ThreadingHTTPServer(('127.0.0.1',0),s.Handler);s.Handler.port=http.server_port;t=threading.Thread(target=http.serve_forever,daemon=True);t.start();base=f'http://127.0.0.1:{http.server_port}'
   try:
    with urllib.request.urlopen(base+'/health') as r:body=json.load(r)
    self.assertTrue(body['cloud_key_configured']);self.assertFalse(body['key_exposed'])
    for path in ['/.env','/../.env','/scripts/serve_presentation.py']:
     with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(base+path)
     self.assertEqual(e.exception.code,404)
    with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(urllib.request.Request(base+'/health',headers={'Origin':'https://example.invalid'}))
    self.assertEqual(e.exception.code,403)
   finally:http.shutdown();http.server_close();t.join()
if __name__=='__main__':unittest.main()
