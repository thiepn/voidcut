from pathlib import Path

p = Path(__file__).resolve().parent / 'test-service-worker-navigation-cache-source.mjs'
s = p.read_text(encoding='utf-8')

old = """assert.match(sw, /if \\(shouldCacheVoidcutShellResponse\\(url, response\\)\\) \\{\\s*await cache\\.put\\(VOIDCUT_INDEX_URL, response\\.clone\\(\\)\\);\\s*\\}/,
  'canonical index cache write must be guarded by F14 eligibility helper');
assert.doesNotMatch(sw, /if \\(response && response\\.ok\\) \\{\\s*await cache\\.put\\(VOIDCUT_INDEX_URL, response\\.clone\\(\\)\\);\\s*\\}/,
  'obsolete unconditional navigation shell cache write must be absent');

const navBlock = sw.match(/if \\(request\\.mode === 'navigate'\\) \\{[\\s\\S]*?\\n  \\}\\n\\n  if \\(VOIDCUT_CORE_SET/);
assert.ok(navBlock, 'navigation fetch block missing');
assert.equal((navBlock[0].match(/cache\\.put\\(VOIDCUT_INDEX_URL/g) || []).length, 1, 'navigation path must have exactly one canonical shell write site');
assert.ok(navBlock[0].includes('shouldCacheVoidcutShellResponse(url, response)'), 'the only navigation shell write must be eligibility-guarded');
"""
new = """assert.match(sw, /if \\(shouldCacheVoidcutShellResponse\\(url, response\\)\\) \\{\\s*const cache = await openVoidcutCache\\(\\);\\s*await cacheVoidcutResponse\\(cache, VOIDCUT_INDEX_URL, response\\);\\s*\\}/,
  'canonical index cache write must remain guarded by F14 eligibility helper');
assert.doesNotMatch(sw, /if \\(response && response\\.ok\\) \\{\\s*await cache\\.put\\(VOIDCUT_INDEX_URL, response\\.clone\\(\\)\\);\\s*\\}/,
  'obsolete unconditional navigation shell cache write must be absent');

const navBlock = sw.match(/if \\(request\\.mode === 'navigate'\\) \\{[\\s\\S]*?\\n  \\}\\n\\n  if \\(VOIDCUT_CORE_SET/);
assert.ok(navBlock, 'navigation fetch block missing');
assert.equal((navBlock[0].match(/cacheVoidcutResponse\\(cache, VOIDCUT_INDEX_URL, response\\)/g) || []).length, 1, 'navigation path must have exactly one canonical shell write site');
assert.ok(navBlock[0].includes('shouldCacheVoidcutShellResponse(url, response)'), 'the only navigation shell write must be eligibility-guarded');
"""
if s.count(old) != 1:
    raise SystemExit(f'F14 write assertion block: expected 1 match, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
