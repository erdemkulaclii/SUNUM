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
import json, re
S = json.loads((R / 'output/MAKALE_SAYILARI.json').read_text())
TR = {'United States': 'ABD', 'Germany': 'Almanya', 'Italy': 'İtalya', 'India': 'Hindistan', 'China': 'Çin', 'Russia': 'Rusya', 'United Kingdom': 'Birleşik Krallık', 'Canada': 'Kanada', 'Bulgaria': 'Bulgaristan', 'Romania': 'Romanya', 'France': 'Fransa', 'Brazil': 'Brezilya', 'Slovak Republic': 'Slovakya', 'Portugal': 'Portekiz', 'Austria': 'Avusturya', 'Albania': 'Arnavutluk', 'Spain': 'İspanya', 'Poland': 'Polonya', 'Switzerland': 'İsviçre', 'Ukraine': 'Ukrayna', 'Czech Republic': 'Çekya', 'Netherlands': 'Hollanda', 'Belgium': 'Belçika', 'Norway': 'Norveç', 'Australia': 'Avustralya', 'Japan': 'Japonya', 'Pakistan': 'Pakistan', 'Indonesia': 'Endonezya', 'Philippines': 'Filipinler', 'Hungary': 'Macaristan', 'Greece': 'Yunanistan', 'Mexico': 'Meksika', 'Argentina': 'Arjantin', 'Ireland': 'İrlanda', 'Israel': 'İsrail', 'Egypt': 'Mısır', 'Kosovo': 'Kosova', 'Macedonia': 'Kuzey Makedonya', 'Serbia': 'Sırbistan', 'Lithuania': 'Litvanya', 'Latvia': 'Letonya', 'Estonia': 'Estonya', 'Sweden': 'İsveç', 'Denmark': 'Danimarka', 'Finland': 'Finlandiya', 'Turkey': 'Türkiye', 'South Africa': 'Güney Afrika', 'Nigeria': 'Nijerya', 'Kenya': 'Kenya', 'Singapore': 'Singapur', 'Malaysia': 'Malezya', 'Croatia': 'Hırvatistan', 'Slovenia': 'Slovenya', 'Belarus': 'Belarus', 'Moldova': 'Moldova', 'Georgia': 'Gürcistan', 'United Arab Emirates': 'BAE', 'Saudi Arabia': 'Suudi Arabistan', 'Qatar': 'Katar', 'Vietnam': 'Vietnam', 'Thailand': 'Tayland', 'South Korea': 'Güney Kore', 'Taiwan': 'Tayvan', 'Hong Kong': 'Hong Kong', 'New Zealand': 'Yeni Zelanda', 'Colombia': 'Kolombiya', 'Chile': 'Şili', 'Peru': 'Peru', 'Venezuela': 'Venezuela', 'Bosnia-Herzegovina': 'Bosna-Hersek', 'Montenegro': 'Karadağ', 'Cyprus': 'Kıbrıs', 'Luxembourg': 'Lüksemburg', 'Iran': 'İran', 'Bangladesh': 'Bangladeş', 'Sri Lanka': 'Sri Lanka', 'Nepal': 'Nepal', 'Kazakhstan': 'Kazakistan', 'Armenia': 'Ermenistan', 'Azerbaijan': 'Azerbaycan', 'Syria': 'Suriye', 'Cambodia': 'Kamboçya', 'Ghana': 'Gana', 'Ivory Coast': 'Fildişi Sahili'}
fmt = lambda x, n=2: f'{x:.{n}f}'.replace('.', ',')
th = lambda n: f'{n:,}'.replace(',', '.')
rows = ['| Yayın ülkesi | Haber | Yayın kuruluşu | Taranan kayıt | 100.000 kayıt başına (%95 GA) |', '|---|---:|---:|---:|---|']
for x in S['gdelt']['all_countries']:
    rows.append(f"| {TR.get(x['country'], x['country'])} | {x['articles']} | {x['outlets']} | {th(x['scanned'])} | {fmt(x['per100k'])} ({fmt(x['ci95'][0])}–{fmt(x['ci95'][1])}) |")
md = (M / 'makale.md').read_text()
md = re.sub(r'<!-- EK-A -->.*?<!-- /EK-A -->', '<!-- EK-A -->\n' + '\n'.join(rows) + '\n<!-- /EK-A -->', md, flags=re.S)
(M / 'makale.md').write_text(md)
subprocess.run(['pandoc', 'makale.md', '-o', 'makale.docx', f'--reference-doc={ref.name}', '--resource-path=.'], cwd=M, check=True)
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', 'makale.docx'], cwd=M, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('makale.docx ve makale.pdf üretildi')
