"""Static GDELT map image for the PowerPoint/PDF copy (real snapshot only)."""
from __future__ import annotations
import json,math,re,sys,unicodedata
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
R=Path(__file__).resolve().parents[1]
ALIAS={'unitedstates':'United States of America','czechrepublic':'Czechia','bosniaherzegovina':'Bosnia and Herzegovina','macedonia':'North Macedonia','serbia':'Republic of Serbia','tanzania':'United Republic of Tanzania','burma':'Myanmar','swaziland':'eSwatini','congo':'Republic of the Congo','bahamas':'The Bahamas','slovakrepublic':'Slovakia','eastimor':'East Timor','russianfederation':'Russia','southkorea':'South Korea','korea':'South Korea'}
TARGETS=['Germany','United Kingdom','France','Italy','Latvia','Ukraine']
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower())
def world():
    geo=json.loads((R/'research/countries.geojson').read_text());out=[]
    for f in geo['features']:
        p=f['properties'];g=f['geometry'];polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        names={norm(p.get(k)) for k in ['ADMIN','NAME','NAME_LONG','NAME_EN','FORMAL_EN','NAME_ALT','BRK_NAME','GEOUNIT','SUBUNIT','NAME_SORT'] if p.get(k)}
        out.append({'admin':p['ADMIN'],'tr':p.get('NAME_TR') or p['ADMIN'],'names':names,'polys':polys})
    return out
def match(features):
    by={norm(f['admin']):f for f in features};idx={}
    for f in features:
        for n in f['names']:idx.setdefault(n,f)
    def find(name):
        k=norm(name)
        if k in ALIAS:return by.get(norm(ALIAS[k]))
        return by.get(k) or idx.get(k)
    return find
def counts(snap):
    seen=set();c=Counter()
    for a in snap.get('articles',[]):
        u=a.get('url','').strip()
        if u and u not in seen:seen.add(u);c[a.get('sourcecountry') or 'Bilinmiyor']+=1
    return c,len(seen)
def summary(snap):
    feats=world();find=match(feats);c,total=counts(snap);by=Counter()
    for k,v in c.items():
        f=find(k)
        if f:by[f['admin']]+=v
    de=by.get('Germany',0);top=[(find(k)['tr'] if find(k) else k,v) for k,v in c.most_common() if k!='Bilinmiyor'][:3]
    share=f"%{de/total*100:.1f}".replace('.',',') if total else '—'
    w=snap['window'];when=snap.get('retrieved_at','')[:10]
    return {'total':total,'germany_share':share,'line':f"{total} haber · en çok: "+', '.join(f'{n} {v}' for n,v in top)+f" · Almanya kaynaklı {share}",
            'caption':f"GDELT DOC 2.0 · {w['start']} – {w['end']} · {total} tekil haber · alındı {when} · sınıra takılan dilim: {snap.get('capped_chunks',0)} · kaynak ülke ≠ hedef ülke"}
def render(snap,out,width_in=7.1,height_in=3.75):
    feats=world();find=match(feats);c,total=counts(snap);by=Counter()
    for k,v in c.items():
        f=find(k)
        if f:by[f['admin']]+=v
    mx=max(by.values(),default=1)
    fig=plt.figure(figsize=(width_in,height_in),dpi=200);ax=fig.add_axes([0,0,1,1]);ax.set_facecolor('#dfe9f1')
    for f in feats:
        n=by.get(f['admin'],0);alpha=.18+.72*math.log1p(n)/math.log1p(mx) if n else 1
        color=(31/255,95/255,153/255,alpha) if n else '#eef2f5'
        patches=[Polygon(poly[0],closed=True) for poly in f['polys']]
        ax.add_collection(PatchCollection(patches,facecolor=color,edgecolor='#8ea3b6',linewidths=.3))
        if f['admin'] in TARGETS:
            ax.add_collection(PatchCollection([Polygon(poly[0],closed=True) for poly in f['polys']],facecolor='none',edgecolor='#c0392b',linewidths=1.6 if f['admin']=='Germany' else 1.0,linestyles='solid' if f['admin']=='Germany' else (0,(3,2))))
    rows=(snap.get('locations') or {}).get('rows') or []
    if rows:
        m=max(r['articles'] for r in rows)
        ax.scatter([r['lon'] for r in rows],[r['lat'] for r in rows],s=[8+120*(r['articles']/m) for r in rows],c='#f0a43a',edgecolors='#5b3a00',linewidths=.4,zorder=5)
    ax.set_xlim(-14,40);ax.set_ylim(34,64);ax.set_aspect(1.55,adjustable='datalim');ax.set_xticks([]);ax.set_yticks([]);[sp.set_visible(False) for sp in ax.spines.values()];fig.patch.set_facecolor('#dfe9f1')
    top=[(find(k)['tr'] if find(k) else k,v) for k,v in c.most_common() if k!='Bilinmiyor'][:6]
    txt='Kaynak ülke (tekil haber)\n'+'\n'.join(f'{n}: {v}' for n,v in top)
    ax.text(.985,.97,txt,transform=ax.transAxes,ha='right',va='top',fontsize=6.5,family='DejaVu Sans',bbox=dict(facecolor='white',edgecolor='#a9bccd',alpha=.95,boxstyle='square,pad=.5'))
    ax.text(.015,.03,'Mavi: haberin kaynak ülkesi · Turuncu: GKG anılan yer · Kırmızı çerçeve: Meta hedef etiketi',transform=ax.transAxes,fontsize=5.5,family='DejaVu Sans',bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
    fig.savefig(out,dpi=200);plt.close(fig)
