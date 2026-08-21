from pathlib import Path

p=Path('design/rc_browser_certify.mjs')
t=p.read_text(encoding='utf-8')
old="    if (engine === 'Firefox' && text.includes('Viewport argument key \\\"interactive-widget\\\" not recognized and ignored.')) {"
new="    if (engine === 'Firefox' && text.includes('interactive-widget') && text.includes('not recognized and ignored')) {"
if new in t:
    print('Robust Firefox compatibility filter already present')
    raise SystemExit(0)
if old not in t:
    # Handle the equivalent source spelling if the backslashes were normalized.
    old2="    if (engine === 'Firefox' && text.includes('Viewport argument key \\"interactive-widget\\" not recognized and ignored.')) {"
    if old2 not in t:
        raise SystemExit('Existing Firefox notice condition not found')
    old=old2
t=t.replace(old,new,1)
p.write_text(t,encoding='utf-8')
print('Hardened Firefox interactive-widget compatibility filter')
