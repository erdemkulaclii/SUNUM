"""Reproduce structural findings from Meta's archived September 2022 IOC CSV.

No live domains are visited. Analysis units are distinct domain strings, not
operations, content, operators, registration prices, or audience effects.
"""
from __future__ import annotations
from pathlib import Path
from collections import Counter, defaultdict
import argparse,csv,hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_SOURCE=ROOT/'research/meta/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv'
COMMIT='2d664e985e55fb754de7b1175f713e11f73cf8c8'
EXPECTED_SHA256='9f216a37e15c4772019d20ee620eafabf57a3876d4a7ab72fff5330fa8167d8d'
SOURCE_URL='https://github.com/facebook/threat-research/blob/'+COMMIT+'/indicators/csv/'+DEFAULT_SOURCE.name
EXPECTED_COUNTRIES={'Germany':298,'UK':4,'France':2,'Italy':2,'Latvia':3,'Ukraine':1,'Multiple':1}
EXPECTED_TOP_SIX={'online':53,'website':50,'site':46,'space':42,'pw':28,'fun':21}

def defang(value):return value.replace('.','[.]')
def share(n,total):return round(100*n/total,6) if total else None

def load_source(path):
    entries=[]
    with path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        expected=['indicator_type','indicator_value','comment','ds']
        if reader.fieldnames!=expected:raise ValueError(f'Unexpected source schema: {reader.fieldnames}')
        for ordinal,row in enumerate(reader,1):
            entries.append({**row,'source_record_ordinal':ordinal,'source_csv_line_end':reader.line_num})
    return entries

def analyze(path):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=EXPECTED_SHA256:raise ValueError('Source bytes differ from the pinned archived CSV; review required before attributing the published dataset.')
    source=load_source(path)
    domain_rows=[r for r in source if r['indicator_type']=='domain_name']
    grouped=defaultdict(list)
    for row in domain_rows:
        canonical=row['indicator_value'].strip().lower()
        if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?',canonical) or '..' in canonical or '.' not in canonical:
            raise ValueError('Invalid DNS-style domain string in source; manual review required')
        if any(not label or label.startswith('-') or label.endswith('-') for label in canonical.split('.')):
            raise ValueError('Invalid DNS label in source; manual review required')
        grouped[canonical].append(row)
    records=[]
    for canonical,rows in sorted(grouped.items()):
        labels={r['comment'] for r in rows}
        dates={r['ds'] for r in rows}
        if len(labels)!=1 or len(dates)!=1:raise ValueError('Repeated domain has conflicting source labels/dates')
        label=next(iter(labels))
        match=re.fullmatch(r'(.+)-targeting CIB domain',label)
        if not match:raise ValueError('Missing explicit target-country source label')
        parts=canonical.split('.')
        records.append({'canonical_domain':canonical,'defanged_domain':defang(canonical),
                        'source_target_label':match.group(1),'source_comment':label,
                        'source_ds':next(iter(dates)),'first_dns_label':parts[0],
                        'last_dns_label':parts[-1],'dns_label_count':len(parts),
                        'source_record_ordinals':[r['source_record_ordinal'] for r in rows],
                        'source_csv_line_ends':[r['source_csv_line_end'] for r in rows],
                        'source_row_count':len(rows)})
    total=len(records)
    countries=Counter(r['source_target_label'] for r in records)
    suffixes=Counter(r['last_dns_label'] for r in records)
    country_suffix=Counter((r['source_target_label'],r['last_dns_label']) for r in records)
    families=defaultdict(list)
    for row in records:families[row['first_dns_label']].append(row)
    family_rows=[]
    for first,members in sorted(families.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        distinct=sorted({r['last_dns_label'] for r in members})
        family_rows.append({'first_dns_label':first,'domain_count':len(members),
                            'distinct_last_label_count':len(distinct),'last_dns_labels':distinct,
                            'source_target_labels':sorted({r['source_target_label'] for r in members}),
                            'is_multi_suffix_family':len(distinct)>1,
                            'canonical_domains':[r['canonical_domain'] for r in members],
                            'defanged_domains':[r['defanged_domain'] for r in members],
                            'source_record_ordinals':sorted(n for r in members for n in r['source_record_ordinals'])})
    reused=[f for f in family_rows if f['is_multi_suffix_family']]
    reused_domains=sum(f['domain_count'] for f in reused)
    top6=[{'last_dns_label':k,'domain_count':v,'share_percent':share(v,total)} for k,v in suffixes.most_common(6)]
    types=Counter(r['indicator_type'] for r in source)
    result={
      'analysis_title':'Meta 2022 CIB alan adı göstergelerinin yapısal analizi',
      'source':{'path':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                'url':SOURCE_URL,'commit':COMMIT,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'bytes':path.stat().st_size,'columns':['indicator_type','indicator_value','comment','ds']},
      'method':{
       'unit':'Distinct canonical domain string; not an operation or a content item.',
       'canonicalization':'Strip surrounding whitespace and lowercase; group on full domain string.',
       'target_country':'Exact country component of source comment: <label>-targeting CIB domain. Never inferred from DNS suffix or hosting.',
       'last_dns_label':'Literal text after the last dot. This is the root DNS/TLD label, not effective public suffix or registrable-domain boundary.',
       'first_dns_label':'Literal text before the first dot. Exact equality only; no fuzzy matching, publisher identity coding, or operator attribution.',
       'source_record_ordinal':'One-based data-record position excluding header.',
       'source_csv_line_end':'Physical CSV line number at end of record, including header.',
       'time':'ds is the source record date. It is not registration time, first activity, or publication date of a linked story.',
       'network_requests':0},
      'audit':{'raw_records':len(source),'raw_record_types':dict(types),'domain_rows':len(domain_rows),
               'unique_domains':total,'duplicate_rows_removed':len(domain_rows)-total,
               'duplicate_domains':[{'domain':r['defanged_domain'],'source_record_ordinals':r['source_record_ordinals']} for r in records if r['source_row_count']>1],
               'source_ds_distribution':dict(Counter(r['ds'] for r in source)),
               'unique_domain_ds_distribution':dict(Counter(r['source_ds'] for r in records)),
               'activity_timeline_supported':False,'source_sha256_verified':True},
      'findings':{
       'target_country_counts':dict(countries),
       'last_dns_label_count':len(suffixes),
       'top_six_last_dns_labels':top6,
       'top_six_last_dns_label_domains':sum(r['domain_count'] for r in top6),
       'top_six_last_dns_label_share_percent':share(sum(r['domain_count'] for r in top6),total),
       'top_six_all_targeted_Germany':all(r['source_target_label']=='Germany' for r in records if r['last_dns_label'] in {r['last_dns_label'] for r in top6}),
       'distinct_first_dns_labels':len(families),
       'multi_suffix_first_label_families':len(reused),
       'domains_in_multi_suffix_first_label_families':reused_domains,
       'multi_suffix_first_label_domain_share_percent':share(reused_domains,total),
       'singleton_first_label_families':sum(f['domain_count']==1 for f in family_rows),
       'dns_label_count_distribution':dict(Counter(r['dns_label_count'] for r in records)),
       'activity_timeline_supported':False},
      'interpretation_limits':[
       'The last DNS label does not measure registration price, hosting location, or targeted country. No suffix is classified as cheap.',
       'Exact first-label reuse is a lexical pattern; it does not independently establish a common operator, campaign, publisher identity, content imitation, or intent.',
       'Country and suffix shares describe this published selection. They are not estimates of all Russian operations or public-opinion effects.',
       'All350 source records and all311 distinct domains have ds=2022-09-27; no activity timeline can be derived from ds.',
       'Examples containing intermediate labels, such as bild.eu.com and theguardian.co.com, have last DNS label com. No Public Suffix List join was performed.'],
      'last_dns_label_distribution':[{'last_dns_label':k,'domain_count':v,'share_percent':share(v,total)} for k,v in sorted(suffixes.items(),key=lambda kv:(-kv[1],kv[0]))],
      'target_by_last_dns_label':[{'source_target_label':k,'last_dns_label':t,'domain_count':n} for (k,t),n in sorted(country_suffix.items())],
      'first_label_families':family_rows,
      'records':records}
    validate(result)
    return result

def validate(result):
    a=result['audit'];f=result['findings'];records=result['records']
    assert (a['raw_records'],a['domain_rows'],a['unique_domains'],a['duplicate_rows_removed'])==(350,313,311,2),'Archived source counts changed; review required.'
    assert a['raw_record_types']=={'cib_url':22,'domain_name':313,'telegram_url':15},'Record-type partition changed.'
    assert f['target_country_counts']==EXPECTED_COUNTRIES,'Source-country classification differs from archived snapshot.'
    assert {r['last_dns_label']:r['domain_count'] for r in f['top_six_last_dns_labels']}==EXPECTED_TOP_SIX
    assert a['source_ds_distribution']=={'2022-09-27':350}
    assert sum(r['domain_count'] for r in result['last_dns_label_distribution'])==len(records)
    assert sum(r['domain_count'] for r in result['target_by_last_dns_label'])==len(records)
    assert sum(r['domain_count'] for r in result['first_label_families'])==len(records)
    ordinals=[n for r in records for n in r['source_record_ordinals']]
    assert len(ordinals)==313 and len(set(ordinals))==313,'Source-row trace was lost or duplicated.'
    assert len({r['canonical_domain'] for r in records})==311
    assert all(r['first_dns_label']==r['canonical_domain'].split('.')[0] and r['last_dns_label']==r['canonical_domain'].split('.')[-1] for r in records)
    f['audit_passed']=True

def csv_report(path,fields,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(row[k],ensure_ascii=False) if isinstance(row.get(k),(list,dict)) else row.get(k,'') for k in fields})

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path,default=DEFAULT_SOURCE);parser.add_argument('--output',type=Path,default=ROOT/'output');args=parser.parse_args()
    result=analyze(args.source.resolve());out=args.output;out.mkdir(exist_ok=True,parents=True)
    (out/'IOC_YAPISAL_ANALIZ.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    csv_report(out/'IOC_SON_ETIKET_DAGILIMI.csv',['last_dns_label','domain_count','share_percent'],result['last_dns_label_distribution'])
    csv_report(out/'IOC_HEDEF_SON_ETIKET.csv',['source_target_label','last_dns_label','domain_count'],result['target_by_last_dns_label'])
    csv_report(out/'IOC_GOVDE_AILELERI.csv',['first_dns_label','domain_count','distinct_last_label_count','is_multi_suffix_family','last_dns_labels','source_target_labels','defanged_domains','source_record_ordinals'],result['first_label_families'])
    csv_report(out/'IOC_YAPISAL_KANIT.csv',['canonical_domain','defanged_domain','source_target_label','source_ds','first_dns_label','last_dns_label','dns_label_count','source_row_count','source_record_ordinals','source_csv_line_ends'],result['records'])
    f=result['findings'];print(json.dumps({'unique_domains':result['audit']['unique_domains'],'distinct_last_labels':f['last_dns_label_count'],'top_six_total':f['top_six_last_dns_label_domains'],'top_six_share_percent':f['top_six_last_dns_label_share_percent'],'first_label_families':f['distinct_first_dns_labels'],'multi_suffix_families':f['multi_suffix_first_label_families'],'domains_in_multi_suffix_families':f['domains_in_multi_suffix_first_label_families'],'multi_suffix_domain_share_percent':f['multi_suffix_first_label_domain_share_percent'],'source_ds':result['audit']['source_ds_distribution'],'audit_passed':f['audit_passed']},ensure_ascii=False))

if __name__=='__main__':main()
