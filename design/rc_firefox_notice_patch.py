from pathlib import Path

p=Path('design/rc_browser_certify.mjs')
t=p.read_text(encoding='utf-8')
old="  page.on('console', m => { if (m.type() === 'error') runtime.push(`console ${m.text()}`); });"
new="""  page.on('console', m => {\n    if (m.type() !== 'error') return;\n    const text = m.text();\n    if (engine === 'Firefox' && text.includes('Viewport argument key \\\"interactive-widget\\\" not recognized and ignored.')) {\n      results.push(`${engine} ${label} compatibility notice: interactive-widget ignored`);\n      return;\n    }\n    runtime.push(`console ${text}`);\n  });"""
if new in t:
    print('Firefox viewport compatibility filter already present')
    raise SystemExit(0)
if old not in t:
    raise SystemExit('Expected cross-engine console handler not found')
t=t.replace(old,new,1)
p.write_text(t,encoding='utf-8')
print('Applied exact Firefox interactive-widget compatibility notice filter')
