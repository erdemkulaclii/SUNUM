"""Census coding of all distinct matched titles, near-miss and loose German pools.

Coding rule (fixed before counting): RELEVANT = the title reports Meta's 27 Sep 2022 CIB takedown
announcement (Russian or Chinese network; both were in the same announcement) or the
Doppelgänger campaign. Everything else is NOT relevant.

First coder: AI-assisted (Claude), title + URL only. Second coder: the author fills
research/kodlama/insan_kodlama_formu.csv WITHOUT seeing the AI labels; `python scripts/gdelt_census.py`
then reports agreement and Cohen's kappa.
"""
from __future__ import annotations
import csv, json, sys
from collections import Counter
from pathlib import Path
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
from gdelt_gkg_archive import dedupe
from gdelt_validation import wilson, kappa
K = R / 'research/kodlama'
A = R / 'research/gdelt/gkg_archive'

# AI-assisted first coding: normalized titles judged NOT relevant (with reason). All others relevant.
NOT_RELEVANT = {
    'apple elimina dall\' app store il social vk |  il facebook russo': 'Apple–VK; Meta duyurusu değil',
    'apple removes russian facebook competitor vk from app store': 'Apple–VK',
    'apple removes russian facebook competitor vk from the app store, citing sanctions': 'Apple–VK',
    'apple remove vk, o "facebook da rússia", de sua app store em todo o mundo': 'Apple–VK',
    'apple removes russian facebook from its app store': 'Apple–VK',
    'apple, google und der russische facebook-klon vk': 'Apple–VK',
    'russia demands an explanation after apple removes its facebook competitor from the app store': 'Apple–VK',
    'çfarë ndodhi? rusia \'shtang\' me vendimin e fundit drastik ndaj meta-s, zbardhen detajet': 'Rusya’nın Meta kararı (Ekim 2022)',
    'facebook dhe instagram janë të paqasshëm atje, rusia merr një vendim për "meta-n"': 'Rusya’nın Meta kararı',
    'rusia në luftë me meta: kompania e zuckerberg përfshihet në listën e organizatave terroriste': 'Rusya’nın Meta’yı terör listesine alması',
    'ukraine war: finland closes border to russian tourists': 'Finlandiya sınırı',
    'wladimir putin ausgetauscht: geheimdienstchef glaubt an irre theorie: kreml-chef hat 3 doppelgänger': 'Putin’in “dublörleri”',
}
# Near-miss and loose-German pools: indices (file order) judged RELEVANT; all others not relevant.
NEARMISS_RELEVANT = {'https://www.watson.ch/digital/facebook/678520655-facebook-bestaetigt-so-hat-putins-troll-armee-westeuropa-attackiert': 'watson.ch 27.09: Facebook bestätigt … Troll-Armee'}


def norm(t: str) -> str:
    return t.strip().lower()


def load_matches():
    return dedupe([json.loads(l) for l in (A / 'matches.jsonl').read_text().splitlines() if l])


def census():
    hits = load_matches()
    by_title = {}
    for h in hits:
        by_title.setdefault(norm(h['title']), []).append(h)
    rows = []
    for t, hs in sorted(by_title.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        rel = 0 if t in NOT_RELEVANT else 1
        rows.append({'baslik': hs[0]['title'].strip(), 'haber_sayisi': len(hs), 'kural': Counter(h['rule'] for h in hs).most_common(1)[0][0],
                     'ornek_url': hs[0]['url'], 'ilgili_yz': rel, 'gerekce_yz': NOT_RELEVANT.get(t, 'Meta 27.09.2022 duyurusu / Doppelgänger')})
    with (K / 'yz_baslik_kodlama.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    form = K / 'insan_kodlama_formu.csv'
    if not form.exists():
        with form.open('w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh); w.writerow(['baslik', 'ornek_url', 'ilgili_insan (1/0)', 'not'])
            for r in sorted(rows, key=lambda r: r['baslik'].lower()):
                w.writerow([r['baslik'], r['ornek_url'], '', ''])
    n_t, rel_t = len(rows), sum(r['ilgili_yz'] for r in rows)
    n_a, rel_a = sum(r['haber_sayisi'] for r in rows), sum(r['haber_sayisi'] for r in rows if r['ilgili_yz'])
    out = {'titles': n_t, 'titles_relevant': rel_t, 'title_precision': round(rel_t / n_t, 3), 'title_wilson95': [round(x, 3) for x in wilson(rel_t, n_t)],
           'articles': n_a, 'articles_relevant': rel_a, 'article_precision': round(rel_a / n_a, 3),
           'by_rule': {r: {'articles': sum(x['haber_sayisi'] for x in rows if x['kural'] == r), 'relevant': sum(x['haber_sayisi'] for x in rows if x['kural'] == r and x['ilgili_yz'])} for r in sorted({x['kural'] for x in rows})}}
    # optional human agreement
    with form.open(encoding='utf-8') as fh:
        human = {norm(r['baslik']): r['ilgili_insan (1/0)'].strip() for r in csv.DictReader(fh)}
    pairs = [(r['ilgili_yz'], int(human[norm(r['baslik'])])) for r in rows if human.get(norm(r['baslik'])) in ('0', '1')]
    out['human_coded'] = len(pairs)
    if pairs:
        a, b = zip(*pairs)
        out['agreement'] = round(sum(x == y for x, y in pairs) / len(pairs), 3)
        out['cohen_kappa'] = None if kappa(list(a), list(b)) is None else round(kappa(list(a), list(b)), 3)
    return out, {norm(h['title']) for h in hits if norm(h['title']) not in NOT_RELEVANT}, hits


def recall_checks(hits):
    matched = {h['url'] for h in hits}
    near = [json.loads(l) for l in (A / 'nearmiss_de.jsonl').read_text().splitlines() if l]
    near_rel = [x for x in near if x['url'] in NEARMISS_RELEVANT]
    loose_path = A / 'sensitivity_de_20220926_30.jsonl'
    loose = [json.loads(l) for l in loose_path.read_text().splitlines() if l]
    # loose-German pool: relevant by the same rule (coded by title, AI-assisted)
    LOOSE_REL = ('meta löscht größtes pro-russisches', 'facebook zerschlägt propaganda-netzwerke', 'meta stoppt russische fake-news-kampagne',
                 'troll-armee westeuropa', 'russische fake-news-kampagne gestoppt', 'fake-news-netwerke lahm', 'wie facebook russischer propaganda den stecker zog')
    rel = [x for x in loose if any(k in norm(x['title']) for k in LOOSE_REL)]
    caught = [x for x in rel if x['url'] in matched]
    with (K / 'yakin_iska_kodlama.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(['havuz', 'tarih', 'alan_adi', 'baslik', 'ilgili_yz', 'kurallarca_yakalandi'])
        for x in near:
            w.writerow(['yakin_iska_de', x['date'][:8], x['domain'], x['title'], int(x in near_rel), 0])
        for x in loose:
            w.writerow(['gevsek_almanca_26_30_eylul', x['date'][:8], x['domain'], x['title'], int(x in rel), int(x['url'] in matched)])
    lo, hi = wilson(len(caught), len(rel))
    return {'nearmiss_pool': len(near), 'nearmiss_relevant': len(near_rel), 'loose_pool': len(loose), 'loose_relevant': len(rel),
            'loose_relevant_caught': len(caught), 'loose_recall': round(len(caught) / len(rel), 3), 'loose_recall_wilson95': [round(lo, 3), round(hi, 3)],
            'loose_relevant_germany_source': sum(x['sourcecountry'] == 'Germany' for x in rel),
            'loose_relevant_germany_source_caught': sum(x['sourcecountry'] == 'Germany' and x['url'] in matched for x in rel)}


def main():
    c, _, hits = census()
    r = recall_checks(hits)
    res = {'census': c, 'recall': r}
    (R / 'output/KODLAMA_SONUCLARI.json').write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
