const VOIDCUT_CACHE_PREFIX = 'voidcut-shell-';
const VOIDCUT_WORKER_URL = new URL(self.location.href);
const VOIDCUT_BUILD_VALUE = String(VOIDCUT_WORKER_URL.searchParams.get('build') || '').trim();
const VOIDCUT_BUILD = /^[0-9A-Za-z._-]{1,64}$/.test(VOIDCUT_BUILD_VALUE) ? VOIDCUT_BUILD_VALUE : 'unversioned';
const VOIDCUT_CACHE = `${VOIDCUT_CACHE_PREFIX}${VOIDCUT_BUILD}`;
const VOIDCUT_SCOPE = self.registration.scope;

const VOIDCUT_CORE_PATHS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.svg',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './design/voidcut-design-system.css',
  './design/voidcut-design-system.js'
];

const VOIDCUT_CORE_URLS = VOIDCUT_CORE_PATHS.map(path => new URL(path, VOIDCUT_SCOPE).href);
const VOIDCUT_CORE_SET = new Set(VOIDCUT_CORE_URLS);
const VOIDCUT_CORE_REQUESTS = VOIDCUT_CORE_URLS.map(url => new Request(url, { cache: 'reload' }));
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

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VOIDCUT_CACHE);
    await cache.addAll(VOIDCUT_CORE_REQUESTS);
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.map(name => {
      if (name.startsWith(VOIDCUT_CACHE_PREFIX) && name !== VOIDCUT_CACHE) {
        return caches.delete(name);
      }
      return Promise.resolve(false);
    }));
    await self.clients.claim();
  })());
});

self.addEventListener('message', event => {
  const type = event.data && event.data.type;
  if (type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== VOIDCUT_ORIGIN) return;

  if (request.mode === 'navigate') {
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

  if (VOIDCUT_CORE_SET.has(url.href)) {
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
});
