"""GDELT Cloud REST v2 collector. Key stays in environment or an interactive prompt.

Examples:
  python scripts/fetch_gdelt_cloud.py
  python scripts/fetch_gdelt_cloud.py --prompt-key
Do not pass a key on the command line or put it in source / exported HTML.
"""
import argparse,datetime as dt,getpass,hashlib,json,os,pathlib,sys,urllib.error,urllib.parse,urllib.request

BASE='https://gdeltcloud.com/api/v2'
ALLOWED={'/meta/endpoints','/meta/query-units','/events'}
class CloudError(Exception):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None

def request_json(path,params,key,opener=None):
 if path not in ALLOWED:raise CloudError('Belgelendirilmemiş uç nokta reddedildi.')
 if not key or any(ord(c)<33 or ord(c)>126 for c in key):raise CloudError('Gizli değişken boş veya geçersiz karakter içeriyor.')
 url=BASE+path+('?' + urllib.parse.urlencode(params) if params else '')
 req=urllib.request.Request(url,headers={'Authorization':'Bearer '+key,'Accept':'application/json','User-Agent':'SUNUM-OSINT-Atlas/1.0'})
 opener=opener or urllib.request.build_opener(NoRedirect())
 try:
  with opener.open(req,timeout=45) as response:
   raw=response.read(10*1024*1024+1)
   if len(raw)>10*1024*1024:raise CloudError('Yanıt 10 MB sınırını aşıyor.')
   # Never persist a credential even if a remote server unexpectedly echoes it.
   text=raw.decode('utf-8').replace(key,'[REDACTED]')
   try:body=json.loads(text)
   except ValueError:raise CloudError('Servis geçerli JSON dönmedi.') from None
   if not isinstance(body,dict):raise CloudError('Yanıt nesne biçiminde değil.')
   if body.get('success') is False:raise CloudError('GDELT Cloud hata yanıtı verdi; veri sayılmadı.')
   return body,{'url':url,'fetched_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'quota_cost_upper_bound':response.headers.get('X-Quota-Cost')}
 except urllib.error.HTTPError as e:
  labels={401:'Anahtar reddedildi veya süresi dolmuş.',403:'Ağ politikası veya hesap erişimi isteği reddetti.',402:'Hesabın bu API erişimi kullanılamıyor.',429:'Kota/hız sınırı: tekrar denemeden duruldu.'}
  raise CloudError(f'HTTP {e.code}: '+labels.get(e.code,'İstek başarısız; otomatik tekrar yapılmadı.')) from None
 except urllib.error.URLError:
  raise CloudError('Proxy / ağ / TLS bağlantısı kurulamadı. Anahtarın geçerliliği henüz sınanamadı.') from None
 except (TimeoutError,OSError):
  raise CloudError('GDELT Cloud bağlantısı zaman aşımına uğradı veya kapandı.') from None

def collect(key,params,max_pages=1,transport=request_json):
 pages=[];records=[];seen=set();cursor=None;complete=False;reason='request_budget';ids=set()
 for _ in range(max_pages):
  query={**params,**({'cursor':cursor} if cursor else {})}
  body,receipt=transport('/events',query,key)
  page={'response':body,'receipt':receipt};pages.append(page)
  if not isinstance(body.get('data'),list):raise CloudError('Events data dizisi eksik; sonuç üretilmedi.')
  applied=body.get('applied_filters')
  if not isinstance(applied,dict) or applied.get('ignored'):raise CloudError('Uygulanan filtreler doğrulanamadı; sonuç üretilmedi.')
  for field in ('search','date_start','date_end'):
   if applied.get(field)!=params[field]:raise CloudError('API tarih/arama filtresini aynı biçimde doğrulamadı; sonuç üretilmedi.')
  pagination=body.get('pagination')
  if not isinstance(pagination,dict) or 'next_cursor' not in pagination:raise CloudError('Sayfalama bitiş bilgisi eksik; tam sonuç varsayılmadı.')
  nxt=pagination['next_cursor']
  if nxt is not None and (not isinstance(nxt,str) or not nxt or nxt in seen or nxt==cursor):raise CloudError('İlerlemeyen veya geçersiz cursor; duruldu.')
  if pagination.get('has_more') is not None and bool(nxt)!=bool(pagination['has_more']):raise CloudError('Çelişkili sayfalama bilgisi; duruldu.')
  for row in body['data']:
   if not isinstance(row,dict):raise CloudError('Event kaydı nesne değil.')
   identity=row.get('id')
   if not isinstance(identity,str) or not identity:raise CloudError('Event kimliği eksik.')
   if identity not in ids:records.append(row);ids.add(identity)
  if nxt is None:complete=True;reason='terminal_cursor';break
  seen.add(nxt);cursor=nxt
 return {'provider':'GDELT Cloud','record_kind':'machine_coded_events','query':params,'data':records,'pages':pages,'pagination_complete':complete,'stop_reason':reason,'next_cursor':None if complete else cursor,'coverage_complete':None,'warning':'Semantic retrieval candidates, not all disinformation operations. Terminal pagination does not establish complete temporal coverage or exhaustive reporting.'}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--prompt-key',action='store_true',help='Kendi terminalinde gizli giriş; dosyaya kaydedilmez.')
 p.add_argument('--schema-only',action='store_true',help='Yalnız ücretsiz şema ve maliyet metaverisi; veri erişimini doğrulamaz.')
 p.add_argument('--start');p.add_argument('--end');p.add_argument('--max-pages',type=int,default=1,choices=range(1,3))
 p.add_argument('--search',default='Russian disinformation operations targeting Western Europe Doppelganger')
 a=p.parse_args();key=os.environ.get('GDELT_API_KEY','')
 if a.prompt_key:key=getpass.getpass('GDELT Cloud API key (gizli, kaydedilmez): ')
 if not key:raise CloudError('GDELT_API_KEY tanımlı değil. Ortamın Secrets alanında tanımla veya kendi terminalinde --prompt-key kullan.')
 today=dt.datetime.now(dt.timezone.utc).date();end=dt.date.fromisoformat(a.end) if a.end else today-dt.timedelta(days=1)
 start=dt.date.fromisoformat(a.start) if a.start else end-dt.timedelta(days=6)
 if not start<=end<today or (end-start).days>30:raise CloudError('1–31 tamamlanmış UTC günü seçilmeli; bugünün açık dönemi dışarıda tutulur.')
 root=pathlib.Path(__file__).resolve().parents[1];out=root/'output';out.mkdir(exist_ok=True)
 if a.schema_only:
  result={'provider':'GDELT Cloud','warning':'Schema reads do not establish data entitlement.'}
  for path in ('/meta/endpoints','/meta/query-units'):
   body,receipt=request_json(path,{},key);result[path]={'response':body,'receipt':receipt}
  name='GDELT_CLOUD_SCHEMA.json'
 else:
  # One free metadata read, then at most two small evidence pages. No retries/polling.
  costs,receipt=request_json('/meta/query-units',{},key)
  result=collect(key,{'search':a.search,'date_start':start.isoformat(),'date_end':end.isoformat(),'limit':10},a.max_pages)
  result['quota_reference']={'response':costs,'receipt':receipt};name='GDELT_CLOUD_EVENTS.json'
 encoded=json.dumps(result,ensure_ascii=False,indent=2).encode();tmp=out/(name+'.tmp');tmp.write_bytes(encoded);tmp.replace(out/name)
 print('Kaydedildi:',name,'SHA-256:',hashlib.sha256(encoded).hexdigest())
 if 'data' in result:print('GDELT Cloud Event kaydı:',len(result['data']),'Sayfalama tamamlandı:',result['pagination_complete'],'Tarihsel kapsam: yanıt meta.coverage alanlarından ayrıca incelenmeli.')

if __name__=='__main__':
 try:main()
 except CloudError as e:print('GDELT CLOUD:',str(e),file=sys.stderr);sys.exit(2)
 except ValueError:print('GDELT CLOUD: Tarih veya yapılandırma değeri geçersiz.',file=sys.stderr);sys.exit(2)
