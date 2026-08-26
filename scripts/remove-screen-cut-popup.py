from pathlib import Path
import re

index = Path('index.html')
s = index.read_text(encoding='utf-8')

dom = '<div id="screenCutFx" class="vc-screen-cut" aria-hidden="true"><span class="cut-pane cut-pane-a"></span><span class="cut-pane cut-pane-b"></span><span class="cut-beam"></span></div>\n'
if s.count(dom) != 1:
    raise SystemExit(f'Expected one screenCutFx DOM node, found {s.count(dom)}')
s = s.replace(dom, '', 1)
s = s.replace('let screenCutTimer=0,rankUpTimer=0;', 'let rankUpTimer=0;', 1)
s = s.replace('function screenCutTransition(){/* intentionally disabled: navigation should not flash a center-screen overlay */}\n', '', 1)
s = re.sub(r"screenCutTransition\('[^']+'\);", '', s)
if 'screenCutFx' in s or 'screenCutTransition(' in s or 'screenCutTimer' in s:
    raise SystemExit('Screen-cut runtime references remain after removal')
index.write_text(s, encoding='utf-8')

sw = Path('sw.js')
w = sw.read_text(encoding='utf-8')
old_version = "const VOIDCUT_CACHE_VERSION = '6.1.0-pwa3';"
if old_version not in w:
    raise SystemExit('Expected pwa3 service-worker cache version')
w = w.replace(old_version, "const VOIDCUT_CACHE_VERSION = '6.1.0-pwa4';", 1)

install_old = "self.addEventListener('install', event => {\n  event.waitUntil((async () => {\n    const cache = await caches.open(VOIDCUT_CACHE);\n    await cache.addAll(VOIDCUT_CORE_URLS);\n  })());\n});"
install_new = "self.addEventListener('install', event => {\n  event.waitUntil((async () => {\n    const cache = await caches.open(VOIDCUT_CACHE);\n    await cache.addAll(VOIDCUT_CORE_URLS);\n    await self.skipWaiting();\n  })());\n});"
if install_old not in w:
    raise SystemExit('Service-worker install anchor missing')
w = w.replace(install_old, install_new, 1)

nav_old = "  if (request.mode === 'navigate') {\n    event.respondWith((async () => {\n      const cache = await caches.open(VOIDCUT_CACHE);\n      const cached = await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true });\n      if (cached) return cached;\n\n      try {\n        const response = await fetch(request);\n        if (response && response.ok) {\n          await cache.put(VOIDCUT_INDEX_URL, response.clone());\n        }\n        return response;\n      } catch (error) {\n        const fallback = await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true });\n        if (fallback) return fallback;\n        throw error;\n      }\n    })());\n    return;\n  }\n"
nav_new = "  if (request.mode === 'navigate') {\n    event.respondWith((async () => {\n      const cache = await caches.open(VOIDCUT_CACHE);\n      try {\n        const response = await fetch(request, { cache: 'no-store' });\n        if (response && response.ok) {\n          await cache.put(VOIDCUT_INDEX_URL, response.clone());\n        }\n        return response;\n      } catch (error) {\n        const fallback = await cache.match(VOIDCUT_INDEX_URL, { ignoreSearch: true });\n        if (fallback) return fallback;\n        throw error;\n      }\n    })());\n    return;\n  }\n"
if nav_old not in w:
    raise SystemExit('Service-worker navigation strategy anchor missing')
w = w.replace(nav_old, nav_new, 1)
sw.write_text(w, encoding='utf-8')
print('Screen-cut popup runtime removed; PWA cache upgraded to pwa4.')
