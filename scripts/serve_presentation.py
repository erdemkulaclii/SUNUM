"""Loopback presentation server. GDELT Cloud key is used only on the server.

Run: python scripts/serve_presentation.py
The server never serves repository files or .env, and never returns the key.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit,unquote,urlencode
from urllib.request import urlopen,Request
import argparse,datetime as dt,json,os,threading,time,webbrowser,mimetypes
from fetch_gdelt_cloud import collect,CloudError
R=Path(__file__).resolve().parents[1];O=R/'output'

def load_key():
 key=os.environ.get('GDELT_API_KEY','')
 if key:return key
 # Private application configuration; never read or printed by HTTP handlers.
 p=R/'.env'
 if p.is_file():
  for line in p.read_text().splitlines():
   if line.startswith('GDELT_API_KEY='):return line.partition('=')[2].strip()
 return ''

class CloudGateway:
 def __init__(self,key,transport=None):self.key=key;self.transport=transport;self.lock=threading.Lock();self.cached=None;self.last=0
 def get(self):
  with self.lock:
   if self.cached and time.time()-self.last<(21600 if self.cached.get('status')=='ok' else 60):
    return {**self.cached,'gateway_cache':True}
   end=dt.datetime.now(dt.timezone.utc).date()-dt.timedelta(days=1);start=end-dt.timedelta(days=6)
   query={'search':'Russian disinformation operations targeting Western Europe Doppelganger','date_start':start.isoformat(),'date_end':end.isoformat(),'limit':10}
   result={'provider':'GDELT Cloud','key_configured':bool(self.key),'checked_at':dt.datetime.now(dt.timezone.utc).isoformat(),'query':query,'gateway_cache':False}
   if not self.key:result.update(status='key_not_configured',message='GDELT Cloud sunucu anahtarı yapılandırılmamış.')
   else:
    try:
     kwargs={'transport':self.transport} if self.transport else {}
     data=collect(self.key,query,max_pages=1,**kwargs)
     result.update(status='ok',result=data,message='GDELT Cloud API yanıtı; en fazla bir sayfalık semantik aday seçkisi.')
     safe=json.dumps(data,ensure_ascii=False,indent=2).replace(self.key,'[REDACTED]');(O/'GDELT_CLOUD_EVENTS.json').write_text(safe)
    except CloudError as e:
     message=str(e).replace(self.key,'[REDACTED]')
     status='credential_rejected' if 'HTTP 401' in message else 'quota_limited' if 'HTTP 429' in message else 'request_failed'
     result.update(status=status,message=message)
   if self.key:result=json.loads(json.dumps(result,ensure_ascii=False).replace(self.key,'[REDACTED]'))
   self.last=time.time();self.cached=result
   summary={k:v for k,v in result.items() if k!='result'}
   (O/'GDELT_CLOUD_RUNTIME_STATUS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
   return result

def public_doc():
 end=dt.datetime.now(dt.timezone.utc).replace(second=0,microsecond=0);start=end-dt.timedelta(days=30)
 q={'query':'(Doppelganger OR "Doppelgänger") (Russia OR Russian OR Russie OR Russland OR Rusya)','mode':'artlist','format':'json','maxrecords':250,'sort':'datedesc','startdatetime':start.strftime('%Y%m%d%H%M%S'),'enddatetime':end.strftime('%Y%m%d%H%M%S')}
 endpoint='https://api.gdeltproject.org/api/v2/doc/doc?'+urlencode(q)
 with urlopen(Request(endpoint,headers={'User-Agent':'SUNUM-Research/2.0'}),timeout=35) as response:raw=response.read(10*1024*1024+1)
 if len(raw)>10*1024*1024:raise ValueError('DOC yanıtı boyut sınırını aşıyor.')
 body=json.loads(raw)
 if not isinstance(body,dict) or not isinstance(body.get('articles'),list):raise ValueError('DOC articles şeması dönmedi.')
 return {'provider':'GDELT Project DOC 2.0','status':'ok','raw':body,'endpoint':endpoint,'query':q,'retrieved_at':dt.datetime.now(dt.timezone.utc).isoformat()}

class Handler(BaseHTTPRequestHandler):
 gateway=None;doc_cache=None;doc_lock=threading.Lock();port=8765
 def log_message(self,*args):pass
 def respond(self,status,body,ctype='application/json; charset=utf-8'):
  encoded=json.dumps(body,ensure_ascii=False).encode() if isinstance(body,dict) else body
  self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(encoded)));self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cache-Control','no-store' if ctype.startswith('application/json') else 'no-cache');self.send_header('Referrer-Policy','strict-origin-when-cross-origin');self.end_headers();self.wfile.write(encoded)
 def do_GET(self):
  allowed={f'127.0.0.1:{self.port}',f'localhost:{self.port}'}
  if self.headers.get('Host') not in allowed:return self.respond(403,{'status':'forbidden'})
  origin=self.headers.get('Origin');site=self.headers.get('Sec-Fetch-Site')
  if (origin and origin not in {f'http://{h}' for h in allowed}) or site=='cross-site':return self.respond(403,{'status':'forbidden'})
  path=unquote(urlsplit(self.path).path)
  if path=='/health':return self.respond(200,{'status':'ok','cloud_key_configured':bool(self.gateway.key),'cloud_endpoint':'https://gdeltcloud.com/api/v2','key_exposed':False})
  if path=='/api/gdelt-cloud':return self.respond(200,self.gateway.get())
  if path=='/api/gdelt-doc':
   with self.doc_lock:
    if not Handler.doc_cache or time.time()-Handler.doc_cache[0]>21600:
     try:Handler.doc_cache=(time.time(),public_doc())
     except Exception:Handler.doc_cache=(time.time(),{'provider':'GDELT Project DOC 2.0','status':'request_failed','message':'DOC API için ağ/proxy/servis bağlantısı kurulamadı.'})
    return self.respond(200,Handler.doc_cache[1])
  if path in ['/','/index.html']:target=O/'PROFESYONEL_SUNUM.html'
  else:
   name=path.removeprefix('/output/').lstrip('/')
   if '/' in name or name.startswith('.') or Path(name).suffix not in {'.html','.pdf','.pptx','.docx','.mp4','.gif','.png','.jpg','.json','.md','.txt'}:return self.respond(404,{'status':'not_found'})
   target=O/name
  if not target.is_file():return self.respond(404,{'status':'not_found'})
  return self.respond(200,target.read_bytes(),mimetypes.guess_type(target.name)[0] or 'application/octet-stream')

def main():
 p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);p.add_argument('--no-open',action='store_true');p.add_argument('--probe',action='store_true');a=p.parse_args();key=load_key();gateway=CloudGateway(key)
 if a.probe:
  result=gateway.get();print(json.dumps({k:v for k,v in result.items() if k!='result'},ensure_ascii=False));return
 Handler.gateway=gateway;Handler.port=a.port
 server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
 print('Sunum sunucusu hazır. GDELT Cloud anahtarı yapılandırıldı:',bool(key),flush=True)
 if not a.no_open:threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{a.port}/')).start()
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
