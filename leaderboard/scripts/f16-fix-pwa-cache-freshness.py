from pathlib import Path

root = Path(__file__).resolve().parents[2]
sw_path = root / 'sw.js'
index_path = root / 'index.html'
f14_path = root / 'leaderboard' / 'scripts' / 'test-service-worker-navigation-cache-source.mjs'
f15_path = root / 'leaderboard' / 'scripts' / 'test-pwa-update-lifecycle-source.mjs'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

# Service worker: bind Cache Storage generation to the canonical app build,
# force fresh install fetches, use network-first core assets, and make runtime
# cache persistence best-effort.
sw = sw_path.read_text(encoding='utf-8')
old_header = """const VOIDCUT_CACHE_PREFIX = 'voidcut-shell-';
const VOIDCUT_CACHE_VERSION = '6.1.0-pwa4';
const VOIDCUT_CACHE = `${VOIDCUT_CACHE_PREFIX}${VOIDCUT_CACHE_VERSION}`;
const VOIDCUT_SCOPE = self.registration.scope;
"""
new_header = """const VOIDCUT_CACHE_PREFIX = 'voidcut-shell-';
const VOIDCUT_WORKER_URL = new URL(self.location.href);
const VOIDCUT_BUILD_VALUE = String(VOIDCUT_WORKER_URL.searchParams.get('build') || '').trim();
const VOIDCUT_BUILD = /^[0-9A-Za-z._-]{1,64}$/.test(VOIDCUT_BUILD_VALUE) ? VOIDCUT_BUILD_VALUE : 'unversioned';
const VOIDCUT_CACHE = `${VOIDCUT_CACHE_PREFIX}${VOIDCUT_BUILD}`;
const VOIDCUT_SCOPE = self.registration.scope;
"""
sw = replace_once(sw, old_header, new_header, 'build-derived cache namespace')

old_urls = """const VOIDCUT_CORE_URLS = VOIDCUT_CORE_PATHS.map(path => new URL(path, VOIDCUT_SCOPE).href);
const VOIDCUT_CORE_SET = new Set(VOIDCUT_CORE_URLS);
"""
new_urls = """const VOIDCUT_CORE_URLS = VOIDCUT_CORE_PATHS.map(path => new URL(path, VOIDCUT_SCOPE).href);
const VOIDCUT_CORE_SET = new Set(VOIDCUT_CORE_URLS);
const VOIDCUT_CORE_REQUESTS = VOIDCUT_CORE_URLS.map(url => new Request(url, { cache: 'reload' }));
"""
sw = replace_once(sw, old_urls, new_urls, 'fresh install request set')

anchor = """function shouldCacheVoidcutShellResponse(requestUrl, response) {
  if (!isVoidcutShellUrl(requestUrl) || !response || !response.ok || !response.url || !isVoidcutShellUrl(response.url)) {
    return false;
  }
  const contentType = String(response.headers?.get?.('Content-Type') || '').trim();
  return /^text\\/html(?:\\s*;|$)/i.test(contentType);
}
"""
helpers = anchor + """
async function openVoidcutCache() {
  try {
    return await caches.open(VOIDCUT_CACHE);
  } catch (error) {
    console.warn('VOIDCUT cache unavailable', error);
    return null;
  }
}

async function cacheVoidcutResponse(cache, key, response) {
  if (!cache || !response) return false;
  try {
    await cache.put(key, response.clone());
    return true;
  } catch (error) {
    console.warn('VOIDCUT cache write failed', error);
    return false;
  }
}
"""
sw = replace_once(sw, anchor, helpers, 'best-effort cache helpers')

old_install = """self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VOIDCUT_CACHE);
    await cache.addAll(VOIDCUT_CORE_URLS);
  })());
});
"""
new_install = """self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VOIDCUT_CACHE);
    await cache.addAll(VOIDCUT_CORE_REQUESTS);
  })());
});
"""
sw = replace_once(sw, old_install, new_install, 'fresh install precache')

old_nav = """  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      const cache = await caches.open(VOIDCUT_CACHE);
      try {
        const response = await fetch(request, { cache: 'no-store' });
        if (shouldCacheVoidcutShellResponse(url, response)) {
          await cache.put(VOIDCUT_INDEX_URL, response.clone());
        }
        return response;
      } catch (error) {
        const fallback = await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true });
        if (fallback) return fallback;
        throw error;
      }
    })());
    return;
  }
"""
new_nav = """  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const response = await fetch(request, { cache: 'no-store' });
        if (shouldCacheVoidcutShellResponse(url, response)) {
          const cache = await openVoidcutCache();
          await cacheVoidcutResponse(cache, VOIDCUT_INDEX_URL, response);
        }
        return response;
      } catch (error) {
        const cache = await openVoidcutCache();
        const fallback = cache ? await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true }) : null;
        if (fallback) return fallback;
        throw error;
      }
    })());
    return;
  }
"""
sw = replace_once(sw, old_nav, new_nav, 'navigation best-effort cache write')

old_core = """  if (VOIDCUT_CORE_SET.has(url.href)) {
    event.respondWith((async () => {
      const cache = await caches.open(VOIDCUT_CACHE);
      const cached = await cache.match(request, { ignoreSearch: true });
      if (cached) return cached;
      const response = await fetch(request);
      if (response && response.ok) await cache.put(request, response.clone());
      return response;
    })());
  }
"""
new_core = """  if (VOIDCUT_CORE_SET.has(url.href)) {
    event.respondWith((async () => {
      try {
        const response = await fetch(request, { cache: 'no-cache' });
        if (response && response.ok) {
          const cache = await openVoidcutCache();
          await cacheVoidcutResponse(cache, request, response);
        }
        return response;
      } catch (error) {
        const cache = await openVoidcutCache();
        const cached = cache ? await cache.match(request, { ignoreSearch: true }) : null;
        if (cached) return cached;
        throw error;
      }
    })());
  }
"""
sw = replace_once(sw, old_core, new_core, 'network-first core asset strategy')
sw_path.write_text(sw, encoding='utf-8')

# Client registration: BUILD_ID is already the canonical release identity, so
# use it for the worker script URL and bypass HTTP cache for worker updates.
html = index_path.read_text(encoding='utf-8')
old_reg = """if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol))window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js',{scope:'./'}).then(reg=>{watchRegistration(reg);reg.update().catch(()=>{})}).catch(()=>{}));"""
new_reg = """if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol))window.addEventListener('load',()=>{const workerUrl=`./sw.js?build=${encodeURIComponent(BUILD_ID)}`;navigator.serviceWorker.register(workerUrl,{scope:'./',updateViaCache:'none'}).then(reg=>{watchRegistration(reg);reg.update().catch(()=>{})}).catch(()=>{})});"""
html = replace_once(html, old_reg, new_reg, 'build-bound worker registration')
index_path.write_text(html, encoding='utf-8')

# F14/F15 no longer own the obsolete independent cache-revision boundary.
f14 = f14_path.read_text(encoding='utf-8')
f14 = replace_once(
    f14,
    "assert.ok(sw.includes(\"const VOIDCUT_CACHE_VERSION = '6.1.0-pwa4';\"), 'F14 must not change the F16 cache revision contract');\n",
    '',
    'F14 obsolete F16 revision assertion',
)
f14_path.write_text(f14, encoding='utf-8')

f15 = f15_path.read_text(encoding='utf-8')
f15 = replace_once(
    f15,
    "assert.ok(sw.includes(\"const VOIDCUT_CACHE_VERSION = '6.1.0-pwa4';\"), 'F15 must not change F16 cache revision');\n\n",
    '',
    'F15 obsolete F16 revision assertion',
)
old_registration_assert = """assert.match(html, /navigator\\.serviceWorker\\.register\\('\\.\\/sw\\.js',\\{scope:'\\.\\/'\\}\\)\\.then\\(reg=>\\{watchRegistration\\(reg\\);reg\\.update\\(\\)\\.catch\\(\\(\\)=>\\{\\}\\)\\}\\)/,
  'registration must continue to watch lifecycle and proactively check for updates');
"""
new_registration_assert = """assert.match(html, /navigator\\.serviceWorker\\.register\\(workerUrl,\\{scope:'\\.\\/',updateViaCache:'none'\\}\\)\\.then\\(reg=>\\{watchRegistration\\(reg\\);reg\\.update\\(\\)\\.catch\\(\\(\\)=>\\{\\}\\)\\}\\)/,
  'registration must continue to watch lifecycle and proactively check for updates');
"""
f15 = replace_once(f15, old_registration_assert, new_registration_assert, 'F15 registration assertion')
f15_path.write_text(f15, encoding='utf-8')

# Defect register.
reg = register_path.read_text(encoding='utf-8')
row18 = '| VC-018 | MEDIUM | Cache freshness for core design assets relies on manually changing the SW cache revision; mixed old/new assets are possible after an incomplete release update. | F16 | OPEN |'
row19 = '| VC-019 | MEDIUM | Cache-write failures can interfere with otherwise successful network responses instead of degrading gracefully. | F16 | OPEN |'
reg = replace_once(reg, row18, row18.replace('OPEN', 'FIXED — VERIFYING'), 'VC-018 register row')
reg = replace_once(reg, row19, row19.replace('OPEN', 'FIXED — VERIFYING'), 'VC-019 register row')
reg += '''\n## F16 implementation record — build-bound PWA caching and failure isolation\n\n- The independent manually maintained `VOIDCUT_CACHE_VERSION` has been removed. The worker cache namespace is derived from the canonical application `BUILD_ID` carried in the registered service-worker URL (`sw.js?build=...`).\n- Registration uses the existing trusted local `BUILD_ID` and `updateViaCache: 'none'`; changing the canonical release build therefore changes the worker script URL/cache generation without a second PWA revision that can be forgotten.\n- The worker validates the build query value before using it in a Cache Storage name and falls back to `unversioned` for malformed/manual registrations.\n- Install precaching uses `Request(..., {cache:'reload'})` for every core URL, bypassing a stale HTTP-cache hit while building a new generation. Build-specific cache names prevent a waiting F15 update from mutating the cache used by the currently active worker.\n- Core non-navigation assets are now network-first with `cache:'no-cache'` and Cache Storage fallback on network failure. Online clients therefore revalidate core design assets instead of remaining indefinitely cache-first until a manual SW revision bump.\n- Navigation remains F14 network-first/no-store and retains only the canonical-index offline fallback.\n- Runtime Cache Storage open/write failures are isolated: a successful network navigation/core response is returned even if Cache Storage is unavailable, quota-limited, or `cache.put()` rejects. Cache writes are best-effort and emit a warning rather than becoming response failures.\n- Install-time precache failure remains strict, because activating a newly installed offline-capable worker without a complete initial core bundle would be less safe than failing that installation.\n- F15 manual waiting/activation behavior remains intact; no install-time `skipWaiting()` was reintroduced.\n- No gameplay, balance, leaderboard, replay, save-schema, scoring, UI or visual-design behavior changed in F16.\n'''
register_path.write_text(reg, encoding='utf-8')
