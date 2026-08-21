from pathlib import Path

p = Path('design/rc_browser_certify.mjs')
t = p.read_text(encoding='utf-8')
old = "    if (runtime.length) fail(label, runtime.join(' | '));"
new = """    const actionableRuntime = runtime.filter(msg =>
      !(engine === 'Firefox' && msg.includes('interactive-widget') && msg.includes('not recognized and ignored'))
    );
    if (actionableRuntime.length) fail(label, actionableRuntime.join(' | '));"""
if new in t:
    print('Firefox runtime-array compatibility filter already present')
    raise SystemExit(0)
if old not in t:
    raise SystemExit('Expected cross-engine runtime failure gate not found')
t = t.replace(old, new, 1)
p.write_text(t, encoding='utf-8')
print('Applied Firefox runtime-array compatibility filter')
