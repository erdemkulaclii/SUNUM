"""Build the current academic HTML, editable PowerPoint, PDF and speaker files."""
from pathlib import Path
import runpy
SCRIPTS=Path(__file__).resolve().parent
for name in ['build_concise_presentation.py','export_editorial.py','export_academic_documents.py']:
 runpy.run_path(str(SCRIPTS/name),run_name='__main__')
