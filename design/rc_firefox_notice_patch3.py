from pathlib import Path

p=Path('design/rc_browser_certify.mjs')
t=p.read_text(encoding='utf-8')
lines=t.splitlines()
replacement="    if (engine === 'Firefox' && text.includes('interactive-widget') && text.includes('not recognized and ignored')) {"
matched=0
for i,line in enumerate(lines):
    if "engine === 'Firefox'" in line and 'text.includes(' in line:
        lines[i]=replacement
        matched+=1
if matched!=1:
    raise SystemExit(f'Expected exactly one Firefox compatibility condition; found {matched}')
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Applied robust Firefox interactive-widget compatibility condition')
