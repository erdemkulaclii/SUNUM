"""Sensitivity scan for German-language disclosure coverage (26-30 Sep 2022).

A deliberately loose rule without any Russia requirement: forged/cloned/fake-site terms together
with an outlet/media term, or explicit campaign/disinformation-network wording. Applied to German
translingual records and to records from German-source domains. Output is reviewed by hand.
"""
import json, re, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'scripts'))
import gdelt_gkg_archive as g

LOOSE = re.compile(r'(gefälscht|gefaelscht|fälschung|gefakt|fake|geklont|klon|kopie|imitier|nachgeahmt|nachgemacht|doppelg|täuschend echt)', re.I)
MEDIA = re.compile(r'(spiegel|\bbild\b|t-online|\bwelt\b|\bfaz\b|süddeutsche|tagesspiegel|zeitung|medien|nachrichten|news|webseite|website|seiten|portal)', re.I)
CAMP = re.compile(r'(desinformationskampagne|desinformations-kampagne|propaganda-netzwerk|propagandanetzwerk|fake-netzwerk|troll-armee|trollarmee|einflusskampagne)', re.I)


def loose(title, url, cc, language='', country=''):
    if not (language == 'deu' or country == 'Germany'):
        return None
    t = f'{title} {url}'
    if (LOOSE.search(t) and MEDIA.search(t)) or CAMP.search(t):
        return 'LOOSE_de'
    return None


def main():
    g.classify = loose
    dc, _ = g.load_domains()
    entries = [e for s in ('eng', 'trans') for e in g.master_entries(s, '20220926', '20220930')]
    out = []
    import concurrent.futures as cf
    def job(e):
        try:
            return g.process(e, dc)[3]
        except Exception as exc:
            return [{'error': str(exc), 'url': e['url']}]
    with cf.ThreadPoolExecutor(16) as ex:
        for hits in ex.map(job, entries):
            out.extend(hits)
    out = g.dedupe([h for h in out if 'error' not in h])
    p = R / 'research/gdelt/gkg_archive/sensitivity_de_20220926_30.jsonl'
    with p.open('w') as fh:
        for h in sorted(out, key=lambda h: h['date']):
            fh.write(json.dumps({k: h[k] for k in ('date', 'url', 'domain', 'sourcecountry', 'language', 'title')}, ensure_ascii=False) + '\n')
    print(len(entries), 'files;', len(out), 'loose German candidates →', p.relative_to(R))


if __name__ == '__main__':
    main()
