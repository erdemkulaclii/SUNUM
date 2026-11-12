/* 3B sahneler (three.js r149, gömülü; ağ isteği yok).
 *  - Küre: GDELT haber sütunları (gün gün birikim → aktif kuruluş başına oran → anılan yerler ve Meta hedefleri)
 *  - Takımyıldız: 311 alan adı; marka klonları, yazım varyantları, uydurma yayın aileleri
 *  - Kapak: yavaş dönen küre
 * Bütün değerler derleme sırasında ham veriden üretilen D.globe ve D.typology nesnelerinden gelir.
 * Aşamaları sunucu ilerletir (→ / Boşluk); hiçbir aşama süreyle kendiliğinden geçmez.
 * WebGL yoksa slayt 2B görsele (Leaflet haritası / çubuk grafik) düşer.
 */
'use strict';
(function(){
const T3=window.THREE,nf=new Intl.NumberFormat('tr-TR'),tr=(x,n=1)=>Number(x).toLocaleString('tr-TR',{minimumFractionDigits:n,maximumFractionDigits:n});
let GL=null;
function webglOK(){if(GL!==null)return GL;try{const c=document.createElement('canvas');GL=!!(T3&&window.WebGLRenderingContext&&(c.getContext('webgl2')||c.getContext('webgl')))}catch(e){GL=false}return GL}
window.use3D=()=>webglOK()&&!window.GDELT_FORCE_2D&&!!D.globe;
window.has3D=()=>webglOK();
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;
const ll2v=(lat,lon,r=1)=>{const ph=(90-lat)*Math.PI/180,th=(lon+180)*Math.PI/180;return new T3.Vector3(-r*Math.sin(ph)*Math.cos(th),r*Math.cos(ph),r*Math.sin(ph)*Math.sin(th))};
const hex=c=>new T3.Color(c);
const mix=(a,b,t)=>'#'+hex(a).lerp(hex(b),t).getHexString();

function makeStage(el,{fov=38,dist=3.2,alpha=false}={}){
 const renderer=new T3.WebGLRenderer({antialias:true,alpha});renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.outputEncoding=T3.sRGBEncoding;if(!alpha)renderer.setClearColor(0x0a1626,1);
 const scene=new T3.Scene(),camera=new T3.PerspectiveCamera(fov,1,.05,200);camera.position.set(0,0,dist);
 renderer.domElement.className='s3-canvas';el.prepend(renderer.domElement);
 const resize=()=>{const w=el.clientWidth,h=el.clientHeight;if(!w||!h)return;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()};
 const ro=new ResizeObserver(resize);ro.observe(el);resize();
 let raf=0,alive=true,last=performance.now();const tick=[];
 const loop=t=>{if(!alive)return;const dt=Math.min(.05,(t-last)/1000);last=t;for(const f of tick)f(dt,t/1000);renderer.render(scene,camera);raf=requestAnimationFrame(loop)};raf=requestAnimationFrame(loop);
 return{renderer,scene,camera,tick,el,dispose(){alive=false;cancelAnimationFrame(raf);ro.disconnect();scene.traverse(o=>{o.geometry&&o.geometry.dispose&&o.geometry.dispose();if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{m.map&&m.map.dispose();m.dispose()})});renderer.dispose();try{renderer.forceContextLoss()}catch(e){}renderer.domElement.remove()}};
}
function textSprite(text,{size=46,color='#ffffff',bg='rgba(10,22,38,.82)',edge=null}={}){
 const c=document.createElement('canvas'),x=c.getContext('2d'),font='700 '+size+'px Arial,Helvetica,sans-serif';x.font=font;
 const w=Math.ceil(x.measureText(text).width)+30,h=size+24;c.width=w;c.height=h;x.font=font;x.fillStyle=bg;x.fillRect(0,0,w,h);if(edge){x.fillStyle=edge;x.fillRect(0,0,7,h)}x.fillStyle=color;x.textBaseline='middle';x.fillText(text,edge?20:15,h/2+2);
 const tex=new T3.CanvasTexture(c);tex.minFilter=T3.LinearFilter;tex.encoding=T3.sRGBEncoding;
 const sp=new T3.Sprite(new T3.SpriteMaterial({map:tex,depthTest:false,transparent:true}));sp.userData={aspect:w/h,text};sp.renderOrder=20;return sp;
}
function stars(scene,n=900,r=60){const p=new Float32Array(n*3);let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;for(let i=0;i<n;i++){const u=rnd()*2-1,a=rnd()*Math.PI*2,s=Math.sqrt(1-u*u);p[i*3]=r*s*Math.cos(a);p[i*3+1]=r*u;p[i*3+2]=r*s*Math.sin(a)}const g=new T3.BufferGeometry();g.setAttribute('position',new T3.BufferAttribute(p,3));scene.add(new T3.Points(g,new T3.PointsMaterial({color:0x9fb6cf,size:.22,sizeAttenuation:true,transparent:true,opacity:.75})))}
function hud(el){const h=document.createElement('div');h.className='s3-hud';h.innerHTML='<p class="s3-kicker"></p><p class="s3-big"></p><p class="s3-sub"></p>';el.append(h);return{set(k,b,s){h.children[0].textContent=k;h.children[1].innerHTML=b;h.children[2].innerHTML=s}}}
function stageBar(slot,labels,onPick){const bar=document.createElement('div');bar.className='stage-bar';bar.innerHTML=labels.map((l,i)=>'<button data-i="'+i+'"><b>'+(i+1)+'</b>'+esc(l)+'</button>').join('')+'<span class="stage-hint">→ sonraki aşama · ← önceki</span>';slot.append(bar);bar.querySelectorAll('button').forEach(b=>b.onclick=e=>{e.stopPropagation();onPick(+b.dataset.i)});return i=>bar.querySelectorAll('button').forEach((b,k)=>{b.classList.toggle('on',k===i);b.classList.toggle('done',k<i)})}

/* ------------------------------ KÜRE ------------------------------ */
function Globe(el,{ambient=false}={}){
 const G=D.globe,st=makeStage(el,{dist:ambient?2.75:3.25,alpha:ambient,fov:ambient?36:38});
 const world=new T3.Group();st.scene.add(world);if(!ambient){stars(st.scene);world.position.set(.34,-.16,0)}
 st.scene.add(new T3.AmbientLight(0xffffff,.82));const sun=new T3.DirectionalLight(0xffffff,.55);sun.position.set(4,3,6);st.scene.add(sun);
 // Doku: ülkeler 2B tuvale çizilir ve küreye sarılır (eşdikdörtgen izdüşüm).
 const W=4096,H=2048,cv=document.createElement('canvas');cv.width=W;cv.height=H;const cx=cv.getContext('2d'),tex=new T3.CanvasTexture(cv);tex.encoding=T3.sRGBEncoding;tex.anisotropy=Math.min(8,st.renderer.capabilities.getMaxAnisotropy());
 const byAdmin=new Map(D.features.map(f=>[f.name,f])),targetSet=new Map(G.targets.map(t=>[t.admin,t]));
 function trace(f){cx.beginPath();for(const poly of f.polygons)for(const ring of poly){let px=null;ring.forEach(([lon,lat],i)=>{const x=(lon+180)/360*W,y=(90-lat)/180*H;if(i===0||(px!==null&&Math.abs(x-px)>W/2))cx.moveTo(x,y);else cx.lineTo(x,y);px=x});cx.closePath()}}
 function paint(values,max,metaFill){
  cx.fillStyle='#0d2238';cx.fillRect(0,0,W,H);cx.lineJoin='round';
  for(const f of D.features){const v=values.get(f.name)||0,t=targetSet.get(f.name);trace(f);
   cx.fillStyle=metaFill&&t?(f.name==='Germany'?'#d8453a':'#8f4a48'):v?mix('#2f587f','#9fd0f5',Math.sqrt(v/max)):'#26405a';cx.fill();cx.strokeStyle='#5b7a96';cx.lineWidth=1.4;cx.stroke()}
  for(const f of D.features){const t=targetSet.get(f.name);if(!t)continue;trace(f);cx.strokeStyle=f.name==='Germany'?'#ff6a5c':'#e0796f';cx.lineWidth=f.name==='Germany'?7:4;cx.stroke()}
  tex.needsUpdate=true;
 }
 world.add(new T3.Mesh(new T3.SphereGeometry(1,96,64),new T3.MeshLambertMaterial({map:tex})));
 world.add(new T3.Mesh(new T3.SphereGeometry(1.045,48,32),new T3.MeshBasicMaterial({color:0x58a6e8,transparent:true,opacity:.10,side:T3.BackSide})));
 // Bakış: küre döndürülür, kamera sabit kalır.
 const rot={y:0,x:0,z:st.camera.position.z},fly={on:false};
 const aim=(lat,lon)=>({y:-(lon+90)*Math.PI/180,x:lat*Math.PI/180});
 function look(lat,lon,dist,secs=1.6){const a=aim(lat,lon);let dy=a.y-rot.y;dy=((dy+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;Object.assign(fly,{on:true,t:0,secs,y0:rot.y,x0:rot.x,z0:rot.z,dy,dx:a.x-rot.x,dz:(dist||rot.z)-rot.z});if(!secs){rot.y+=dy;rot.x=a.x;rot.z=dist||rot.z;fly.on=false}}
 let drag=null,spin=ambient?0:0;
 if(!ambient){const c=st.renderer.domElement;c.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY};fly.on=false;c.setPointerCapture(e.pointerId)});c.addEventListener('pointermove',e=>{if(!drag)return;rot.y+=(e.clientX-drag.x)*.006;rot.x=Math.max(-1.2,Math.min(1.2,rot.x+(e.clientY-drag.y)*.006));drag={x:e.clientX,y:e.clientY}});const up=()=>{drag=null};c.addEventListener('pointerup',up);c.addEventListener('pointercancel',up);c.addEventListener('click',e=>e.stopPropagation())}
 // Sütunlar
 const SHORT={'United States of America':'ABD'};const colGeo=new T3.CylinderGeometry(.017,.017,1,16);colGeo.translate(0,.5,0);const up=new T3.Vector3(0,1,0),cols=[];
 if(!ambient)for(const c of G.countries){const n=ll2v(c.lat,c.lon,1),de_=c.admin==='Germany',m=new T3.Mesh(colGeo,new T3.MeshLambertMaterial({color:de_?0xff6a5c:0xf0a43a,emissive:de_?0x5a1410:0x4a2c00}));c.short=SHORT[c.admin]||c.name;m.position.copy(n.clone().multiplyScalar(1.001));m.quaternion.setFromUnitVectors(up,n);m.scale.set(1,.0001,1);m.visible=false;world.add(m);cols.push({c,m,n,h:0,target:0,label:null,key:''})}
 // Anılan yerler
 const places=[];if(!ambient){const mx=Math.max(1,...G.places.map(p=>p.articles));for(const p of G.places){const m=new T3.Mesh(new T3.SphereGeometry(.008+.022*Math.sqrt(p.articles/mx),12,10),new T3.MeshBasicMaterial({color:0xffd27a}));m.position.copy(ll2v(p.lat,p.lon,1.006));m.scale.setScalar(.0001);m.visible=false;world.add(m);places.push(m)}}
 let placeK=0,placeTarget=0;
 function setLabel(col,text,edge){if(col.key===text)return;col.key=text;if(col.label){world.remove(col.label);col.label.material.map.dispose();col.label.material.dispose();col.label=null}if(!text)return;const sp=textSprite(text,{edge});const k=.062;sp.scale.set(k*sp.userData.aspect,k,1);world.add(sp);col.label=sp}
 const HMAX=.6;let stage=-1,dayTimer=null,mode='count';
 const H_=hud(el),dayEl=document.createElement('div');dayEl.className='s3-day';dayEl.hidden=true;el.append(dayEl);
 function showCount(cut){ // cut: gün sınırı (dahil) ya da null = tamamı
  const vals=new Map(),max=Math.max(...G.countries.map(c=>c.articles));let total=0;
  for(const col of cols){let v=0;if(cut===null)v=col.c.articles;else for(const d in col.c.daily)if(d<=cut)v+=col.c.daily[d];total+=v;vals.set(col.c.admin,v);col.target=v/max*HMAX;col.val=v}
  const top=[...cols].sort((a,b)=>b.val-a.val).slice(0,4);for(const col of cols)setLabel(col,top.includes(col)&&col.val?col.c.short+' '+nf.format(col.val):'',col.c.admin==='Germany'?'#ff6a5c':'#f0a43a');
  paint(vals,max,false);return total;
 }
 function showRate(){const shown=cols.filter(c=>c.c.rate_shown),max=Math.max(...shown.map(c=>c.c.per1000)),vals=new Map();
  const top=[...shown].sort((a,b)=>b.c.per1000-a.c.per1000).slice(0,4);for(const col of cols){const ok=col.c.rate_shown;col.target=ok?col.c.per1000/max*HMAX:0;col.val=ok?col.c.per1000:0;if(ok)vals.set(col.c.admin,col.c.per1000);setLabel(col,top.includes(col)?col.c.short+' ‰'+tr(col.c.per1000):'',col.c.admin==='Germany'?'#ff6a5c':'#f0a43a')}
  paint(vals,max,false)}
 function showPlaces(){for(const col of cols){col.target=0;setLabel(col,'')}paint(new Map(),1,true)}
 const us=G.countries.find(c=>c.admin==='United States of America'),de=G.countries.find(c=>c.admin==='Germany');
 function setStage(i,instant){
  if(ambient)return;clearInterval(dayTimer);dayEl.hidden=true;stage=i;placeTarget=0;
  if(i===0){mode='count';look(40,-52,3.3,instant?0:1.4);
   const days=G.days,play=k=>{const d=days[k];const total=showCount(d);dayEl.hidden=false;dayEl.innerHTML='<b>'+d.slice(6)+'.'+d.slice(4,6)+'.'+d.slice(0,4)+'</b><span>birikimli '+nf.format(total)+' haber</span>'};
   H_.set('AŞAMA 1 · HABER SAYISI','ABD <b>'+nf.format(us.articles)+'</b> · Almanya <b>'+nf.format(de.articles)+'</b>',nf.format(G.total)+' tekil haber · ABD’deki '+nf.format(us.articles)+' haber yalnızca '+G.titles_us+' farklı başlık (ajans tekrarı)');
   if(instant){showCount(null)}else{let k=0;play(0);dayTimer=setInterval(()=>{k++;if(k>=days.length){clearInterval(dayTimer);showCount(null);dayEl.hidden=true;return}play(k)},300)}}
  if(i===1){mode='rate';showRate();look(46,-34,3.3,instant?0:1.8);
   H_.set('AŞAMA 2 · AKTİF KURULUŞ BAŞINA (BİNDE)','Almanya <b>‰'+tr(de.per1000)+'</b> · ABD <b>‰'+tr(us.per1000)+'</b>','İfşayı haberleştiren kuruluş / dönemde aktif kuruluş: Almanya '+de.outlets+'/'+nf.format(de.active)+', ABD '+us.outlets+'/'+nf.format(us.active)+' · en az '+G.min_articles+' haberi ve '+G.min_active+' aktif kuruluşu olan ülkeler')}
  if(i===2){mode='places';showPlaces();placeTarget=1;look(47,14,2.2,instant?0:2);const t=G.targets.find(t=>t.admin==='Germany');
   H_.set('AŞAMA 3 · ANILAN YERLER VE META HEDEFLERİ','Haberlerin <b>%'+tr(G.mention_de_pct)+'</b>’sı Almanya’yı anıyor','Kırmızı: Meta hedef etiketi (Almanya '+t.domains+'/'+G.unique_domains+' alan adı) · Sarı noktalar: haberlerde anılan yerler (GKG)')}
  ctl&&ctl.mark(i);
 }
 let ctl=null;
 st.tick.push((dt,t)=>{
  if(fly.on){fly.t+=dt;const k=ease(Math.min(1,fly.t/fly.secs));rot.y=fly.y0+fly.dy*k;rot.x=fly.x0+fly.dx*k;rot.z=fly.z0+fly.dz*k;if(fly.t>=fly.secs)fly.on=false}
  if(ambient)rot.y=aim(26,6).y+Math.sin(t*.12)*.42;
  world.rotation.set(rot.x,rot.y,0);st.camera.position.z=rot.z;
  const v=new T3.Vector3();
  for(const col of cols){col.h+=(col.target-col.h)*Math.min(1,dt*5);const vis=col.h>.002;col.m.visible=vis;if(vis)col.m.scale.set(1,col.h,1);
   if(col.label){col.label.position.copy(col.n.clone().multiplyScalar(1.03+col.h));col.label.getWorldPosition(v);col.label.visible=v.z>.25&&col.h>.002}}
  placeK+=(placeTarget-placeK)*Math.min(1,dt*4);for(const p of places){p.visible=placeK>.01;if(p.visible)p.scale.setScalar(placeK*(1+.12*Math.sin(t*3+p.position.x*20)))}
 });
 if(ambient){const vals=new Map();paint(vals,1,true);look(26,6,2.6,0)}
 return{setStage,dispose(){clearInterval(dayTimer);st.dispose()},bind(c){ctl=c},stage:()=>stage,_cols:cols};
}

/* --------------------------- TAKIMYILDIZ --------------------------- */
function Galaxy(el){
 const TY=D.typology,st=makeStage(el,{dist:11,fov:40});stars(st.scene);st.scene.add(new T3.AmbientLight(0xffffff,.62));const sun=new T3.DirectionalLight(0xffffff,.45);sun.position.set(3,4,8);st.scene.add(sun);
 const COL={marka_birebir:'#ff5a4d',marka_varyant:'#ffb347',family:'#5cc8ff',other:'#8fa3bb'};
 // Küçük kümeler eğik bir halka, büyükler küre üzerinde dağıtılır.
 const around=(k,n,r,seed=0)=>{if(n>9)return fib(k,n,r);const a=2*Math.PI*k/Math.max(1,n)+seed*1.7,tilt=.6+seed*.9;return new T3.Vector3(r*Math.cos(a),r*Math.sin(a)*Math.sin(tilt),r*Math.sin(a)*Math.cos(tilt))};
 const fib=(i,n,r)=>{const y=n===1?0:1-2*i/(n-1),s=Math.sqrt(Math.max(0,1-y*y)),a=i*2.399963;return new T3.Vector3(r*s*Math.cos(a),r*y,r*s*Math.sin(a))};
 const groups=new Map();TY.rows.forEach((r,i)=>{const k=r[0];if(!groups.has(k))groups.set(k,{label:k,cls:r[2],brand:r[3],fam:r[4],rows:[]});groups.get(k).rows.push(i)});
 const brandG=new T3.Group(),inventG=new T3.Group();brandG.position.set(-3.6,0,0);inventG.position.set(2.5,0,0);st.scene.add(brandG,inventG);
 const nodes=[],links=[],labels=[]; // node: {parent,pos,cls,row}
 // Marka klonları: gerçek marka adı merkezde (beyaz), klon adresler çevresinde
 const brands=[...groups.values()].filter(g=>g.cls==='marka_birebir').sort((a,b)=>b.rows.length-a.rows.length),hubs=new Map();
 brands.forEach((g,i)=>{const c=fib(i,brands.length,1.75);hubs.set(g.label,c);const hub=new T3.Mesh(new T3.OctahedronGeometry(.085),new T3.MeshBasicMaterial({color:0xffffff}));hub.position.copy(c);brandG.add(hub);
  g.rows.forEach((ri,k)=>{const p=c.clone().add(around(k,g.rows.length,.36+.014*g.rows.length,i));nodes.push({parent:brandG,pos:p,cls:'marka_birebir',row:ri});links.push({parent:brandG,a:c,b:p,cls:'marka_birebir',set:'brand'})});
  labels.push({parent:brandG,pos:c.clone().add(new T3.Vector3(0,.5+.012*g.rows.length,0)),text:g.label+' ×'+g.rows.length,set:'brand',edge:COL.marka_birebir,min:0})});
 [...groups.values()].filter(g=>g.cls==='marka_varyant').forEach((g,i)=>{const h=hubs.get(g.brand)||new T3.Vector3(0,-2.3+i*.5,0),dir=h.clone().normalize();if(!hubs.has(g.brand))dir.set(0,-1,0);const c=h.clone().add(dir.multiplyScalar(.95)).add(around(i,7,.3,1));
  if(hubs.has(g.brand))links.push({parent:brandG,a:h,b:c,cls:'marka_varyant',set:'brand'});
  g.rows.forEach((ri,k)=>{const p=c.clone().add(around(k,g.rows.length,.15,i));nodes.push({parent:brandG,pos:p,cls:'marka_varyant',row:ri});links.push({parent:brandG,a:c,b:p,cls:'marka_varyant',set:'brand'})})});
 // Uydurma yayın adları: harf karışımı aileleri sıkı kümeler, diğerleri dış kabukta
 const famOf=new Map();TY.families.forEach((f,i)=>f.forEach(l=>famOf.set(l,i)));
 const fams=TY.families.map((f,i)=>({i,labels:f,size:f.reduce((n,l)=>n+(groups.get(l)?groups.get(l).rows.length:0),0)})).sort((a,b)=>b.size-a.size);
 fams.forEach((f,i)=>{const c=fib(i,fams.length,2.15),ring=[];
  f.labels.forEach((l,k)=>{const g=groups.get(l);if(!g)return;const lc=c.clone().add(around(k,f.labels.length,.4,i));ring.push(lc);g.rows.forEach((ri,m)=>{const p=lc.clone().add(around(m,g.rows.length,.15,k+i));nodes.push({parent:inventG,pos:p,cls:'family',row:ri});links.push({parent:inventG,a:lc,b:p,cls:'family',set:'family'})})});
  ring.forEach((p,k)=>{if(ring.length>1)links.push({parent:inventG,a:p,b:ring[(k+1)%ring.length],cls:'family',set:'family',strong:true})});
  labels.push({parent:inventG,pos:c.clone().multiplyScalar(1.22),text:f.labels[0]+' ×'+f.size,set:'family',edge:COL.family,min:i<9?0:99})});
 const others=[...groups.values()].filter(g=>g.cls==='sahte_yayin'&&!famOf.has(g.label));
 others.forEach((g,i)=>{const c=fib(i,others.length,3.25);g.rows.forEach((ri,m)=>{const p=c.clone().add(around(m,g.rows.length,.14,i));nodes.push({parent:inventG,pos:p,cls:'other',row:ri});if(g.rows.length>1)links.push({parent:inventG,a:c,b:p,cls:'other',set:'other'})})});
 // Çizim: her küme için tek InstancedMesh + tek LineSegments
 const geo=new T3.SphereGeometry(.06,14,12),meshes=new Map(),lines=new Map(),dummy=new T3.Object3D();
 for(const parent of [brandG,inventG]){const ns=nodes.filter(n=>n.parent===parent),m=new T3.InstancedMesh(geo,new T3.MeshLambertMaterial({color:0xffffff}),ns.length);ns.forEach((n,i)=>{dummy.position.copy(n.pos);dummy.updateMatrix();m.setMatrixAt(i,dummy.matrix);m.setColorAt(i,hex(COL[n.cls]));n.mesh=m;n.i=i});m.instanceMatrix.needsUpdate=true;parent.add(m);meshes.set(parent,m);
  const ls=links.filter(l=>l.parent===parent),pos=new Float32Array(ls.length*6),col=new Float32Array(ls.length*6);ls.forEach((l,i)=>{pos.set([l.a.x,l.a.y,l.a.z,l.b.x,l.b.y,l.b.z],i*6);l.i=i});const g=new T3.BufferGeometry();g.setAttribute('position',new T3.BufferAttribute(pos,3));g.setAttribute('color',new T3.BufferAttribute(col,3));const seg=new T3.LineSegments(g,new T3.LineBasicMaterial({vertexColors:true,transparent:true,opacity:.75}));parent.add(seg);lines.set(parent,seg)}
 labels.forEach(l=>{const sp=textSprite(l.text,{edge:l.edge,size:40});const k=.3;sp.scale.set(k*sp.userData.aspect,k,1);sp.position.copy(l.pos);sp.visible=false;l.parent.add(sp);l.sp=sp});
 const top6=new Set(TY.top6),cnt=TY.counts,H_=hud(el),leg=document.createElement('div');leg.className='s3-legend';
 leg.innerHTML='<span><i style="background:'+COL.marka_birebir+'"></i>Marka birebir '+cnt.marka_birebir+'</span><span><i style="background:'+COL.marka_varyant+'"></i>Yazım varyantı '+cnt.marka_varyant+'</span><span><i style="background:'+COL.family+'"></i>Uydurma · harf karışımı ailesi '+TY.family_domains+'</span><span><i style="background:'+COL.other+'"></i>Uydurma · diğer '+(cnt.sahte_yayin-TY.family_domains)+'</span>';el.append(leg);
 const cam={x:0,y:0,z:11,tx:0,ty:0,tz:11};let stage=-1,ctl=null;
 function light(pred,linkPred,labelSet){
  for(const n of nodes){const on=pred(n),c=hex(COL[n.cls]);if(!on)c.multiplyScalar(.13);n.mesh.setColorAt(n.i,c)}for(const m of meshes.values())m.instanceColor.needsUpdate=true;
  for(const l of links){const c=hex(COL[l.cls]).multiplyScalar(linkPred(l)?(l.strong?.95:.5):.05),a=lines.get(l.parent).geometry.attributes.color;a.setXYZ(l.i*2,c.r,c.g,c.b);a.setXYZ(l.i*2+1,c.r,c.g,c.b);a.needsUpdate=true}
  for(const l of labels)l.sp.visible=labelSet===l.set&&l.min===0;
 }
 const n=TY.rows.length,pc=x=>'%'+tr(x/n*100);
 function setStage(i){stage=i;
  if(i===0){light(()=>true,()=>true,null);Object.assign(cam,{tx:-.5,ty:.7,tz:12.6});H_.set('AŞAMA 1 · '+n+' ALAN ADI, ÜÇ SINIF','Uydurma yayın adı <b>'+cnt.sahte_yayin+'</b> ('+pc(cnt.sahte_yayin)+')','Marka birebir '+cnt.marka_birebir+' ('+pc(cnt.marka_birebir)+') · yazım varyantı '+cnt.marka_varyant+' ('+pc(cnt.marka_varyant)+') · her nokta bir alan adı')}
  if(i===1){light(x=>x.cls==='marka_birebir'||x.cls==='marka_varyant',l=>l.set==='brand','brand');Object.assign(cam,{tx:-4.3,ty:.75,tz:8.4});H_.set('AŞAMA 2 · MARKA TAKLİTLERİ','<b>'+cnt.marka_birebir+'</b> birebir + <b>'+cnt.marka_varyant+'</b> yazım varyantı','Beyaz çekirdek: gerçek marka adı · kırmızı: aynı adı taşıyan klon adresler ('+TY.brand_tlds+' farklı uzantı) · turuncu: bir iki harfi değişmiş varyantlar')}
  if(i===2){light(x=>x.cls==='family',l=>l.set==='family','family');Object.assign(cam,{tx:1.6,ty:.85,tz:10});H_.set('AŞAMA 3 · HARF KARIŞIMI AİLELERİ','<b>'+TY.family_domains+'</b> adres, <b>'+TY.family_count+'</b> aile','Aynı Almanca ifadenin harfleri yer değiştirilerek yazılmış adlar; her küme bir aile, her halka aynı ifadenin farklı yazımları')}
  if(i===3){const lit=x=>top6.has(TY.rows[x.row][1]);light(lit,()=>false,null);Object.assign(cam,{tx:-.5,ty:.7,tz:12.6});const t=TY.top6_by_class,all=t.sahte_yayin+t.marka_birebir+t.marka_varyant;H_.set('AŞAMA 4 · EN SIK ALTI UZANTI','<b>'+all+'</b> adresin <b>'+t.sahte_yayin+'</b>’i uydurma yayın adı','.online · .website · .site · .space · .pw · .fun — bu uzantılarda yalnızca '+t.marka_birebir+' birebir marka taklidi var')}
  ctl&&ctl.mark(i);
 }
 let drag=null,spinB=0,spinI=0;const c=st.renderer.domElement;c.addEventListener('pointerdown',e=>{drag={x:e.clientX};c.setPointerCapture(e.pointerId)});c.addEventListener('pointermove',e=>{if(!drag)return;const d=(e.clientX-drag.x)*.008;spinB+=d;spinI+=d;drag={x:e.clientX}});const up=()=>{drag=null};c.addEventListener('pointerup',up);c.addEventListener('pointercancel',up);c.addEventListener('click',e=>e.stopPropagation());
 st.tick.push(dt=>{if(!drag){spinB+=dt*.10;spinI+=dt*.07}brandG.rotation.y=spinB;inventG.rotation.y=spinI;const k=Math.min(1,dt*2.2);cam.x+=(cam.tx-cam.x)*k;cam.y+=(cam.ty-cam.y)*k;cam.z+=(cam.tz-cam.z)*k;st.camera.position.set(cam.x,cam.y+.6,cam.z);st.camera.lookAt(cam.x,cam.y,0)});
 return{setStage,dispose(){st.dispose()},bind(x){ctl=x},stage:()=>stage,_nodes:nodes};
}

/* ------------------------- Slayt bağlantısı ------------------------- */
let active=null,cover=null;
function staged(slot,obj,labels){const mark=stageBar(slot,labels,i=>ctl.set(i));const ctl={count:labels.length,index:0,set(i){if(i<0||i>=labels.length)return;ctl.index=i;obj.setStage(i)},mark};obj.bind(ctl);window.stageCtl=ctl;obj.setStage(0);return ctl}
function mountGlobe(){const slot=$('gdelt-slot');if(!slot)return;slot.innerHTML='<div class="stage3d" id="globe3d"><button class="s3-switch" id="to-2d">2B harita</button></div>';const g=Globe($('globe3d'));active=g;staged(slot,g,['Haber sayısı','Aktif kuruluş başına','Anılan yerler · Meta hedefleri']);$('to-2d').onclick=e=>{e.stopPropagation();window.GDELT_FORCE_2D=true;go(scene)}}
function mountGalaxy(){const slot=$('galaxy-slot');if(!slot)return;slot.innerHTML='<div class="stage3d" id="galaxy3d"></div>';const g=Galaxy($('galaxy3d'));active=g;staged(slot,g,['Üç sınıf','Marka taklitleri','Harf karışımı aileleri','Altı uzantı'])}
const bg=document.createElement('div');bg.id='bg3d';document.querySelector('main.slide').prepend(bg);
const prev=window.onSlideRendered;
window.onSlideRendered=s=>{
 if(active){active.dispose();active=null}window.stageCtl=null;
 if(prev)prev(s);
 try{
  if(s.visual==='gdelt_map'&&window.use3D())mountGlobe();
  if(s.visual==='galaxy3d'&&webglOK()&&D.typology)mountGalaxy();
  if(s.visual==='cover'&&webglOK()&&D.globe){if(!cover)cover=Globe(bg,{ambient:true})}else if(cover){cover.dispose();cover=null}
 }catch(e){console.warn('3B sahne açılamadı; 2B görsele dönülüyor',e);GL=false;window.stageCtl=null;if(active){try{active.dispose()}catch(x){}active=null}go(scene)}
};
window.scene3d={get active(){return active},get cover(){return cover}};
if(typeof S!=='undefined')window.onSlideRendered(S[scene]);
})();
