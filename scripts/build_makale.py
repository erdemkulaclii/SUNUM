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
subprocess.run(['pandoc', 'makale.md', '-o', 'makale.docx', f'--reference-doc={ref.name}', '--resource-path=.'], cwd=M, check=True)
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', 'makale.docx'], cwd=M, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('makale.docx ve makale.pdf üretildi')
