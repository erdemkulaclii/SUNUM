"""Build the article (DOCX + PDF) from makale/makale.md after recomputing all numbers.

    python scripts/build_makale.py
"""
import subprocess, sys
from pathlib import Path
from docx import Document
from docx.shared import Pt
R = Path(__file__).resolve().parents[1]; M = R / 'makale'
subprocess.run([sys.executable, str(R / 'scripts/makale_istatistikleri.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, str(R / 'scripts/makale_sekiller.py')], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ref = M / 'referans.docx'
if not ref.exists():
    subprocess.run(['pandoc', '-o', str(ref), '--print-default-data-file', 'reference.docx'], check=True)
    d = Document(ref)
    styles = {st.name.lower(): st for st in d.styles if st.type == 1}
    small = {'caption', 'image caption', 'table'}
    sizes = {'title': 16, 'heading 1': 13, 'heading 2': 12, 'heading 3': 12, 'author': 12}
    for key, st in styles.items():
        if key in ('normal', 'body text', 'first paragraph', 'compact', 'bibliography', 'abstract', 'block text') or key in small or key in sizes:
            st.font.name = 'Times New Roman'
            st.font.size = Pt(10 if key in small else sizes.get(key, 12))
            if key in sizes:
                st.font.color.rgb = None
            st.paragraph_format.line_spacing = 1.0 if key in small or key in sizes else 1.5
    d.save(ref)
import json, re, sys
S = json.loads((R / 'output/MAKALE_SAYILARI.json').read_text())
TR = {'United States': 'ABD', 'Germany': 'Almanya', 'Italy': 'İtalya', 'India': 'Hindistan', 'China': 'Çin', 'Russia': 'Rusya', 'United Kingdom': 'Birleşik Krallık', 'Canada': 'Kanada', 'Bulgaria': 'Bulgaristan', 'Romania': 'Romanya', 'France': 'Fransa', 'Brazil': 'Brezilya', 'Slovak Republic': 'Slovakya', 'Portugal': 'Portekiz', 'Austria': 'Avusturya', 'Albania': 'Arnavutluk', 'Spain': 'İspanya', 'Poland': 'Polonya', 'Switzerland': 'İsviçre', 'Ukraine': 'Ukrayna', 'Czech Republic': 'Çekya', 'Netherlands': 'Hollanda', 'Belgium': 'Belçika', 'Norway': 'Norveç', 'Australia': 'Avustralya', 'Japan': 'Japonya', 'Pakistan': 'Pakistan', 'Indonesia': 'Endonezya', 'Philippines': 'Filipinler', 'Hungary': 'Macaristan', 'Greece': 'Yunanistan', 'Mexico': 'Meksika', 'Argentina': 'Arjantin', 'Ireland': 'İrlanda', 'Israel': 'İsrail', 'Egypt': 'Mısır', 'Kosovo': 'Kosova', 'Macedonia': 'Kuzey Makedonya', 'Serbia': 'Sırbistan', 'Lithuania': 'Litvanya', 'Latvia': 'Letonya', 'Estonia': 'Estonya', 'Sweden': 'İsveç', 'Denmark': 'Danimarka', 'Finland': 'Finlandiya', 'Turkey': 'Türkiye', 'South Africa': 'Güney Afrika', 'Nigeria': 'Nijerya', 'Kenya': 'Kenya', 'Singapore': 'Singapur', 'Malaysia': 'Malezya', 'Croatia': 'Hırvatistan', 'Slovenia': 'Slovenya', 'Belarus': 'Belarus', 'Moldova': 'Moldova', 'Georgia': 'Gürcistan', 'United Arab Emirates': 'BAE', 'Saudi Arabia': 'Suudi Arabistan', 'Qatar': 'Katar', 'Vietnam': 'Vietnam', 'Thailand': 'Tayland', 'South Korea': 'Güney Kore', 'Taiwan': 'Tayvan', 'Hong Kong': 'Hong Kong', 'New Zealand': 'Yeni Zelanda', 'Colombia': 'Kolombiya', 'Chile': 'Şili', 'Peru': 'Peru', 'Venezuela': 'Venezuela', 'Bosnia-Herzegovina': 'Bosna-Hersek', 'Montenegro': 'Karadağ', 'Cyprus': 'Kıbrıs', 'Luxembourg': 'Lüksemburg', 'Iran': 'İran', 'Bangladesh': 'Bangladeş', 'Sri Lanka': 'Sri Lanka', 'Nepal': 'Nepal', 'Kazakhstan': 'Kazakistan', 'Armenia': 'Ermenistan', 'Azerbaijan': 'Azerbaycan', 'Syria': 'Suriye', 'Cambodia': 'Kamboçya', 'Ghana': 'Gana', 'Ivory Coast': 'Fildişi Sahili'}
fmt = lambda x, n=2: f'{x:.{n}f}'.replace('.', ',')
th = lambda n: f'{n:,}'.replace(',', '.')
rows = ['| Yayın ülkesi | Haber | Yayın kuruluşu | Taranan kayıt | 100.000 kayıt başına (%95 GA) |', '|---|---:|---:|---:|---|']
for x in S['gdelt']['all_countries']:
    rows.append(f"| {TR.get(x['country'], x['country'])} | {x['articles']} | {x['outlets']} | {th(x['scanned'])} | {fmt(x['per100k'])} ({fmt(x['ci95'][0])}–{fmt(x['ci95'][1])}) |")
md = (M / 'makale.md').read_text()
md = re.sub(r'<!-- EK-A -->.*?<!-- /EK-A -->', '<!-- EK-A -->\n' + '\n'.join(rows) + '\n<!-- /EK-A -->', md, flags=re.S)
g = S['gdelt']
t3 = ['| Asgari kayıt (alan adı başına) | Almanya: haberleştiren / aktif | ABD: haberleştiren / aktif | Almanya/ABD oranı (%95 GA) |', '|---:|---:|---:|---|']
for x in g.get('outlet_threshold', []):
    t3.append(f"| {th(x['min_records'])} | {x['germany'][0]} / {th(x['germany'][1])} | {x['united_states'][0]} / {th(x['united_states'][1])} | {fmt(x['ratio_de_us'])} ({fmt(x['ci95'][0])}–{fmt(x['ci95'][1])}) |")
md = re.sub(r'<!-- TABLO-3 -->.*?<!-- /TABLO-3 -->', lambda _: '<!-- TABLO-3 -->\n' + '\n'.join(t3) + '\n<!-- /TABLO-3 -->', md, flags=re.S)
sys.path.insert(0, str(R / 'scripts'))
import gdelt_gkg_archive as gga
pats = [('R1', 'kampanya adı', gga.CAMPAIGN), ('R1, R2, R3', 'Rusya terimi', gga.RUSSIA), ('R2', 'platform', gga.PLATFORM), ('R2', 'ağ / sahte / kaldırma', gga.ACTION),
        ('R3', 'Almanca sahtecilik', gga.FAKE_DE), ('R3', 'yayın / medya', gga.OUTLET_DE), ('Birinci duyarlılık havuzu', 'geniş Almanca terim', gga.BROAD_DE)]
eb = ['Bütün ifadeler büyük-küçük harfe duyarsızdır ve sayfa başlığı ile URL’nin birleştirilmiş metnine uygulanır. R1: kampanya adı ve (Rusya terimi ya da GKG konum alanında Rusya). R2: platform, Rusya terimi ve ağ/sahte/kaldırma terimi birlikte. R3: Almanca sahtecilik, yayın/medya ve Rusya terimi birlikte. Kurallar bu sırayla denenir; bir habere ilk karşıladığı kural atanır. Birinci duyarlılık havuzu, hiçbir kuralı karşılamayan Almanca ya da Almanya kaynaklı kayıtlarda Rusya terimi ile geniş Almanca terimin birlikte geçmesidir.', '']
for rule, name, rx in pats:
    eb += [f'**{rule} — {name}**', '', '```', rx.pattern, '```', '']
md = re.sub(r'<!-- EK-B -->.*?<!-- /EK-B -->', lambda _: '<!-- EK-B -->\n' + '\n'.join(eb) + '\n<!-- /EK-B -->', md, flags=re.S)
(M / 'makale.md').write_text(md)
subprocess.run(['pandoc', 'makale.md', '-o', 'makale.docx', f'--reference-doc={ref.name}', '--resource-path=.'], cwd=M, check=True)
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', 'makale.docx'], cwd=M, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('makale.docx ve makale.pdf üretildi')
