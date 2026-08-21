const VOIDCUT_CACHE_PREFIX = 'voidcut-shell-';
const VOIDCUT_CACHE_VERSION = '6.0.0-pwa2';
const VOIDCUT_CACHE = `${VOIDCUT_CACHE_PREFIX}${VOIDCUT_CACHE_VERSION}`;
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
const VOIDCUT_INDEX_URL = new URL('./index.html', VOIDCUT_SCOPE).href;

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VOIDCUT_CACHE);
    await cache.addAll(VOIDCUT_CORE_URLS);
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
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      const cache = await caches.open(VOIDCUT_CACHE);
      const cached = await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true });
      if (cached) return cached;

      try {
        const response = await fetch(request);
        if (response && response.ok) {
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

  if (VOIDCUT_CORE_SET.has(url.href)) {
    event.respondWith((async () => {
      const cache = await caches.open(VOIDCUT_CACHE);
      const cached = await cache.match(request, { ignoreSearch: true });
      if (cached) return cached;
      const response = await fetch(request);
      if (response && response.ok) await cache.put(request, response.clone());
      return response;
    })());
  }
});
