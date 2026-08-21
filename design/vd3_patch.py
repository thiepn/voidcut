from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

if 'name="voidcut-visual-phase" content="VD3"' not in text:
    raise SystemExit('VD3 product shell baseline is missing')

runpy.run_path(str(ROOT / 'design' / 'vd3_review_patch.py'), run_name='__main__')
