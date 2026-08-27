import fs from 'node:fs';
import assert from 'node:assert/strict';

const root = new URL('../../', import.meta.url);
const sw = fs.readFileSync(new URL('sw.js', root), 'utf8');

assert.match(sw, /if \(type === 'SKIP_WAITING'\) \{\s*self\.skipWaiting\(\);\s*\}/, 'F14 must preserve explicit SKIP_WAITING message handling');
assert.ok(sw.includes("const response = await fetch(request, { cache: 'no-store' });"), 'navigation must remain network-first/no-store');
assert.ok(sw.includes("const fallback = cache ? await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true }) : null;"), 'offline navigation must retain canonical index fallback even when Cache Storage is unavailable');

const helperMatch = sw.match(/function isVoidcutShellUrl\(value\) \{[\s\S]*?function shouldCacheVoidcutShellResponse\(requestUrl, response\) \{[\s\S]*?\n\}/);
assert.ok(helperMatch, 'F14 shell cache eligibility helpers are missing');

const helpers = new Function(
  'VOIDCUT_SCOPE',
  'VOIDCUT_ORIGIN',
  'VOIDCUT_ROOT_PATH',
  'VOIDCUT_INDEX_PATH',
  `${helperMatch[0]};return {isVoidcutShellUrl,shouldCacheVoidcutShellResponse};`,
)(
  'https://example.test/voidcut/',
  'https://example.test',
  '/voidcut/',
  '/voidcut/index.html',
);

const response = (url, contentType = 'text/html; charset=utf-8', ok = true) => ({
  url,
  ok,
  headers: { get: name => String(name).toLowerCase() === 'content-type' ? contentType : null },
});

assert.equal(helpers.isVoidcutShellUrl('https://example.test/voidcut/'), true, 'scope root is a shell URL');
assert.equal(helpers.isVoidcutShellUrl('https://example.test/voidcut/index.html'), true, 'canonical index is a shell URL');
assert.equal(helpers.isVoidcutShellUrl('https://example.test/voidcut/?from=pwa'), true, 'root query must not change shell identity');
assert.equal(helpers.isVoidcutShellUrl('https://example.test/voidcut/index.html?x=1#top'), true, 'index query/fragment must not change shell identity');
assert.equal(helpers.isVoidcutShellUrl('https://example.test/voidcut/design/vd0-preview.html'), false, 'same-scope arbitrary HTML is not the app shell');
assert.equal(helpers.isVoidcutShellUrl('https://other.test/voidcut/index.html'), false, 'cross-origin index path is not the app shell');

assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('https://example.test/voidcut/')),
  true,
  'canonical root HTML navigation may refresh the shell',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/index.html?fresh=1', response('https://example.test/voidcut/index.html')),
  true,
  'canonical index HTML navigation may refresh the shell',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/design/vd0-preview.html', response('https://example.test/voidcut/design/vd0-preview.html')),
  false,
  'arbitrary same-scope HTML navigation must never poison canonical index cache',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/manifest.webmanifest', response('https://example.test/voidcut/manifest.webmanifest', 'application/manifest+json')),
  false,
  'manifest navigation must never become the shell',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('https://example.test/voidcut/other.html')),
  false,
  'canonical request redirected to arbitrary final URL must not refresh shell cache',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('https://other.test/voidcut/index.html')),
  false,
  'canonical request redirected cross-origin must not refresh shell cache',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('https://example.test/voidcut/', 'application/json')),
  false,
  'canonical URL returning non-HTML must not replace shell cache',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('https://example.test/voidcut/', 'TEXT/HTML ; charset=UTF-8')),
  true,
  'HTML content type matching should be case-insensitive and tolerate parameters',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('https://example.test/voidcut/', 'text/html', false)),
  false,
  'non-ok response must not replace shell cache',
);
assert.equal(
  helpers.shouldCacheVoidcutShellResponse('https://example.test/voidcut/', response('', 'text/html')),
  false,
  'response without a final URL must fail closed',
);

assert.match(sw, /if \(shouldCacheVoidcutShellResponse\(url, response\)\) \{\s*const cache = await openVoidcutCache\(\);\s*await cacheVoidcutResponse\(cache, VOIDCUT_INDEX_URL, response\);\s*\}/,
  'canonical index cache write must remain guarded by F14 eligibility helper');
assert.doesNotMatch(sw, /if \(response && response\.ok\) \{\s*await cache\.put\(VOIDCUT_INDEX_URL, response\.clone\(\)\);\s*\}/,
  'obsolete unconditional navigation shell cache write must be absent');

const navBlock = sw.match(/if \(request\.mode === 'navigate'\) \{[\s\S]*?\n  \}\n\n  if \(VOIDCUT_CORE_SET/);
assert.ok(navBlock, 'navigation fetch block missing');
assert.equal((navBlock[0].match(/cacheVoidcutResponse\(cache, VOIDCUT_INDEX_URL, response\)/g) || []).length, 1, 'navigation path must have exactly one canonical shell write site');
assert.ok(navBlock[0].includes('shouldCacheVoidcutShellResponse(url, response)'), 'the only navigation shell write must be eligibility-guarded');

console.log('F14 service-worker navigation shell cache isolation PASS');
