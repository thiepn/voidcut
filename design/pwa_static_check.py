from pathlib import Path
import json, re, struct

required = [
    'index.html', 'manifest.webmanifest', 'sw.js', 'icon.svg',
    'icon-192.png', 'icon-512.png', 'icon-maskable-512.png',
    'design/voidcut-design-system.css', 'design/voidcut-design-system.js',
    'design/RELEASE_PWA_README.md'
]
missing = [p for p in required if not Path(p).is_file()]
if missing:
    raise SystemExit('Missing package asset(s): ' + ', '.join(missing))

html = Path('index.html').read_text(encoding='utf-8')
for token in ['./manifest.webmanifest', './icon.svg', './icon-192.png', "register('./sw.js',{scope:'./'})"]:
    if token not in html:
        raise SystemExit('HTML packaging reference missing: ' + token)

manifest = json.loads(Path('manifest.webmanifest').read_text(encoding='utf-8'))
expected = {
    'id': './', 'start_url': './', 'scope': './', 'display': 'standalone',
    'background_color': '#E9E4D8', 'theme_color': '#E9E4D8'
}
for key, value in expected.items():
    if manifest.get(key) != value:
        raise SystemExit(f'Manifest {key}={manifest.get(key)!r}; expected {value!r}')

required_icons = {
    ('./icon-192.png', '192x192', 'any'),
    ('./icon-512.png', '512x512', 'any'),
    ('./icon-maskable-512.png', '512x512', 'maskable')
}
actual_icons = {(x.get('src'), x.get('sizes'), x.get('purpose')) for x in manifest.get('icons', [])}
if not required_icons.issubset(actual_icons):
    raise SystemExit('Manifest icon contract mismatch')

def png_size(path):
    data = Path(path).read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise SystemExit(path + ' is not a valid PNG header')
    return struct.unpack('>II', data[16:24])

for path, expected_size in {
    'icon-192.png': (192, 192),
    'icon-512.png': (512, 512),
    'icon-maskable-512.png': (512, 512)
}.items():
    got = png_size(path)
    if got != expected_size:
        raise SystemExit(f'{path}: {got}, expected {expected_size}')

sw = Path('sw.js').read_text(encoding='utf-8')
for token in [
    "VOIDCUT_CACHE_VERSION = '6.0.0-pwa1'", 'cache.addAll(VOIDCUT_CORE_URLS)',
    "type === 'SKIP_WAITING'", 'self.skipWaiting()', 'self.clients.claim()'
]:
    if token not in sw:
        raise SystemExit('Service-worker contract missing: ' + token)

for name, expected_value in {
    'voidcut-build': '6.0.0', 'voidcut-save-schema': '16', 'voidcut-replay-version': '8',
    'voidcut-arena-generation': '2', 'voidcut-director-generation': '6', 'voidcut-daily-generation': '1'
}.items():
    m = re.search(rf'<meta name="{re.escape(name)}" content="([^"]+)"', html)
    if not m or m.group(1) != expected_value:
        raise SystemExit(f'Release contract changed: {name}')

print('VOIDCUT PWA STATIC CERTIFICATION PASS')
