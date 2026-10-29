"""Build the native editable deck and refresh established download filenames."""
from pathlib import Path
import runpy,shutil
R=Path(__file__).resolve().parents[1];O=R/'output'
runpy.run_path(str(R/'scripts/export_concise_deck.py'),run_name='__main__')
for ext in ['pptx','pdf']:
 for name in ['PROFESYONEL_SUNUM','ATLAS_SUNUMU','SINEMATIK_SUNUM','SUNUM_15dk']:
  shutil.copyfile(O/f'AKADEMIK_ODAKLI_SUNUM.{ext}',O/f'{name}.{ext}')
shutil.copyfile(O/'AKADEMIK_ODAKLI_SUNUM.pptx',O/'AKADEMIK_SUNUM_DUZENLENEBILIR.pptx')
