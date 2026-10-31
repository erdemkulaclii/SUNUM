/* GDELT haber haritası (Bulgu 4 / AS3).
 * Katmanlar: (1) haberin kaynak ülkesi — DOC 2.0 artlist, (2) haberde anılan yer — GKG V2Locations,
 * (3) Meta hedef etiketi — karşılaştırma çerçevesi.
 * Veri kaynakları sırayla: gömülü anlık görüntü → tarayıcı önbelleği → canlı sorgu (yerel vekil ya da doğrudan API) → elle JSON.
 * Hiçbir koşulda örnek/uydurma gözlem üretilmez; başarısız istek "veri yok" olarak gösterilir.
 */
'use strict';
(function(){
const CFG=D.gdelt_config,CACHE_KEY='SUNUM_GDELT_MAP_V1',PROXY=['127.0.0.1','localhost'].includes(location.hostname)&&location.protocol==='http:';
const G={snap:D.gdelt||null,map:null,base:null,meta:null,points:null,busy:false,progress:'',error:'',show:{src:true,loc:true,meta:true}};
const nf=new Intl.NumberFormat('tr-TR'),pct=x=>'%'+(x*100).toLocaleString('tr-TR',{maximumFractionDigits:1,minimumFractionDigits:1});
const normName=s=>String(s||'').normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]/g,'');
// GDELT (FIPS tabanlı) ülke adları → Natural Earth ADMIN
const ALIAS={unitedstates:'United States of America',czechrepublic:'Czechia',bosniaherzegovina:'Bosnia and Herzegovina',macedonia:'North Macedonia',serbia:'Republic of Serbia',tanzania:'United Republic of Tanzania',burma:'Myanmar',swaziland:'eSwatini',congo:'Republic of the Congo',congobrazzaville:'Republic of the Congo',congokinshasa:'Democratic Republic of the Congo',democraticrepublicofthecongo:'Democratic Republic of the Congo',bahamas:'The Bahamas',slovakrepublic:'Slovakia',eastimor:'East Timor',timorleste:'East Timor',cotedivoire:'Ivory Coast',occupiedpalestinianterritory:'Palestine',westbank:'Palestine',gazastrip:'Palestine',korea:'South Korea',southkorea:'South Korea',northkorea:'North Korea',russianfederation:'Russia',unitedkingdom:'United Kingdom',greatbritain:'United Kingdom',england:'United Kingdom',scotland:'United Kingdom',holland:'Netherlands',vatican:'Italy'};
const META_TARGETS={Germany:'Germany','United Kingdom':'UK',France:'France',Italy:'Italy',Latvia:'Latvia',Ukraine:'Ukraine'};
const index=new Map();D.features.forEach((f,i)=>{for(const n of f.names)if(!index.has(n))index.set(n,i)});
const byAdmin=new Map(D.features.map((f,i)=>[normName(f.name),i]));
function featureFor(name){const k=normName(name);if(ALIAS[k]!==undefined)return byAdmin.get(normName(ALIAS[k]));return byAdmin.get(k)??index.get(k)}

/* ---------- veri ---------- */
function aggregate(articles){const seen=new Set(),unique=[];for(const a of articles){const u=String(a.url||'').trim();if(!u||seen.has(u))continue;seen.add(u);unique.push({url:u,title:a.title||'',seendate:a.seendate||'',domain:a.domain||'',language:a.language||'',sourcecountry:a.sourcecountry||''})}
 const count=key=>{const m=new Map();for(const a of unique){const k=a[key]||'Bilinmiyor';m.set(k,(m.get(k)||0)+1)}return [...m].sort((x,y)=>y[1]-x[1]).map(([name,count])=>({name,count}))};
 return{articles:unique,source_countries:count('sourcecountry'),languages:count('language'),unique_articles:unique.length}}
function validSnap(x){return x&&x.schema===CFG.schema&&Array.isArray(x.articles)&&x.window&&x.query}
function normalizeSnap(x){const agg=aggregate(x.articles);return{...x,...agg}}
function parseDoc(text){text=String(text).trim();if(!text.startsWith('{'))throw new Error('GDELT JSON yerine metin döndürdü: '+text.slice(0,140));let b;try{b=JSON.parse(text)}catch(e){b=JSON.parse(text.replace(/[\u0000-\u001f]/g,' '))}const a=b.articles||[];if(!Array.isArray(a))throw new Error('Beklenmeyen DOC şeması');return a.filter(x=>x&&x.url)}
const stamp=d=>d.toISOString().replace(/[-:TZ]/g,'').slice(0,14);
function windowRange(id){const w=CFG.windows[id];if(w.start)return[new Date(w.start+'T00:00:00Z'),new Date(w.end+'T00:00:00Z')];const e=new Date();e.setUTCHours(0,0,0,0);const s=new Date(e);s.setUTCDate(s.getUTCDate()-w.days);return[s,e]}
function slices(id){const[s,e]=windowRange(id),stop=new Date(e);stop.setUTCDate(stop.getUTCDate()+1);const out=[];let cur=new Date(s);while(cur<stop){const n=new Date(cur);n.setUTCDate(n.getUTCDate()+CFG.windows[id].chunk_days);out.push([new Date(cur),n<stop?n:new Date(stop)]);cur=n}return out}
function docURL(a,b){const u=new URL(CFG.endpoint);u.search=new URLSearchParams({query:CFG.query,mode:'artlist',format:'json',maxrecords:String(CFG.max_records),sort:'dateasc',startdatetime:stamp(a),enddatetime:stamp(new Date(b-1000))});return u.href}
async function timed(url,ms=60000){const c=new AbortController(),t=setTimeout(()=>c.abort(),ms);try{return await fetch(url,{signal:c.signal,credentials:'omit',cache:'no-store'})}finally{clearTimeout(t)}}
async function fetchChunk(a,b){
 if(PROXY){try{const r=await timed('/api/gdelt-map-chunk?start='+stamp(a)+'&end='+stamp(b),90000),j=await r.json();if(r.ok&&j.status==='ok')return{articles:j.articles,endpoint:j.endpoint,via:'local_proxy',waited:true};throw new Error(j.message||('HTTP '+r.status))}catch(e){G.proxyError=e.message}}
 const url=docURL(a,b),r=await timed(url);if(!r.ok)throw new Error('HTTP '+r.status);return{articles:parseDoc(await r.text()),endpoint:url,via:'browser_direct',waited:false};
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function runQuery(id){
 if(G.busy)return;G.busy=true;G.error='';const parts=slices(id),log=[],all=[];let via='';
 try{
  for(const[i,[a,b]]of parts.entries()){
   G.progress=`GDELT sorgulanıyor · dilim ${i+1}/${parts.length}`;paint();
   const entry={start:a.toISOString(),end:b.toISOString()};
   try{const r=await fetchChunk(a,b);via=r.via;all.push(...r.articles);Object.assign(entry,{status:'ok',endpoint:r.endpoint,articles_returned:r.articles.length,capped:r.articles.length>=CFG.max_records});if(!r.waited&&i<parts.length-1)await sleep(5600)}
   catch(e){Object.assign(entry,{status:'failed',error:String(e.name==='AbortError'?'zaman aşımı':e.message).slice(0,200)});if(i===0&&log.length===0){log.push(entry);throw new Error(entry.error)}await sleep(5600)}
   log.push(entry);
  }
  if(!log.some(c=>c.status==='ok'))throw new Error('Hiçbir dilim yanıt vermedi');
  const[s,e]=windowRange(id),w=CFG.windows[id];
  G.snap=normalizeSnap({schema:CFG.schema,provider:'GDELT Project DOC 2.0 API (artlist)',query:CFG.query,window:{id,label:w.label,start:s.toISOString().slice(0,10),end:e.toISOString().slice(0,10),note:w.note},retrieved_at:new Date().toISOString(),origin:via,chunks:log,capped_chunks:log.filter(c=>c.capped).length,failed_chunks:log.filter(c=>c.status!=='ok').length,articles:all,locations:G.snap?.window?.id===id?G.snap.locations||null:null,warnings:CFG.warnings});
  try{localStorage.setItem(CACHE_KEY,JSON.stringify(G.snap))}catch(e){/* depolama kapalı olabilir */}
 }catch(e){G.error=(e.name==='AbortError'?'Zaman aşımı':e.message)+'. İnternet, tarayıcı CORS kuralı veya GDELT erişimi engelliyor olabilir. Çözüm: BASLAT.sh ile yerel sunucudan açın ya da fetch_gdelt_map.py ile kaydedilmiş JSON yükleyin.'}
 finally{G.busy=false;G.progress='';paint()}
}
function restoreCache(){if(G.snap)return;try{const x=JSON.parse(localStorage.getItem(CACHE_KEY)||'null');if(validSnap(x)){G.snap=normalizeSnap(x);G.snap.from_cache=true}}catch(e){}}
function download(){if(!G.snap)return;const blob=new Blob([JSON.stringify({...G.snap,exported_at:new Date().toISOString()},null,1)],{type:'application/json'}),u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download='GDELT_HARITA_VERISI.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1500)}
$('gdelt-file').onchange=async e=>{const f=e.target.files[0];e.target.value='';if(!f)return;try{const x=JSON.parse(await f.text());if(!validSnap(x))throw new Error('Şema sunum.gdelt-map/1 değil');G.snap=normalizeSnap({...x,origin:'file_import:'+(x.origin||'bilinmiyor')});G.error=''}catch(err){G.error='JSON yüklenemedi: '+err.message}paint()};

/* ---------- özet ---------- */
function stats(){const s=G.snap;if(!s)return null;const total=s.unique_articles||0,rows=s.source_countries.filter(r=>r.name!=='Bilinmiyor'),counts=new Map(),unmatched=[];
 for(const r of rows){const i=featureFor(r.name);if(i===undefined)unmatched.push(r);else counts.set(i,(counts.get(i)||0)+r.count)}
 const de=byAdmin.get('germany'),deN=counts.get(de)||0;let targetN=0;for(const k of Object.keys(META_TARGETS)){const i=byAdmin.get(normName(k));targetN+=counts.get(i)||0}
 return{total,rows,counts,unmatched,max:Math.max(1,...counts.values()),deN,targetN}}
window.gdeltSummaryLine=()=>{const t=stats();if(!t||!t.total)return 'Kaynak ülke ve anılan yer katmanları (haritada canlı)';const top=t.rows.slice(0,3).map(r=>trName(r.name)+' '+r.count).join(', ');return `${nf.format(t.total)} haber · en çok: ${top} · Almanya kaynaklı ${pct(t.deN/t.total)}`};
function trName(name){const i=featureFor(name);return i===undefined?name:D.features[i].name_tr}
function originLabel(s){const o=String(s.origin||'');const when=new Date(s.retrieved_at).toLocaleString('tr-TR',{dateStyle:'medium',timeStyle:'short'});
 if(s.from_cache)return'TARAYICI ÖNBELLEĞİ · alındı '+when;if(o.startsWith('embedded_snapshot'))return'ANLIK GÖRÜNTÜ · alındı '+when;if(o.startsWith('file_import'))return'YÜKLENEN DOSYA · alındı '+when;return'CANLI GDELT YANITI · '+when+(o==='local_proxy'?' · yerel sunucu':'')}

/* ---------- harita ---------- */
function geo(){return{type:'FeatureCollection',features:D.features.map((f,i)=>({type:'Feature',properties:{i,name:f.name},geometry:{type:'MultiPolygon',coordinates:f.polygons}}))}}
let GEO=null;
function styleFor(t){return feat=>{const n=t&&G.show.src?t.counts.get(feat.properties.i)||0:0;return{color:'#8ea3b6',weight:.5,fillColor:n?'#1f5f99':'#eef2f5',fillOpacity:n?.18+.72*Math.log1p(n)/Math.log1p(t.max):1}}}
function mount(){const slot=$('gdelt-slot');if(!slot)return;unmount();
 slot.innerHTML='<div class="gm-wrap"><div id="gm-map" class="gm-map" role="application" aria-label="GDELT haber haritası"></div><div id="gm-empty" class="gm-empty"></div><aside id="gm-panel" class="gm-panel" aria-live="polite"></aside></div><div class="gm-controls"><button data-q="meta2022">2022 penceresini sorgula</button><button data-q="recent30">Son 30 gün</button><button id="gm-load">JSON yükle</button><button id="gm-save">JSON indir</button><span class="gm-sep"></span><label><input type="checkbox" data-l="src" checked>Kaynak ülke</label><label><input type="checkbox" data-l="loc" checked>Anılan yer</label><label><input type="checkbox" data-l="meta" checked>Meta hedefi</label><span class="gm-sep"></span><button data-v="eu">Avrupa</button><button data-v="world">Dünya</button></div>';
 GEO=GEO||geo();const map=L.map('gm-map',{keyboard:false,zoomSnap:.25,minZoom:1,maxZoom:7,worldCopyJump:false,attributionControl:true});G.map=map;map.setView([50,10],3);map.attributionControl.setPrefix('Leaflet 1.9.4');map.attributionControl.addAttribution('Sınırlar: Natural Earth · Veri: The GDELT Project');
 G.base=L.geoJSON(GEO,{style:styleFor(stats()),onEachFeature:(f,l)=>l.on('mouseover',()=>l.bindTooltip(tip(f.properties.i),{sticky:true}).openTooltip())}).addTo(map);
 map.createPane('meta');map.getPane('meta').style.zIndex=420;map.getPane('meta').style.pointerEvents='none';
 G.meta=L.geoJSON({type:'FeatureCollection',features:GEO.features.filter(f=>META_TARGETS[f.properties.name])},{pane:'meta',interactive:false,style:f=>({color:'#c0392b',weight:f.properties.name==='Germany'?3.2:2,dashArray:f.properties.name==='Germany'?null:'5 4',fill:false})});
 G.points=L.layerGroup();
 slot.querySelectorAll('[data-q]').forEach(b=>b.onclick=()=>runQuery(b.dataset.q));$('gm-load').onclick=()=>$('gdelt-file').click();$('gm-save').onclick=download;
 slot.querySelectorAll('[data-l]').forEach(c=>{c.checked=G.show[c.dataset.l];c.onchange=()=>{G.show[c.dataset.l]=c.checked;paint()}});slot.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>view(b.dataset.v));
 paint();requestAnimationFrame(()=>setTimeout(()=>{if(G.map!==map)return;map.invalidateSize(false);view(G.view||'eu',false)},30))}
function view(v,anim=true){if(!G.map)return;G.view=v;const b=v==='world'?[[-50,-160],[72,165]]:[[35,-12],[62,34]],pw=($('gm-panel')?.offsetWidth||0)+16,o={paddingTopRight:[innerWidth>900?pw:0,0],paddingBottomLeft:[0,10]};anim?G.map.flyToBounds(b,{...o,duration:.9}):G.map.fitBounds(b,o)}
function unmount(){if(G.map){G.map.remove();G.map=null}}
function tip(i){const f=D.features[i],t=stats(),n=t?.counts.get(i)||0,mk=META_TARGETS[f.name];let h='<b>'+esc(f.name_tr)+'</b><br>'+(t?nf.format(n)+' haber'+(t.total?' ('+pct(n/t.total)+')':''):'GDELT verisi yok');if(mk)h+='<br><span style="color:#c0392b">Meta hedef etiketi: '+D.analysis.findings.target_country_counts[mk]+' gösterge</span>';return h}
function paint(){
 const badge=$('gdelt-open');if(badge){badge.dataset.state=G.busy?'loading':G.snap?'ok':G.error?'error':'empty';badge.textContent=G.busy?'GDELT · sorgulanıyor…':G.snap?'GDELT haritası · '+nf.format(G.snap.unique_articles)+' haber':'GDELT haritası'}
 const panel=$('gm-panel');if(!panel||!G.map)return;const t=stats(),s=G.snap;
 G.base.setStyle(styleFor(t));G.show.meta?G.meta.addTo(G.map):G.meta.remove();
 G.points.clearLayers();const loc=s?.locations?.rows||[];if(G.show.loc&&loc.length){const mx=Math.max(...loc.map(r=>r.articles));for(const r of loc.slice(0,300))L.circleMarker([r.lat,r.lon],{radius:3+13*Math.sqrt(r.articles/mx),color:'#5b3a00',weight:1,fillColor:'#f0a43a',fillOpacity:.85}).bindTooltip('<b>'+esc(r.name)+'</b><br>'+r.articles+' haberde anıldı').addTo(G.points);G.points.addTo(G.map)}else G.points.remove();
 const empty=$('gm-empty');empty.hidden=!!(t&&t.total)||G.busy;empty.innerHTML=G.error?'<b>Veri alınamadı.</b><br>'+esc(G.error):s&&!t.total?'<b>Sorgu yanıt verdi; bu pencerede makale dönmedi.</b><br>'+esc(s.window.note||'')+'<br>Sıfır sonuç, sıfır haber anlamına gelmez.':'<b>GDELT verisi henüz yüklenmedi.</b><br>Aşağıdan “2022 penceresini sorgula” ya da kaydedilmiş JSON yükleyin. Kırmızı çerçeveler Meta hedef etiketleridir.';
 if(G.busy){panel.innerHTML='<p class="gm-chip loading">'+esc(G.progress)+'</p><p class="gm-note">GDELT 5 saniyede bir isteğe izin verir; dilimler sırayla alınır.</p>';return}
 if(!s){panel.innerHTML='<p class="gm-chip">VERİ YOK</p><dl><dt>Sorgu</dt><dd><code>'+esc(CFG.query)+'</code></dd><dt>Pencere</dt><dd>'+esc(CFG.windows.meta2022.label)+'</dd></dl>'+legend(null);return}
 const top=t.rows.slice(0,6),mx=Math.max(1,...top.map(r=>r.count));
 panel.innerHTML='<p class="gm-chip ok">'+esc(originLabel(s))+'</p><p class="gm-window">'+esc(s.window.label)+'</p><div class="gm-kpis"><div><b>'+nf.format(t.total)+'</b><span>tekil haber</span></div><div><b>'+t.rows.length+'</b><span>kaynak ülke</span></div><div><b>'+(t.total?pct(t.deN/t.total):'—')+'</b><span>Almanya kaynaklı</span></div></div>'+
 (top.length?'<ol class="gm-bars">'+top.map(r=>'<li><span>'+esc(trName(r.name))+'</span><i style="width:'+(r.count/mx*100).toFixed(1)+'%"></i><b>'+r.count+'</b></li>').join('')+'</ol>':'')+
 '<p class="gm-compare">Meta hedef etiketlerinde Almanya <b>%95,8</b> · haber kaynaklarında <b>'+(t.total?pct(t.deN/t.total):'—')+'</b>. Altı hedef ülkenin kaynak payı: <b>'+(t.total?pct(t.targetN/t.total):'—')+'</b>.</p>'+
 '<p class="gm-note">'+(s.capped_chunks?'⚠ '+s.capped_chunks+' dilim 250 sınırına ulaştı; seçki eksik olabilir. ':'')+(s.failed_chunks?'⚠ '+s.failed_chunks+' dilim yanıt vermedi. ':'')+(loc.length?'Noktalar: GKG, '+loc.length+' yer. ':'Nokta katmanı için GKG/BigQuery verisi yüklenmedi. ')+(t.unmatched.length?'Haritada eşleşmeyen: '+t.unmatched.map(r=>esc(r.name)+' '+r.count).join(', ')+'.':'')+'</p>'+legend(t);
}
function legend(t){return '<div class="gm-legend"><span><i class="sw src"></i>Kaynak ülke'+(t?' (1–'+t.max+')':'')+'</span><span><i class="sw loc"></i>Anılan yer</span><span><i class="sw meta"></i>Meta hedefi</span></div>'}

window.onSlideRendered=s=>{if(s.visual==='gdelt_map')mount();else unmount()};
$('gdelt-open').onclick=()=>{const i=D.slides.findIndex(s=>s.visual==='gdelt_map');if(i>=0)go(i)};
restoreCache();paint();
if(D.slides[scene]?.visual==='gdelt_map')mount();
// Sunum açılınca, veri yoksa 2022 penceresi arka planda bir kez sorgulanır (≈ 1 dk); harita slaytına gelindiğinde hazır olur.
if(!G.snap&&navigator.onLine)setTimeout(()=>{if(!G.snap&&!G.busy)runQuery('meta2022')},2500);
})();
