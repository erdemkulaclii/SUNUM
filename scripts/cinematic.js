/* Geographic context is an illustration layer; IOC evidence remains country-level. */
const CIN=D.narrative;
scenes.splice(0,scenes.length,...CIN.map(s=>[s.kicker,s.title,s.lead,s.number,s.unit,s.fact]));
offsets.splice(0,offsets.length,0);for(const s of CIN)offsets.push(offsets.at(-1)+s.seconds);
$('track').replaceChildren();CIN.forEach((s,i)=>{const b=document.createElement('button');b.title=`${i+1}. ${s.title}`;b.setAttribute('aria-label',b.title);b.onclick=()=>go(i);$('track').append(b)});
document.body.classList.add('cinema');
const cinePalette=color;color=function(n){if(!document.body.classList.contains('cinema'))return cinePalette(n);const t=Math.max(0,Math.min(1,(Math.log(Math.max(2,n))-Math.log(2))/(Math.log(298)-Math.log(2))));return`rgb(${Math.round(106+65*t)},${Math.round(100+11*t)},${Math.round(79+0*t)})`};
const cineActions=document.createElement('div');cineActions.className='cinema-actions';cineActions.innerHTML='<button id="cinema-style" aria-pressed="true">Sinematik görünüm</button><button id="country-tour">Ülke turu ▶</button>';
document.querySelector('.top-actions').append(cineActions);
const cineGroup=svgEl('g',{id:'location-context-pins'});$('viewport').append(cineGroup);
const cinePins={};let cineActive=null,cineFollowEnd=0,cineFollowFrame=null,cineTour=null,cineDriving=false,cineTourIndex=0;
const cineLeader=svgEl('svg',{id:'photo-leader','aria-hidden':'true'});cineLeader.style.display='none';cineLeader.innerHTML='<path id="photo-connector" pathLength="1"/><circle id="photo-anchor-dot" r="3"/>';
document.querySelector('.map-zone').append(cineLeader);
const cineTag=document.createElement('div');cineTag.className='camera-tag';cineTag.id='camera-tag';cineTag.hidden=true;document.querySelector('.map-zone').append(cineTag);
for(const[k,l]of Object.entries(D.locations)){
 const[x,y]=xy(l.coordinates),g=svgEl('g',{id:'geo-pin-'+k,class:'location-pin',transform:`translate(${x},${y})`,tabindex:0,role:'button','aria-label':`${l.city}: coğrafi bağlam görseli; ${meta[k].name} hedefli ${counts[k]} gösterge`});
 g.append(svgEl('circle',{class:'pin-ring',r:12}),svgEl('path',{class:'pin-cross',d:'M-16,0H-7M7,0H16M0,-16V-7M0,7V16'}),svgEl('circle',{class:'pin-core',r:4}));
 const t=svgEl('text',{x:18,y:-10});t.textContent=l.city;const sub=svgEl('text',{x:18,y:6,class:'pin-sub'});sub.textContent=`${counts[k]} · ${meta[k].name}`;g.append(t,sub);
 g.onclick=()=>{if(!dragMoved)selectCountry(k)};g.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectCountry(k)}};
 cineGroup.append(g);cinePins[k]=g;
}
function cineVisible(){const show=layer==='ioc';cineGroup.style.display=show?'':'none';for(const[k,g]of Object.entries(cinePins)){g.classList.toggle('selected',k===cineActive);g.classList.toggle('dim',!!cineActive&&k!==cineActive);g.style.display=show?'':'none'}if(show)for(const k of focus)markerGroups[k].style.display='none'}
function cineStopTour(){if(cineTour)clearInterval(cineTour);cineTour=null;$('country-tour').textContent='Ülke turu ▶';$('country-tour').setAttribute('aria-pressed','false')}
function cineHidePhoto(){cineActive=null;cineLeader.style.display='none';cineTag.hidden=true;document.body.classList.remove('has-photo');if(cineFollowFrame)cancelAnimationFrame(cineFollowFrame);cineFollowFrame=null;cineVisible()}
const cineBaseClear=clearCountry;clearCountry=function(){cineHidePhoto();cineBaseClear();$('country-card').classList.remove('geo-card','geo-opening');for(const prop of ['left','right','top'])$('country-card').style.removeProperty(prop)};
const cineBaseUpdate=updateMap;updateMap=function(){cineBaseUpdate();cineVisible()};
const cineBaseLayer=setLayer;setLayer=function(next){if(next!=='ioc'){cineHidePhoto();$('country-card').classList.remove('geo-card','geo-opening');for(const prop of ['left','right','top'])$('country-card').style.removeProperty(prop)}cineBaseLayer(next);if(next==='ioc')document.querySelector('.map-disclaimer').textContent='İşaret: yer/kent referansı · Hedef verisi: ülke düzeyi. Fotoğraf kamera GPS veya operasyon konumu değildir. Animasyon, canlı trafik değildir.';cineVisible()};
const cineBaseSelect=selectCountry;
selectCountry=function(k){
 if(cineTour&&!cineDriving)cineStopTour();
 if(layer==='gdelt'&&newsState?.articles.length)return cineBaseSelect(k);
 hideStory();cineBaseSelect(k);
 if(layer!=='ioc'||!D.locations[k]){cineHidePhoto();$('country-card').classList.remove('geo-card','geo-opening');$('country-card').style.left='';$('country-card').style.top='';$('country-card').style.right='';return}
 cineActive=k;document.body.classList.add('has-photo');const l=D.locations[k],card=$('country-card');card.replaceChildren();card.classList.add('geo-card');card.classList.remove('geo-opening');
 const close=document.createElement('button');close.className='close';close.textContent='✕';close.setAttribute('aria-label','Konum kartını kapat');close.onclick=()=>{cineStopTour();clearCountry();resetZoom()};
 const photo=document.createElement('div');photo.className='geo-photo'+(k==='France'?' portrait':'');const img=document.createElement('img');img.src=l.src;img.alt=`${l.city}, ${l.place}; gerçek coğrafi bağlam görseli, operasyon kanıtı değil`;img.decoding='async';photo.append(img);
 const stamp=document.createElement('div');stamp.className='geo-stamp';stamp.textContent='COĞRAFİ BAĞLAM / ARŞİV GÖRSELİ';
 const caption=document.createElement('div');caption.className='geo-caption';const city=document.createElement('strong');city.textContent=l.city;const co=document.createElement('small');co.textContent=`${l.coordinates[1].toFixed(4)}° N / ${Math.abs(l.coordinates[0]).toFixed(4)}° ${l.coordinates[0]<0?'W':'E'} · YER REFERANSI`;caption.append(city,co);photo.append(stamp,caption);
 const info=document.createElement('div');info.className='geo-body';const label=document.createElement('span');label.className='eyebrow';label.textContent='KANITIN ÇÖZÜNÜRLÜĞÜ: HEDEF ÜLKE';
 const h=document.createElement('h2');h.textContent=meta[k].name;const number=document.createElement('span');number.className='count';number.textContent=counts[k];h.append(number);
 const meaning=document.createElement('p');meaning.textContent='Benzersiz alan adı göstergesi · kaynak tarihi 27.09.2022';
 const examples=document.createElement('div');for(const r of D.records.filter(r=>r.country===k).slice(0,2)){const c=document.createElement('code');c.textContent=r.domain;examples.append(c)}
 const evidence=document.createElement('button');evidence.id='country-evidence';evidence.className='evidence-btn';evidence.textContent=`${counts[k]} kaynak kaydını incele →`;evidence.onclick=()=>openEvidence(k);
 const precision=document.createElement('p');precision.className='precision';precision.textContent='Fotoğraf, bu kentte operasyon gerçekleştiğini kanıtlamaz. İşaret kamera GPS konumu değil, yer/kent referansıdır.';
 const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Görsel kaynağı ve konum kesinliği';const dp=document.createElement('p');dp.textContent=l.coordinate_basis+' '+l.license;details.append(summary,dp);details.ontoggle=()=>cineFollow(150);
 info.append(label,h,meaning,examples,evidence,precision,details);
 const credit=document.createElement('div');credit.className='geo-credit';const link=document.createElement('a');link.href=l.source;link.target='_blank';link.rel='noopener noreferrer';link.textContent=l.kind+' · '+l.credit+' ↗';credit.append(link);
 card.append(close,photo,info,credit);card.hidden=false;void card.offsetWidth;card.classList.add('geo-opening');
 cineTag.textContent=`GÖRSEL DOSYASI / ${l.city.toLocaleUpperCase('tr')} / ${l.place.toLocaleUpperCase('tr')}`;cineTag.hidden=false;cineLeader.style.display='';cineLeader.classList.remove('drawing');void cineLeader.getBoundingClientRect();cineLeader.classList.add('drawing');
 focusCountry(k);img.onload=()=>cineFollow(250);cineVisible();cineFollow(1900);
};
function cinePosition(){
 if(!cineActive||$('country-card').hidden||story.hidden===false||layer!=='ioc')return;
 const pin=cinePins[cineActive],matrix=pin.getScreenCTM();if(!matrix)return;
 const point=new DOMPoint(0,0).matrixTransform(matrix),zone=document.querySelector('.map-zone').getBoundingClientRect(),card=$('country-card');
 const x=point.x-zone.left,y=point.y-zone.top,w=card.offsetWidth,h=card.offsetHeight,mobile=zone.width<550;
 let left=mobile?(zone.width-w)/2:x+32;if(!mobile&&left+w>zone.width-20)left=x-w-32;left=Math.max(18,Math.min(left,zone.width-w-18));
 let top=mobile?y-h-28:y-h*.77;top=Math.max(mobile?149:104,Math.min(top,zone.height-h-64));
 card.style.left=left+'px';card.style.top=top+'px';card.style.right='auto';
 let edgeX=Math.max(left+10,Math.min(x,left+w-10)),edgeY=Math.max(top+10,Math.min(y,top+h-10));
 if(x>=left&&x<=left+w&&y>=top&&y<=top+h){edgeY=top+h;edgeX=left+w*.5}
 const elbowX=x+(edgeX-x)*.45;
 $('photo-connector').setAttribute('d',`M${x.toFixed(2)},${y.toFixed(2)}L${elbowX.toFixed(2)},${y.toFixed(2)}L${edgeX.toFixed(2)},${edgeY.toFixed(2)}`);
 $('photo-anchor-dot').setAttribute('cx',x);$('photo-anchor-dot').setAttribute('cy',y);
 card.dataset.anchorX=x.toFixed(2);card.dataset.anchorY=y.toFixed(2);
}
function cineFollow(ms=1700){cineFollowEnd=Math.max(cineFollowEnd,performance.now()+ms);if(cineFollowFrame)return;function frame(){cineFollowFrame=null;cinePosition();if(cineActive&&performance.now()<cineFollowEnd)cineFollowFrame=requestAnimationFrame(frame)}cineFollowFrame=requestAnimationFrame(frame)}
applyZoom=function(){const v=$('viewport');v.style.transformOrigin='0 0';v.style.transition=drag?'none':'transform 1.55s cubic-bezier(.19,.75,.19,1)';v.style.transform=`translate(${transform.x}px,${transform.y}px) scale(${transform.k})`;cineFollow()};
focusCountry=function(k){const l=D.locations[k];if(!l)return;const[x,y]=xy(l.coordinates),small=document.querySelector('.map-zone').clientWidth<550;const n=small?1.7:1.75;transform={k:n,x:(small?490:335)-x*n,y:(small?920:470)-y*n};applyZoom()};
window.addEventListener('resize',()=>{if(cineActive)focusCountry(cineActive);cineFollow(1700)});
const CIN_PANELS={
 'gdelt-products':['GDELT / İKİ AYRI ÜRÜN','Aynı ad ailesi.<br>Farklı veri sözleşmesi.',`<div class="product-duo"><div><span>GDELT PROJECT / DOC 2.0</span><h3>Haber araması</h3><p>URL, başlık, dil, indeksleme zamanı ve kaynak ülkesi. Anahtar gerektirmez. ArtList en fazla 250 sonuçluk seçkidir.</p><button data-api-open>DOC bağlantısını aç →</button></div><div><span>GDELT CLOUD / REST V2</span><h3>Event ve Story</h3><p>Ayrı, anahtarlı servis. Kendi olay kodlaması, hikâye kümelemesi ve metrikleri vardır. Anahtar sunucu/istemci ortam sırrından okunur.</p><p>Bu ortamda canlı veri indirmesi henüz doğrulanmadı.</p></div></div>`,'GDELT Cloud Event kodlaması, GDELT Project’in kodlanmış çıktısı olarak etiketlenmez. Canlı veri yokluğu sonuç değildir.'],
 status:['ARAŞTIRMA DURUMU / ŞEFFAFLIK','Tamamlanan ile<br>açık kalan ayrı.',`<div class="status-ledger"><div><b>TAMAMLANDI</b><p>Gerçek IOC dosyası, tür ayrımı, tekilleştirme, ülke sayımları ve kaynakla ilişkilendirilmiş harita.</p></div><div><b>BAĞLAM</b><p>Gerçek yer fotoğrafları, yer işareti referanslarına bağlandı. Fotoğraflar operasyon anını veya operasyonun şehir konumunu doğrulamaz.</p></div><div><b>AÇIK İŞ</b><p>GDELT canlı veri indirmesi, haber kodlama, bağımsız aktör atfı çapraz kontrolü ve uygun payda ile görünürlük analizi.</p></div><div><b>AYRI TASARIM</b><p>Kamuoyunun ikna edilmesi, erişim ve davranış değişikliği. Mevcut veri bu etkileri ölçmez.</p></div></div>`,'Açık işler, eksik veriyi sıfır kabul ederek veya test yanıtlarını gerçek veri gibi sunarak tamamlanmış sayılmaz.']
};
showScene=function(){
 if(cineTour&&!cineDriving)cineStopTour();
 const s=CIN[scene];$('eyebrow').textContent=s.kicker;
 $('scene-content').innerHTML='<div class="reveal"><h1></h1><p class="lead"></p><div class="hero-number"></div><div class="hero-unit"></div><div class="fact"></div></div>';
 $('scene-content').querySelector('h1').textContent=s.title;$('scene-content').querySelector('.lead').textContent=s.lead;
 const number=$('scene-content').querySelector('.hero-number');number.textContent=s.number;number.classList.toggle('long-number',s.number.length>8);
 $('scene-content').querySelector('.hero-unit').textContent=s.unit;$('scene-content').querySelector('.fact').innerHTML=s.fact;
 $('slide-time').textContent=`${fmt(offsets[scene])}–${fmt(offsets[scene+1])} · 15 dakikalık anlatım`;$('page').innerHTML=`<b>${String(scene+1).padStart(2,'0')}</b> / ${CIN.length}`;$('clock').textContent=`${fmt(elapsed)} / 15:00`;
 $('prev').disabled=scene===0;$('next').disabled=scene===CIN.length-1;
 [...$('track').children].forEach((b,i)=>{b.classList.toggle('active',i===scene);b.classList.toggle('done',i<scene);b.setAttribute('aria-current',i===scene?'step':'false')});
 clearCountry();resetZoom();setLayer('ioc');
 const spec=s.panel?CIN_PANELS[s.panel]:s.story!==undefined?STORY[s.story]:null;
 if(spec){story.innerHTML=`<div class="story-folio">${spec[0]}</div><h2>${spec[1]}</h2>${spec[2]}<div class="story-caption">${spec[3]}</div>`;story.hidden=false;document.querySelector('.map-zone').classList.add('has-story');$('map-heading').textContent=spec[0].replace(' / ',' · ');story.querySelectorAll('[data-api-open]').forEach(b=>b.onclick=openAPI);if($('story-ioc'))$('story-ioc').onclick=()=>{hideStory();setLayer('ioc')};if($('story-evidence'))$('story-evidence').onclick=()=>openEvidence()}
 else{hideStory();if(s.country)selectCountry(s.country)}
 cineVisible();
};
$('country-tour').onclick=()=>{if(cineTour){cineStopTour();return}if(playing)togglePlay();cineTourIndex=0;function step(){cineDriving=true;if(cineTourIndex>=4){go(5);cineDriving=false;cineStopTour();return}go(6+cineTourIndex++);cineDriving=false}step();$('country-tour').textContent='Turu durdur Ⅱ';$('country-tour').setAttribute('aria-pressed','true');cineTour=setInterval(step,6000)};
$('play').onclick=()=>{cineStopTour();togglePlay()};
$('cinema-style').onclick=()=>{const on=document.body.classList.toggle('cinema');document.body.classList.toggle('atlas-mode',!on);$('cinema-style').textContent=on?'Sinematik görünüm':'Atlas görünümü';$('cinema-style').setAttribute('aria-pressed',on);updateMap();cineFollow()};
document.querySelector('.map-disclaimer').textContent='Fotoğraf işaretleri yer/kent referansıdır; kamera GPS veya operasyon konumu değildir. Hedef verisi ülke düzeyindedir. Animasyon gerçek zamanlı trafik değildir.';
document.querySelector('.hint').textContent='Ülkeyi seç → konuma yaklaş → fotoğraf ve kanıt dosyasını aç';
document.addEventListener('keydown',e=>{if(e.key==='Escape'){cineStopTour();cineHidePhoto()}});
// Add a visible, complete image credit ledger below the evidence dataset.
const photoLedger=document.createElement('section');photoLedger.className='photo-source-grid';photoLedger.setAttribute('aria-label','Konum görsellerinin kaynak künyeleri');
for(const l of Object.values(D.locations)){const f=document.createElement('figure');const img=document.createElement('img');img.src=l.src;img.alt=l.city+' · coğrafi bağlam';img.loading='lazy';const cap=document.createElement('figcaption');cap.textContent=l.city+' / '+l.place+'. '+l.credit+'. '+l.coordinate_basis+' '+l.license;const a=document.createElement('a');a.href=l.source;a.target='_blank';a.rel='noopener noreferrer';a.textContent=' Kaynak ↗';cap.append(a);f.append(img,cap);photoLedger.append(f)}document.querySelector('.below').append(photoLedger);
showScene();updateMap();
