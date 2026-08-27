import fs from 'node:fs';
import assert from 'node:assert/strict';

const root = new URL('../../', import.meta.url);
const sw = fs.readFileSync(new URL('sw.js', root), 'utf8');
const html = fs.readFileSync(new URL('index.html', root), 'utf8');

// One canonical release build owns service-worker generation; no independent PWA revision remains.
assert.doesNotMatch(sw, /VOIDCUT_CACHE_VERSION/, 'independent manual service-worker cache revision must be removed');
assert.match(sw, /const VOIDCUT_WORKER_URL = new URL\(self\.location\.href\);/, 'worker must derive generation from its own registered URL');
assert.match(sw, /searchParams\.get\('build'\)/, 'worker must read canonical build from service-worker URL');
assert.match(sw, /\/\^\[0-9A-Za-z\._-\]\{1,64\}\$\//, 'worker build identifier must be validated before becoming a cache name');
assert.match(sw, /const VOIDCUT_CACHE = `\$\{VOIDCUT_CACHE_PREFIX\}\$\{VOIDCUT_BUILD\}`;/, 'cache namespace must be build-derived');

assert.match(html, /const workerUrl=`\.\/sw\.js\?build=\$\{encodeURIComponent\(BUILD_ID\)\}`;/,
  'client must bind service-worker URL to canonical BUILD_ID');
assert.match(html, /navigator\.serviceWorker\.register\(workerUrl,\{scope:'\.\/',updateViaCache:'none'\}\)/,
  'service-worker script updates must bypass the HTTP cache');

// New worker generations must populate from fresh network responses and must not mutate the old generation cache.
assert.match(sw, /const VOIDCUT_CORE_REQUESTS = VOIDCUT_CORE_URLS\.map\(url => new Request\(url, \{ cache: 'reload' \}\)\);/,
  'install core requests must bypass stale HTTP-cache entries');
const installBlock = sw.match(/self\.addEventListener\('install',[\s\S]*?\n\}\);/)?.[0] || '';
assert.ok(installBlock, 'install handler missing');
assert.ok(installBlock.includes('await cache.addAll(VOIDCUT_CORE_REQUESTS);'), 'install must atomically pre-cache the fresh core request set');
assert.doesNotMatch(installBlock, /skipWaiting\s*\(/, 'F16 must preserve F15 waiting lifecycle');

const activateBlock = sw.match(/self\.addEventListener\('activate',[\s\S]*?\n\}\);/)?.[0] || '';
assert.ok(activateBlock, 'activate handler missing');
assert.ok(activateBlock.includes("name.startsWith(VOIDCUT_CACHE_PREFIX) && name !== VOIDCUT_CACHE"), 'activation must purge older build cache generations only');
assert.ok(activateBlock.includes('await self.clients.claim();'), 'activation must preserve client handoff');

// Cache access/write failures are a storage concern, not a successful network-response failure.
const openSource = sw.match(/async function openVoidcutCache\(\) \{[\s\S]*?\n\}/)?.[0];
const putSource = sw.match(/async function cacheVoidcutResponse\(cache, key, response\) \{[\s\S]*?\n\}/)?.[0];
assert.ok(openSource, 'best-effort cache-open helper missing');
assert.ok(putSource, 'best-effort cache-write helper missing');
assert.match(openSource, /catch \(error\) \{[\s\S]*?return null;/, 'cache open failure must be contained');
assert.match(putSource, /try \{[\s\S]*?await cache\.put\(key, response\.clone\(\)\);[\s\S]*?return true;[\s\S]*?catch \(error\) \{[\s\S]*?return false;/,
  'cache put failure must be contained and reported as false');

const helperFactory = new Function(
  'caches',
  'VOIDCUT_CACHE',
  `${openSource}\n${putSource}\nreturn {openVoidcutCache,cacheVoidcutResponse};`,
);
{
  const helpers = helperFactory({ open: async () => { throw new Error('storage-down'); } }, 'voidcut-shell-test');
  assert.equal(await helpers.openVoidcutCache(), null, 'cache open failure must degrade to null');
}
{
  let cloneCount = 0;
  const helpers = helperFactory({ open: async () => null }, 'voidcut-shell-test');
  const cache = { put: async () => { throw new Error('quota'); } };
  const response = { clone: () => { cloneCount++; return { body: 'clone' }; } };
  assert.equal(await helpers.cacheVoidcutResponse(cache, '/asset', response), false, 'cache put rejection must not escape');
  assert.equal(cloneCount, 1, 'cache helper should clone only when attempting persistence');
}
{
  const helpers = helperFactory({ open: async () => null }, 'voidcut-shell-test');
  assert.equal(await helpers.cacheVoidcutResponse(null, '/asset', { clone() {} }), false, 'unavailable cache must fail closed without throwing');
}

// Navigation remains F14 network-first; cache persistence happens only after a successful response exists.
const navBlock = sw.match(/if \(request\.mode === 'navigate'\) \{[\s\S]*?\n  \}\n\n  if \(VOIDCUT_CORE_SET/)?.[0] || '';
assert.ok(navBlock, 'navigation branch missing');
const navFetch = navBlock.indexOf("const response = await fetch(request, { cache: 'no-store' });");
const navOpen = navBlock.indexOf('const cache = await openVoidcutCache();');
assert.ok(navFetch >= 0 && navOpen > navFetch, 'navigation network response must be obtained before cache access can fail');
assert.ok(navBlock.includes('await cacheVoidcutResponse(cache, VOIDCUT_INDEX_URL, response);'), 'navigation shell write must use failure-isolated helper');
assert.doesNotMatch(navBlock, /await cache\.put\(/, 'navigation path must not directly await a fallible cache.put');
assert.ok(navBlock.includes("const fallback = cache ? await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true }) : null;"), 'navigation network failure must retain cached index fallback');

// Core assets revalidate online, cache successful responses best-effort, and fall back offline.
const coreBlock = sw.match(/if \(VOIDCUT_CORE_SET\.has\(url\.href\)\) \{[\s\S]*?\n  \}\n\}\);/)?.[0] || '';
assert.ok(coreBlock, 'core-asset branch missing');
const coreFetch = coreBlock.indexOf("const response = await fetch(request, { cache: 'no-cache' });");
const coreOpen = coreBlock.indexOf('const cache = await openVoidcutCache();');
assert.ok(coreFetch >= 0 && coreOpen > coreFetch, 'core assets must be network-first rather than stale cache-first');
assert.ok(coreBlock.includes('await cacheVoidcutResponse(cache, request, response);'), 'core network response must use best-effort cache persistence');
assert.ok(coreBlock.includes("const cached = cache ? await cache.match(request, { ignoreSearch: true }) : null;"), 'core network failure must retain Cache Storage fallback');
assert.ok(coreBlock.includes('if (cached) return cached;'), 'core cached fallback must be returned when network fails');
assert.doesNotMatch(coreBlock, /const cached = await cache\.match[\s\S]*?if \(cached\) return cached;[\s\S]*?const response = await fetch/,
  'obsolete cache-first core strategy must be absent');
assert.doesNotMatch(coreBlock, /await cache\.put\(/, 'core path must not directly await a fallible cache.put');

console.log('F16 PWA cache freshness and failure-isolation regression PASS');
