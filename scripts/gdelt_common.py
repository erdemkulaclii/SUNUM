"""Shared GDELT map definitions: query, windows, chunking and aggregation.

Used by fetch_gdelt_map.py (command line) and serve_presentation.py (local
proxy). Nothing here invents observations: aggregation only counts articles
that a real GDELT response returned.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from collections import Counter
from urllib.parse import urlencode

DOC_ENDPOINT = 'https://api.gdeltproject.org/api/v2/doc/doc'
SCHEMA = 'sunum.gdelt-map/1'
MAX_RECORDS = 250

# One fixed, documented query. Keyword choice: the campaign name in two
# spellings plus Meta's own term for the takedown category.
QUERY = '(doppelganger OR "doppelgänger" OR "coordinated inauthentic") (russia OR russian OR meta OR facebook)'

WINDOWS = {
    'meta2022': {
        'label': 'Meta duyuru penceresi · 20 Eylül – 11 Ekim 2022',
        'start': '2022-09-20', 'end': '2022-10-11', 'chunk_days': 3,
        'note': 'DOC 2.0 resmî olarak son üç ayı destekler; bu tarihsel pencere veri döndürebilir ama garanti edilmez. Kesin 2022 analizi için GKG/BigQuery yolu kullanılmalıdır.',
    },
    'recent30': {
        'label': 'Son 30 gün (güncel izleme)', 'days': 30, 'chunk_days': 5,
        'note': 'Güncel haber seçkisi; 2022 vakasının tarihsel karşılaştırması değildir.',
    },
}


def window_range(window_id: str, today: dt.date | None = None) -> tuple[dt.date, dt.date]:
    w = WINDOWS[window_id]
    if 'start' in w:
        return dt.date.fromisoformat(w['start']), dt.date.fromisoformat(w['end'])
    end = today or dt.datetime.now(dt.timezone.utc).date()
    return end - dt.timedelta(days=w['days']), end


def chunks(start: dt.date, end: dt.date, days: int) -> list[tuple[dt.datetime, dt.datetime]]:
    """Inclusive date range → [start, end) UTC datetime slices."""
    out, cur, stop = [], dt.datetime.combine(start, dt.time()), dt.datetime.combine(end + dt.timedelta(days=1), dt.time())
    while cur < stop:
        nxt = min(cur + dt.timedelta(days=days), stop)
        out.append((cur, nxt))
        cur = nxt
    return out


def stamp(value: dt.datetime) -> str:
    return value.strftime('%Y%m%d%H%M%S')


def doc_url(start: dt.datetime, end: dt.datetime, query: str = QUERY) -> str:
    params = {'query': query, 'mode': 'artlist', 'format': 'json', 'maxrecords': MAX_RECORDS,
              'sort': 'dateasc', 'startdatetime': stamp(start), 'enddatetime': stamp(end - dt.timedelta(seconds=1))}
    return DOC_ENDPOINT + '?' + urlencode(params)


STAMP_RE = re.compile(r'^\d{14}$')


def valid_chunk_params(start: str, end: str) -> bool:
    if not (STAMP_RE.match(start or '') and STAMP_RE.match(end or '')):
        return False
    try:
        a = dt.datetime.strptime(start, '%Y%m%d%H%M%S')
        b = dt.datetime.strptime(end, '%Y%m%d%H%M%S')
    except ValueError:
        return False
    return dt.datetime(2017, 1, 1) <= a < b and (b - a) <= dt.timedelta(days=31)


def parse_doc(raw: bytes) -> list[dict]:
    """Parse a DOC artlist response. Empty matches come back as `{}`.

    GDELT answers rate-limit or syntax problems with plain text; those raise
    ValueError so they are never mistaken for "zero articles".
    """
    text = raw.decode('utf-8', errors='replace').strip()
    if not text.startswith('{'):
        raise ValueError('GDELT JSON yerine metin döndürdü: ' + text[:160])
    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        body = json.loads(re.sub(r'[\x00-\x1f]', ' ', text))
    if not isinstance(body, dict):
        raise ValueError('Beklenmeyen DOC şeması')
    articles = body.get('articles', [])
    if not isinstance(articles, list):
        raise ValueError('DOC articles alanı liste değil')
    return [a for a in articles if isinstance(a, dict) and a.get('url')]


KEEP = ('url', 'title', 'seendate', 'domain', 'language', 'sourcecountry')


def aggregate(articles: list[dict]) -> dict:
    seen, unique = set(), []
    for a in articles:
        key = a['url'].strip()
        if key in seen:
            continue
        seen.add(key)
        unique.append({k: (a.get(k) or '') for k in KEEP})
    countries = Counter(a['sourcecountry'] or 'Bilinmiyor' for a in unique)
    languages = Counter(a['language'] or 'Bilinmiyor' for a in unique)
    return {
        'articles': unique,
        'source_countries': [{'name': k, 'count': v} for k, v in countries.most_common()],
        'languages': [{'name': k, 'count': v} for k, v in languages.most_common()],
        'unique_articles': len(unique),
    }


def snapshot(window_id: str, start: dt.date, end: dt.date, chunk_log: list[dict], articles: list[dict], origin: str) -> dict:
    agg = aggregate(articles)
    return {
        'schema': SCHEMA,
        'provider': 'GDELT Project DOC 2.0 API (artlist)',
        'query': QUERY,
        'window': {'id': window_id, 'label': WINDOWS[window_id]['label'], 'start': start.isoformat(), 'end': end.isoformat(), 'note': WINDOWS[window_id]['note']},
        'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'origin': origin,
        'chunks': chunk_log,
        'capped_chunks': sum(1 for c in chunk_log if c.get('capped')),
        'failed_chunks': sum(1 for c in chunk_log if c.get('status') != 'ok'),
        **agg,
        'locations': None,
        'warnings': [
            'sourcecountry haberin yayımlandığı ülkedir; hedef ülke veya okur ülkesi değildir.',
            'Her dilim en fazla 250 makale döndürür; capped=true olan dilimlerde seçki eksiktir.',
            'Eşleşme anahtar sözcüğe dayanır; makalelerin konuyla ilgisi elle kodlanmamıştır.',
        ],
    }


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_v2locations(value: str) -> list[dict]:
    """GKG V2Locations: 'type#name#cc#adm1#adm2#lat#lon#featureid#offset;...'."""
    out = []
    for block in (value or '').split(';'):
        parts = block.split('#')
        if len(parts) < 8:
            continue
        try:
            lat, lon = float(parts[5]), float(parts[6])
        except ValueError:
            continue
        out.append({'type': parts[0], 'name': parts[1], 'country_code': parts[2], 'lat': round(lat, 4), 'lon': round(lon, 4), 'feature_id': parts[7]})
    return out
