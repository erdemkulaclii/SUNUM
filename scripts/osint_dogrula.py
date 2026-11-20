"""OSINT doğrulama aracı: makaledeki iddiaları açık kaynaklara karşı sınar.

Kendi bilgisayarınızda çalıştırın (yalnız Python 3 standart kitaplığı gerekir):

    python3 scripts/osint_dogrula.py                 # hepsi (haberler ve alan adları ~20-40 dk)
    python3 scripts/osint_dogrula.py --kaynaklar     # yalnız kaynakça ve ek iddialar (~2 dk)
    python3 scripts/osint_dogrula.py --alanlar --haberler --meta --gdelt

Ne yapar:
  kaynaklar  Kaynakçadaki her DOI'yi Crossref'te arar (başlık, ilk yazar, yıl eşleşiyor mu),
             her bağlantıyı açar (canlı mı, sayfa başlığı ne) ve Wayback'te kopyasını arar.
             Makalede kaynakçası doğrulanamamış iki iddia için (VIGINUM raporu, Galeotti 2014)
             aday sayfaları açıp beklenen ifadeleri arar.
  haberler   Eşleşen 511 haberin bağlantısı bugün açılıyor mu, 27 Eylül 2022'ye en yakın
             Wayback kopyası var mı.
  alanlar    Meta listesindeki 311 alan adının bugün DNS'te çözülüp çözülmediği, RDAP kayıt
             bilgisi (kayıt / bitiş tarihi, kayıt şirketi) ve Wayback'teki ilk ve son kopya tarihi.
             Bu alan adlarına HTTP isteği GÖNDERİLMEZ (yalnız DNS, RDAP ve arşiv sorgusu).
  meta       Meta'nın sabit commit'teki CSV'sini indirip SHA-256'sını depodaki kopyayla karşılaştırır.
  gdelt      Manifestteki dosyalardan rastgele birkaçını indirip MD5'ini yeniden doğrular.

Çıktılar output/osint/ altına yazılır: OSINT_RAPORU.md ve her bölüm için bir CSV.
Yanıtlar output/osint/onbellek.json içinde saklanır; yarıda kalan bir çalıştırma kaldığı yerden
devam eder (--onbellegi-sil ile sıfırlanır).
"""
from __future__ import annotations

import argparse, concurrent.futures as cf, csv, difflib, hashlib, html, json, random, re, socket, ssl, sys, threading, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
OUT = R / 'output' / 'osint'
UA = 'Mozilla/5.0 (X11; Linux x86_64) osint-dogrulama/1.0 (akademik yeniden-uretilebilirlik denetimi)'
DISCLOSURE = '20220927'
META_URL = ('https://raw.githubusercontent.com/facebook/threat-research/2d664e985e55fb754de7b1175f713e11f73cf8c8/'
            'indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv')
META_LOCAL = R / 'research/meta/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv'
META_SHA256 = '9f216a37e15c4772019d20ee620eafabf57a3876d4a7ab72fff5330fa8167d8d'

# Kaynakçası bu ortamdan doğrulanamayan iddialar: aday sayfalar ve sayfada aranacak ifadeler.
EXTRA_CLAIMS = [
    {'id': 'VIGINUM_RRN_2023',
     'iddia': 'VIGINUM, Haziran 2023’te RRN/Doppelgänger kampanyasını Rus aktörlere bağlayan teknik bir rapor yayımladı.',
     'urls': ['https://www.sgdsn.gouv.fr/publications/maj-19062023-rrn-une-campagne-numerique-de-manipulation-de-linformation-complexe-et-persistante',
              'https://www.sgdsn.gouv.fr/publications',
              'https://www.diplomatie.gouv.fr/fr/politique-etrangere-de-la-france/securite-desarmement-et-non-proliferation/'],
     'beklenen': ['RRN', 'VIGINUM']},
    {'id': 'GALEOTTI_2014',
     'iddia': 'Galeotti “Gerasimov doctrine” ifadesini Temmuz 2014’te In Moscow’s Shadows blogunda ortaya attı.',
     'urls': ['https://inmoscowsshadows.wordpress.com/2014/07/06/the-gerasimov-doctrine-and-russian-non-linear-war/'],
     'beklenen': ['Gerasimov', '2014']},
]


# ---------------------------------------------------------------- HTTP katmanı
class Http:
    """Önbellekli, ana makine başına hız sınırlı GET. Testlerde `fetch` değiştirilebilir."""

    def __init__(self, cache_path: Path | None, min_interval: dict[str, float] | None = None, fetch=None, timeout: int = 25):
        self.cache_path, self.timeout = cache_path, timeout
        self.cache = json.loads(cache_path.read_text()) if cache_path and cache_path.is_file() else {}
        self.min_interval = {'web.archive.org': 1.0, 'archive.org': 1.0, 'rdap.org': 1.0, 'api.crossref.org': .2, **(min_interval or {})}
        self.last, self.lock, self.host_locks = {}, threading.Lock(), {}
        self.fetch = fetch or self._fetch
        self.dirty = 0

    def _host_lock(self, host):
        with self.lock:
            return self.host_locks.setdefault(host, threading.Lock())

    def _fetch(self, url: str, max_bytes: int) -> dict:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ssl.create_default_context()) as r:
                body = r.read(max_bytes)
                return {'status': r.status, 'final_url': r.geturl(), 'content_type': r.headers.get('Content-Type', ''),
                        'body': body.decode('utf-8', 'replace')}
        except urllib.error.HTTPError as e:
            return {'status': e.code, 'final_url': url, 'content_type': '', 'body': ''}
        except Exception as e:  # DNS, TLS, zaman aşımı
            msg = str(getattr(e, 'reason', e))
            return {'status': None, 'final_url': url, 'content_type': '', 'body': '', 'error': f'{type(e).__name__}: {msg}'[:120].replace('|', '/')}

    def get(self, url: str, max_bytes: int = 300_000, retries: int = 3) -> dict:
        if url in self.cache:
            return self.cache[url]
        host = urllib.parse.urlsplit(url).hostname or ''
        gap = next((v for k, v in self.min_interval.items() if host == k or host.endswith('.' + k)), 0)
        res = None
        for attempt in range(retries):
            with self._host_lock(host):
                wait = self.last.get(host, 0) + gap - time.monotonic()
                if wait > 0:
                    time.sleep(wait)
                self.last[host] = time.monotonic()
            res = self.fetch(url, max_bytes)
            if res.get('status') in (429, 502, 503, 504) or (res.get('status') is None and attempt < retries - 1 and 'timed out' in res.get('error', '')):
                time.sleep(2 ** attempt * 3)
                continue
            break
        if res.get('status') is None or res['status'] in (429,) or res['status'] >= 500:
            return res  # geçici hatalar önbelleğe alınmaz; sonraki çalıştırmada yeniden denenir
        with self.lock:
            self.cache[url] = res
            self.dirty += 1
            if self.dirty >= 50:
                self.save()
        return res

    def save(self):
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.cache_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(self.cache, ensure_ascii=False))
            tmp.replace(self.cache_path)
            self.dirty = 0


def page_title(body: str) -> str:
    m = re.search(r'<title[^>]*>(.*?)</title>', body or '', re.S | re.I)
    return re.sub(r'\s+', ' ', html.unescape(m.group(1))).strip()[:200] if m else ''


def wayback(http: Http, url: str, ts: str = DISCLOSURE) -> dict:
    r = http.get('https://archive.org/wayback/available?' + urllib.parse.urlencode({'url': url, 'timestamp': ts}), 50_000)
    try:
        snap = json.loads(r['body'])['archived_snapshots'].get('closest') or {}
    except Exception:
        return {'wayback_durum': 'sorgu başarısız', 'wayback_url': '', 'wayback_tarih': ''}
    if snap.get('available'):
        return {'wayback_durum': 'var', 'wayback_url': snap.get('url', ''), 'wayback_tarih': snap.get('timestamp', '')[:8]}
    return {'wayback_durum': 'yok', 'wayback_url': '', 'wayback_tarih': ''}


# ---------------------------------------------------------------- kaynakça
def parse_references(md: str) -> list[dict]:
    part = md.split('# Kaynakça', 1)[1]
    part = re.split(r'\n# ', part, 1)[0]
    refs = []
    for e in [x.strip() for x in part.strip().split('\n\n') if x.strip()]:
        m = re.match(r'(.+?)\s\((\d{4}|t\.y\.|n\.d\.)', e)
        doi = re.search(r'https?://doi\.org/(\S+?)\.?(?:\s|$)', e)
        urls = [u.rstrip('.,);') for u in re.findall(r'https?://\S+', e) if 'doi.org/' not in u]
        refs.append({'kaynak': e, 'ilk_yazar': re.split(r'[,.(]', e, 1)[0].strip(), 'yil': m.group(2) if m else '',
                     'doi': doi.group(1).rstrip('.') if doi else '', 'urls': urls})
    return refs


def norm_words(s: str) -> list[str]:
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or '')).lower()
    s = s.replace('*', ' ')
    return [w for w in re.findall(r'[\wçğıöşüäß]+', s) if len(w) > 3]


def title_match(crossref_title: str, entry: str) -> float:
    """Crossref başlığındaki anlamlı sözcüklerin kaynak girişinde geçme oranı (0-1)."""
    words = norm_words(crossref_title)
    if not words:
        return 0.0
    ent = set(norm_words(entry))
    hits = sum(1 for w in words if w in ent or difflib.get_close_matches(w, ent, 1, .88))
    return hits / len(words)


def check_doi(http: Http, ref: dict) -> dict:
    r = http.get('https://api.crossref.org/works/' + urllib.parse.quote(ref['doi'], safe='/'), 200_000)
    out = {'doi_durum': '', 'crossref_baslik': '', 'crossref_yil': '', 'crossref_ilk_yazar': '', 'baslik_uyumu': '', 'notlar': ''}
    if r.get('status') == 404:
        out['doi_durum'] = 'DOI Crossref’te YOK'
        return out
    if r.get('status') != 200:
        out['doi_durum'] = f"sorgu başarısız ({r.get('status') or r.get('error', '')})"
        return out
    try:
        w = json.loads(r['body'])['message']
    except Exception:
        out['doi_durum'] = 'yanıt okunamadı'
        return out
    title = (w.get('title') or [''])[0]
    year = ''
    for k in ('published-print', 'published-online', 'issued'):
        dp = (w.get(k) or {}).get('date-parts') or [[None]]
        if dp[0] and dp[0][0]:
            year = str(dp[0][0]); break
    years = {str(((w.get(k) or {}).get('date-parts') or [[None]])[0][0]) for k in ('published-print', 'published-online', 'issued')}
    first = ((w.get('author') or [{}])[0].get('family') or '')
    score = title_match(title, ref['kaynak'])
    out.update(crossref_baslik=title, crossref_yil=year, crossref_ilk_yazar=first, baslik_uyumu=f'{score:.2f}')
    notes = []
    if score < .8:
        notes.append('başlık uyuşmuyor')
    if ref['yil'] and ref['yil'] not in years:
        notes.append(f"yıl farklı (kaynakçada {ref['yil']}, Crossref {'/'.join(sorted(y for y in years if y != 'None'))})")
    if first and first.lower() not in ref['kaynak'].lower():
        notes.append(f'ilk yazar farklı (Crossref: {first})')
    out['doi_durum'] = 'doğrulandı' if not notes else 'UYUMSUZ'
    out['notlar'] = '; '.join(notes)
    return out


def check_url(http: Http, url: str) -> dict:
    r = http.get(url)
    title = page_title(r.get('body', ''))
    st = r.get('status')
    durum = 'açılıyor' if st and 200 <= st < 400 else (f'HTTP {st}' if st else f"erişilemedi ({r.get('error', '')[:60]})")
    return {'url': url, 'canli_durum': durum, 'son_url': r.get('final_url', ''), 'sayfa_basligi': title, **wayback(http, url)}


def run_references(http: Http, workers: int) -> tuple[list[dict], list[dict]]:
    refs = parse_references((R / 'makale/makale.md').read_text())
    rows = []

    def one(ref):
        base = {'ilk_yazar': ref['ilk_yazar'], 'yil': ref['yil'], 'doi': ref['doi'], 'kaynak': ref['kaynak'][:300]}
        res = []
        if ref['doi']:
            res.append({**base, 'tur': 'DOI', **check_doi(http, ref)})
        for u in ref['urls']:
            res.append({**base, 'tur': 'bağlantı', **check_url(http, u)})
        if not ref['doi'] and not ref['urls']:
            res.append({**base, 'tur': 'bağlantısız', 'notlar': 'DOI ya da bağlantı yok: elle doğrulanmalı (kütüphane kataloğu, dergi sitesi)'})
        return res

    with cf.ThreadPoolExecutor(workers) as ex:
        for res in ex.map(one, refs):
            rows.extend(res)
    claims = []
    for c in EXTRA_CLAIMS:
        found = []
        for u in c['urls']:
            r = http.get(u)
            body = r.get('body', '')
            hit = [p for p in c['beklenen'] if p.lower() in body.lower()]
            found.append({'url': u, 'durum': r.get('status') or r.get('error', ''), 'baslik': page_title(body), 'bulunan_ifadeler': ', '.join(hit),
                          'tam': len(hit) == len(c['beklenen']), **wayback(http, u)})
        claims.append({'id': c['id'], 'iddia': c['iddia'], 'sonuc': 'DOĞRULANDI' if any(f['tam'] for f in found) else 'doğrulanamadı', 'adaylar': found})
    return rows, claims


# ---------------------------------------------------------------- haberler
def load_articles() -> list[dict]:
    seen, out = set(), []
    for line in (R / 'research/gdelt/gkg_archive/matches.jsonl').read_text().splitlines():
        if not line:
            continue
        h = json.loads(line)
        if h['url'] in seen:
            continue
        seen.add(h['url'])
        out.append({'tarih': h['day'], 'alan_adi': h['domain'], 'ulke': h.get('sourcecountry', ''), 'baslik': h['title'], 'url': h['url']})
    return out


def run_articles(http: Http, workers: int, limit: int | None) -> list[dict]:
    arts = load_articles()[:limit] if limit else load_articles()

    def one(a):
        r = http.get(a['url'], 120_000)
        st = r.get('status')
        canli = 'açılıyor' if st and 200 <= st < 400 else (f'HTTP {st}' if st else 'erişilemedi')
        title = page_title(r.get('body', ''))
        same = ''
        if title and a['baslik']:
            same = f"{difflib.SequenceMatcher(None, title.lower(), a['baslik'].lower()).ratio():.2f}"
        return {**a, 'canli_durum': canli, 'son_url': r.get('final_url', ''), 'bugunku_baslik': title, 'baslik_benzerligi': same, **wayback(http, a['url'], a['tarih'])}

    with cf.ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, arts))


# ---------------------------------------------------------------- alan adları
def load_domains() -> list[dict]:
    t = json.loads((R / 'output/ALAN_ADI_TIPOLOJISI.json').read_text())
    return [{'alan_adi': r['canonical_domain'], 'sinif': r['class'], 'meta_hedef': r['source_target_label']} for r in t['rows']]


def parse_rdap(body: str) -> dict:
    try:
        j = json.loads(body)
    except Exception:
        return {}
    ev = {e.get('eventAction'): (e.get('eventDate') or '')[:10] for e in j.get('events', [])}
    registrar = ''
    for ent in j.get('entities', []):
        if 'registrar' in ent.get('roles', []):
            for item in (ent.get('vcardArray') or [None, []])[1]:
                if item and item[0] == 'fn':
                    registrar = item[3]
    return {'rdap_kayit': ev.get('registration', ''), 'rdap_bitis': ev.get('expiration', ''), 'rdap_degisiklik': ev.get('last changed', ''),
            'rdap_durum': ', '.join(j.get('status', [])), 'kayit_sirketi': registrar}


def parse_cdx(body: str) -> str:
    try:
        rows = json.loads(body)
    except Exception:
        return ''
    return rows[1][0][:8] if len(rows) > 1 and rows[1] else ''


def dns_resolves(domain: str) -> str:
    try:
        return ', '.join(sorted({a[4][0] for a in socket.getaddrinfo(domain, None)}))[:120] or 'çözüldü'
    except socket.gaierror:
        return ''
    except Exception as e:
        return f'hata: {type(e).__name__}'


def run_domains(http: Http, workers: int, limit: int | None, resolver=dns_resolves) -> list[dict]:
    doms = load_domains()[:limit] if limit else load_domains()
    socket.setdefaulttimeout(10)

    def one(d):
        name = d['alan_adi']
        r = http.get('https://rdap.org/domain/' + name, 100_000)
        rd = parse_rdap(r.get('body', '')) if r.get('status') == 200 else {}
        rdap_note = 'kayıtlı' if rd else ('kayıt bulunamadı (bırakılmış olabilir)' if r.get('status') == 404 else f"sorgu başarısız ({r.get('status') or r.get('error', '')[:40]})")
        cdx = 'https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode({'url': name, 'output': 'json', 'fl': 'timestamp', 'limit': '1'})
        cdx_last = 'https://web.archive.org/cdx/search/cdx?' + urllib.parse.urlencode({'url': name, 'output': 'json', 'fl': 'timestamp', 'limit': '-1'})
        first, last = parse_cdx(http.get(cdx, 20_000).get('body', '')), parse_cdx(http.get(cdx_last, 20_000).get('body', ''))
        ip = resolver(name)
        return {**d, 'dns_bugun': ip or 'çözülmüyor', 'rdap': rdap_note, **{k: rd.get(k, '') for k in ('rdap_kayit', 'rdap_bitis', 'rdap_degisiklik', 'rdap_durum', 'kayit_sirketi')},
                'wayback_ilk': first, 'wayback_son': last, 'ifsadan_once_arsivlenmis': ('evet' if first and first <= DISCLOSURE else ('hayır' if first else 'arşiv yok'))}

    with cf.ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, doms))


# ---------------------------------------------------------------- Meta ve GDELT
def download(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=120) as r:
        return r.read()


def run_meta(fetch_bytes=None) -> dict:
    try:
        remote = hashlib.sha256((fetch_bytes or download)(META_URL)).hexdigest()
    except Exception as ex:
        remote = f'indirilemedi ({type(ex).__name__})'
    local = hashlib.sha256(META_LOCAL.read_bytes()).hexdigest() if META_LOCAL.is_file() else ''
    return {'url': META_URL, 'uzak_sha256': remote, 'yerel_sha256': local, 'beklenen_sha256': META_SHA256,
            'sonuc': 'eşleşiyor' if remote == local == META_SHA256 else 'EŞLEŞMİYOR ya da indirilemedi'}


def run_gdelt(n: int, fetch_bytes=None) -> list[dict]:
    m = json.loads((R / 'research/gdelt/gkg_archive/manifest.json').read_text())
    sample = random.Random(2022).sample(m['entries'], min(n, len(m['entries'])))
    out = []
    for e in sample:
        try:
            blob = (fetch_bytes or download)(e['url'])
            md5 = hashlib.md5(blob).hexdigest()
            out.append({'dosya': e['url'].rsplit('/', 1)[-1], 'beklenen_md5': e['md5'], 'indirilen_md5': md5, 'sonuc': 'eşleşiyor' if md5 == e['md5'] else 'EŞLEŞMİYOR'})
        except Exception as ex:
            out.append({'dosya': e['url'].rsplit('/', 1)[-1], 'beklenen_md5': e['md5'], 'indirilen_md5': '', 'sonuc': f'indirilemedi ({type(ex).__name__})'})
    return out


# ---------------------------------------------------------------- rapor
def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(rows)


def pct(a, b):
    return f'{a}/{b} (%{a / b * 100:.1f})' if b else '0/0'


def report(sec: dict) -> str:
    L = [f"# OSINT doğrulama raporu", '', f"Çalıştırma: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", '']
    if 'kaynaklar' in sec:
        rows, claims = sec['kaynaklar']
        dois = [r for r in rows if r['tur'] == 'DOI']
        links = [r for r in rows if r['tur'] == 'bağlantı']
        L += ['## Kaynakça', '',
              f"- DOI: {pct(sum(r['doi_durum'] == 'doğrulandı' for r in dois), len(dois))} doğrulandı; "
              f"{sum(r['doi_durum'] == 'UYUMSUZ' for r in dois)} uyumsuz; {sum(r['doi_durum'].startswith('DOI') for r in dois)} Crossref’te yok; "
              f"{sum(r['doi_durum'].startswith('sorgu') for r in dois)} sorgu başarısız.",
              f"- Bağlantı: {pct(sum(r['canli_durum'] == 'açılıyor' for r in links), len(links))} bugün açılıyor; "
              f"{pct(sum(r['wayback_durum'] == 'var' for r in links), len(links))} Wayback’te kopyası var.",
              f"- DOI’si ve bağlantısı olmayan kaynak: {sum(r['tur'] == 'bağlantısız' for r in rows)} (elle doğrulanmalı).", '']
        bad = [r for r in dois if r['doi_durum'] != 'doğrulandı'] + [r for r in links if r['canli_durum'] != 'açılıyor' and r['wayback_durum'] != 'var']
        if bad:
            L += ['**Bakılması gerekenler**', '', '| Kaynak | Tür | Durum | Not |', '|---|---|---|---|']
            for r in bad:
                cell = lambda s: str(s or '').replace('|', '/').replace('\n', ' ')[:140]
                L.append(f"| {cell(r['ilk_yazar'])} ({r['yil']}) | {r['tur']} | {cell(r.get('doi_durum') or r.get('canli_durum'))} | {cell(r.get('notlar') or r.get('url', ''))} |")
            L.append('')
        L += ['## Ek iddialar', '']
        for c in claims:
            L.append(f"- **{c['id']}: {c['sonuc']}.** {c['iddia']}")
            for f in c['adaylar']:
                L.append(f"  - {f['url']} → {f['durum']}; bulunan: {f['bulunan_ifadeler'] or '—'}; Wayback: {f['wayback_url'] or 'yok'}")
        L.append('')
    if 'haberler' in sec:
        a = sec['haberler']
        L += ['## Eşleşen haberler', '', f"- Bugün açılıyor: {pct(sum(r['canli_durum'] == 'açılıyor' for r in a), len(a))}",
              f"- Wayback’te kopyası var: {pct(sum(r['wayback_durum'] == 'var' for r in a), len(a))}",
              f"- Ne canlı ne arşivde: {sum(r['canli_durum'] != 'açılıyor' and r['wayback_durum'] != 'var' for r in a)}", '']
    if 'alanlar' in sec:
        d = sec['alanlar']
        firsts = sorted(r['wayback_ilk'] for r in d if r['wayback_ilk'])
        L += ['## Meta’nın 311 alan adı', '', f"- Bugün DNS’te çözülüyor: {pct(sum(r['dns_bugun'] != 'çözülmüyor' for r in d), len(d))}",
              f"- RDAP’ta kayıtlı: {pct(sum(r['rdap'] == 'kayıtlı' for r in d), len(d))} (bugünkü kayıt eski sahibine ait olmayabilir)",
              f"- Wayback’te kopyası olan: {pct(len(firsts), len(d))}; ifşadan (27.09.2022) önce arşivlenmiş: {sum(r['ifsadan_once_arsivlenmis'] == 'evet' for r in d)}",
              f"- En erken arşiv kopyası: {firsts[0] if firsts else '—'}; en geç ilk kopya: {firsts[-1] if firsts else '—'}", '']
    if 'meta' in sec:
        m = sec['meta']
        L += ['## Meta gösterge dosyası', '', f"- Sonuç: **{m['sonuc']}** (uzak {m['uzak_sha256'][:16]}…, yerel {m['yerel_sha256'][:16]}…)", '']
    if 'gdelt' in sec:
        g = sec['gdelt']
        L += ['## GDELT örnek dosyaları', '', f"- MD5 eşleşen: {pct(sum(r['sonuc'] == 'eşleşiyor' for r in g), len(g))}", '']
    L += ['Ayrıntılar aynı klasördeki CSV dosyalarındadır.', '']
    return '\n'.join(L)


def main(argv=None, http: Http | None = None, out_dir: Path = OUT, resolver=dns_resolves, gdelt_fetch=None) -> dict:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ('kaynaklar', 'haberler', 'alanlar', 'meta', 'gdelt'):
        p.add_argument('--' + k, action='store_true')
    p.add_argument('--is-parcacigi', type=int, default=6, help='eşzamanlı istek sayısı (varsayılan 6)')
    p.add_argument('--sinir', type=int, help='haber ve alan adı sayısını sınırla (deneme için)')
    p.add_argument('--gdelt-ornek', type=int, default=3, help='MD5’i yeniden doğrulanacak GDELT dosyası sayısı')
    p.add_argument('--onbellegi-sil', action='store_true')
    a = p.parse_args(argv)
    sel = [k for k in ('kaynaklar', 'haberler', 'alanlar', 'meta', 'gdelt') if getattr(a, k)] or ['kaynaklar', 'meta', 'gdelt', 'alanlar', 'haberler']
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = out_dir / 'onbellek.json'
    if a.onbellegi_sil and cache.exists():
        cache.unlink()
    http = http or Http(cache)
    sec = {}
    try:
        for k in sel:
            print(f'→ {k} …', flush=True)
            if k == 'kaynaklar':
                rows, claims = run_references(http, a.is_parcacigi)
                write_csv(out_dir / 'KAYNAK_KONTROL.csv', rows)
                (out_dir / 'EK_IDDIALAR.json').write_text(json.dumps(claims, ensure_ascii=False, indent=1))
                sec[k] = (rows, claims)
            elif k == 'haberler':
                sec[k] = run_articles(http, a.is_parcacigi, a.sinir)
                write_csv(out_dir / 'HABER_URL_KONTROL.csv', sec[k])
            elif k == 'alanlar':
                sec[k] = run_domains(http, a.is_parcacigi, a.sinir, resolver)
                write_csv(out_dir / 'ALAN_ADI_KONTROL.csv', sec[k])
            elif k == 'meta':
                sec[k] = run_meta(gdelt_fetch)
                (out_dir / 'META_KONTROL.json').write_text(json.dumps(sec[k], ensure_ascii=False, indent=1))
            elif k == 'gdelt':
                sec[k] = run_gdelt(a.gdelt_ornek, gdelt_fetch)
                write_csv(out_dir / 'GDELT_KONTROL.csv', sec[k])
    finally:
        http.save()
    text = report(sec)
    (out_dir / 'OSINT_RAPORU.md').write_text(text)
    print('\n' + text)
    print(f'Rapor: {out_dir / "OSINT_RAPORU.md"}')
    return sec


if __name__ == '__main__':
    main()
