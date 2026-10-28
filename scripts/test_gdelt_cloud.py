"""Synthetic contract tests. No real credentials, network or research observations."""
import copy,io,json,unittest
from fetch_gdelt_cloud import collect,request_json,CloudError
PARAMS={'search':'TEST_ONLY','date_start':'2026-10-21','date_end':'2026-10-27','limit':10}
def body(cursor=None,rows=None):
 return {'data':rows if rows is not None else [{'id':'TEST_EVENT_ONLY'}],
         'applied_filters':copy.deepcopy(PARAMS),
         'pagination':{'next_cursor':cursor,'has_more':cursor is not None},
         'meta':{'coverage':{'missing_dates':['2026-10-22']}}}
class ContractTests(unittest.TestCase):
 def test_one_page_partial_preserves_coverage(self):
  result=collect('TEST_NOT_A_CREDENTIAL',PARAMS,transport=lambda *a:(body('opaque'),{}))
  self.assertFalse(result['pagination_complete']);self.assertIsNone(result['coverage_complete'])
  self.assertEqual(result['stop_reason'],'request_budget')
  self.assertEqual(result['pages'][0]['response']['meta']['coverage']['missing_dates'],['2026-10-22'])
 def test_scope_and_limit_frozen_and_rows_deduplicated(self):
  calls=[]
  def transport(path,p,key):
   calls.append(copy.deepcopy(p));return (body('opaque') if len(calls)==1 else body(None,[{'id':'TEST_EVENT_ONLY'},{'id':'TEST_EVENT_2'}])),{}
  result=collect('TEST_NOT_A_CREDENTIAL',PARAMS,2,transport)
  self.assertEqual(len(result['data']),2);self.assertTrue(result['pagination_complete'])
  self.assertEqual(calls[1],{**PARAMS,'cursor':'opaque'})
 def test_ignored_filters_fail(self):
  b=body();b['applied_filters']['ignored']=['search']
  with self.assertRaises(CloudError):collect('TEST',PARAMS,transport=lambda *a:(b,{}))
 def test_absent_cursor_not_complete(self):
  b=body();b['pagination']={}
  with self.assertRaises(CloudError):collect('TEST',PARAMS,transport=lambda *a:(b,{}))
 def test_changed_date_fails(self):
  b=body();b['applied_filters']['date_start']='2026-01-01'
  with self.assertRaises(CloudError):collect('TEST',PARAMS,transport=lambda *a:(b,{}))
 def test_cursor_does_not_advance(self):
  with self.assertRaises(CloudError):collect('TEST',PARAMS,2,lambda *a:(body('same'),{}))
 def test_arbitrary_endpoint_rejected(self):
  with self.assertRaises(CloudError):request_json('https://example.invalid/',{},'TEST')
 def test_credentials_only_in_header_and_echo_redacted(self):
  token='TEST_NOT_A_CREDENTIAL'
  class Response(io.BytesIO):
   headers={'X-Quota-Cost':'1'}
  class Opener:
   def open(self,request,timeout):
    assert request.full_url.startswith('https://gdeltcloud.com/api/v2/')
    assert token not in request.full_url
    assert request.get_header('Authorization')=='Bearer '+token
    return Response(json.dumps({'echo':token}).encode())
  response,_=request_json('/meta/endpoints',{},token,Opener())
  self.assertEqual(response['echo'],'[REDACTED]')
if __name__=='__main__':unittest.main()
