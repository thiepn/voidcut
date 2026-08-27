from pathlib import Path

root = Path(__file__).resolve().parents[2]
sw = root / 'sw.js'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

s = sw.read_text(encoding='utf-8')
old_urls = """const VOIDCUT_CORE_URLS = VOIDCUT_CORE_PATHS.map(path => new URL(path, VOIDCUT_SCOPE).href);
const VOIDCUT_CORE_SET = new Set(VOIDCUT_CORE_URLS);
const VOIDCUT_INDEX_URL = new URL('./index.html', VOIDCUT_SCOPE).href;
"""
new_urls = """const VOIDCUT_CORE_URLS = VOIDCUT_CORE_PATHS.map(path => new URL(path, VOIDCUT_SCOPE).href);
const VOIDCUT_CORE_SET = new Set(VOIDCUT_CORE_URLS);
const VOIDCUT_SCOPE_URL = new URL(VOIDCUT_SCOPE);
const VOIDCUT_ORIGIN = VOIDCUT_SCOPE_URL.origin;
const VOIDCUT_ROOT_PATH = VOIDCUT_SCOPE_URL.pathname;
const VOIDCUT_INDEX_URL = new URL('./index.html', VOIDCUT_SCOPE).href;
const VOIDCUT_INDEX_PATH = new URL(VOIDCUT_INDEX_URL).pathname;

function isVoidcutShellUrl(value) {
  const candidate = value instanceof URL ? value : new URL(value, VOIDCUT_SCOPE);
  return candidate.origin === VOIDCUT_ORIGIN &&
    (candidate.pathname === VOIDCUT_ROOT_PATH || candidate.pathname === VOIDCUT_INDEX_PATH);
}

function shouldCacheVoidcutShellResponse(requestUrl, response) {
  if (!isVoidcutShellUrl(requestUrl) || !response || !response.ok || !response.url || !isVoidcutShellUrl(response.url)) {
    return false;
  }
  const contentType = String(response.headers?.get?.('Content-Type') || '').trim();
  return /^text\/html(?:\s*;|$)/i.test(contentType);
}
"""
s = replace_once(s, old_urls, new_urls, 'shell identity helpers')
s = replace_once(s, "if (url.origin !== self.location.origin) return;", "if (url.origin !== VOIDCUT_ORIGIN) return;", 'canonical origin check')
old_write = """        if (response && response.ok) {
          await cache.put(VOIDCUT_INDEX_URL, response.clone());
        }
"""
new_write = """        if (shouldCacheVoidcutShellResponse(url, response)) {
          await cache.put(VOIDCUT_INDEX_URL, response.clone());
        }
"""
s = replace_once(s, old_write, new_write, 'guard navigation shell cache write')
sw.write_text(s, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_row = '| VC-016 | HIGH | Service worker can cache an arbitrary successful same-scope navigation response under the canonical `index.html` shell key. | F14 | OPEN |'
new_row = '| VC-016 | HIGH | Service worker can cache an arbitrary successful same-scope navigation response under the canonical `index.html` shell key. | F14 | FIXED — VERIFYING |'
r = replace_once(r, old_row, new_row, 'VC-016 register row')
r += '''\n## F14 implementation record — navigation shell cache isolation\n\n- Successful same-origin navigations no longer automatically overwrite the canonical cached `index.html`.\n- Only navigation requests whose pathname is the service-worker scope root or canonical `index.html` may refresh the shell cache. Query strings do not change shell identity.\n- A candidate response must be successful, expose a final response URL that is still a canonical shell URL, and carry a `text/html` content type before it can be written under `VOIDCUT_INDEX_URL`.\n- Same-scope navigations to design previews, manifests, assets or arbitrary pages are returned normally from the network but cannot poison the app-shell cache.\n- Redirected shell requests whose final response resolves outside the root/index shell pair cannot replace the cached shell. Non-HTML and failed responses cannot replace it either.\n- Network-first navigation and the existing offline canonical-index fallback are preserved.\n- F15 update-lifecycle behavior is intentionally unchanged: install-time `skipWaiting()` and the `SKIP_WAITING` message path remain present.\n- F16 cache revision and core-asset freshness/write behavior are intentionally unchanged; the cache revision remains `6.1.0-pwa4`.\n- No client/game, backend, save, replay, ranking, ticket, scoring or UI behavior changed in F14.\n'''
register.write_text(r, encoding='utf-8')
