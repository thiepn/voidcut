from pathlib import Path

p = Path(__file__).resolve().parent / 'test-service-worker-navigation-cache-source.mjs'
s = p.read_text(encoding='utf-8')
old = "assert.ok(sw.includes(\"const fallback = await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true });\"), 'offline navigation must retain canonical index fallback');"
new = "assert.ok(sw.includes(\"const fallback = cache ? await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true }) : null;\"), 'offline navigation must retain canonical index fallback even when Cache Storage is unavailable');"
if s.count(old) != 1:
    raise SystemExit(f'F14 fallback assertion: expected 1 match, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
