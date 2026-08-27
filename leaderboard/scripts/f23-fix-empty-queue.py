from pathlib import Path

spec = Path('tests/pwa-destructive.spec.mjs')
s = spec.read_text(encoding='utf-8')
replacements = [
    (
        "    const backup = parse(localStorage.getItem(backupKey));\n    const unwrapIdentity = value => value?.d || value || null;",
        "    const backup = parse(localStorage.getItem(backupKey));\n    const queue = parse(localStorage.getItem(queueKey));\n    const unwrapIdentity = value => value?.d || value || null;",
    ),
    (
        "      queuePresent: localStorage.getItem(queueKey) != null,",
        "      queue: Array.isArray(queue) ? queue : [],",
    ),
    (
        "  expect(after.queuePresent).toBe(false);",
        "  expect(after.queue).toEqual([]);",
    ),
]
for old, new in replacements:
    if s.count(old) != 1:
        raise SystemExit(f'spec patch expected one match for {old!r}, found {s.count(old)}')
    s = s.replace(old, new, 1)
spec.write_text(s, encoding='utf-8')

contract = Path('leaderboard/scripts/test-destructive-pwa-suite-source.mjs')
c = contract.read_text(encoding='utf-8')
old = '  "expect(after.backupIdentity).toBeNull();",\n])'
new = '  "expect(after.backupIdentity).toBeNull();",\n  "expect(after.queue).toEqual([]);",\n])'
if c.count(old) != 1:
    raise SystemExit(f'contract patch expected one match, found {c.count(old)}')
c = c.replace(old, new, 1)
contract.write_text(c, encoding='utf-8')
