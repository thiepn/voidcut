from html.parser import HTMLParser
from pathlib import Path
import json, re, struct

required=['index.html','manifest.webmanifest','sw.js','icon.svg','icon-192.png','icon-512.png','icon-maskable-512.png','design/voidcut-design-system.css','design/voidcut-design-system.js','design/VD0_README.md','design/VD1_README.md','design/VD2_README.md','design/VD3_README.md','design/VD4_README.md','design/VD5_README.md','design/VD6_README.md','design/VD7_README.md','design/RELEASE_PWA_README.md','design/RELEASE_PWA_STATUS.md','design/FINAL_RELEASE_RC.md']
missing=[p for p in required if not Path(p).is_file()]
if missing: raise SystemExit('Missing RC asset(s): '+', '.join(missing))

html=Path('index.html').read_text(encoding='utf-8')
css=Path('design/voidcut-design-system.css').read_text(encoding='utf-8')
js=Path('design/voidcut-design-system.js').read_text(encoding='utf-8')
sw=Path('sw.js').read_text(encoding='utf-8')

# Only real line-start Git conflict markers are invalid. Decorative divider
# comments containing long runs of '=' are legitimate in the monolith.
conflict_re=re.compile(r'^(?:<<<<<<<(?: .*)?|=======$|>>>>>>>(?: .*)?)$',re.M)
for path,text in [('index.html',html),('design CSS',css),('design JS',js),('sw.js',sw)]:
    m=conflict_re.search(text)
    if m: raise SystemExit(f'Conflict marker {m.group(0)!r} found in {path}')

for name,expected in {'voidcut-build':'6.0.0','voidcut-release-channel':'stable','voidcut-save-schema':'16','voidcut-replay-version':'8','voidcut-arena-generation':'2','voidcut-director-generation':'6','voidcut-daily-generation':'1','voidcut-visual-phase':'VD7'}.items():
    m=re.search(rf'<meta name="{re.escape(name)}" content="([^"]+)"',html)
    if not m or m.group(1)!=expected: raise SystemExit(f'Metadata contract failed: {name}')

for token in ["const VD1_RENDERER_VERSION='VD1.0.0'","const VD2_HUD_VERSION='VD2.0.0'","const VD3_SHELL_VERSION='VD3.0.0'","const VD4_SECONDARY_VERSION='VD4.0.0'","const VD5_COSMETICS_VERSION='VD5.0.0'","const VD6_SYSTEM_VERSION='VD6.0.0'","const VD7_CERT_VERSION='VD7.0.0'","Object.defineProperty(window,'VoidcutCertification'",'drawCoreLightField(){return}']:
    if token not in html: raise SystemExit('Integrated phase contract missing: '+token)

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.scripts=[]; self._script=False; self._buf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag.lower()=='script' and not a.get('src'): self._script=True; self._buf=[]
    def handle_data(self,data):
        if self._script: self._buf.append(data)
    def handle_endtag(self,tag):
        if tag.lower()=='script' and self._script: self.scripts.append(''.join(self._buf)); self._script=False; self._buf=[]
parser=AuditParser(); parser.feed(html)
dupes=sorted({x for x in parser.ids if parser.ids.count(x)>1})
if dupes: raise SystemExit('Duplicate DOM id(s): '+', '.join(dupes))
if not parser.scripts: raise SystemExit('No inline game script found')
Path('/tmp/voidcut-rc-inline.js').write_text(max(parser.scripts,key=len),encoding='utf-8')

manifest=json.loads(Path('manifest.webmanifest').read_text(encoding='utf-8'))
for k,v in {'name':'VOIDCUT','short_name':'VOIDCUT','id':'./','start_url':'./','scope':'./','display':'standalone','background_color':'#E9E4D8','theme_color':'#E9E4D8'}.items():
    if manifest.get(k)!=v: raise SystemExit(f'Manifest {k}={manifest.get(k)!r}; expected {v!r}')
required_icons={('./icon-192.png','192x192','any'),('./icon-512.png','512x512','any'),('./icon-maskable-512.png','512x512','maskable')}
actual_icons={(x.get('src'),x.get('sizes'),x.get('purpose')) for x in manifest.get('icons',[])}
if not required_icons.issubset(actual_icons): raise SystemExit('Manifest icon set is incomplete')

def png_size(path):
    data=Path(path).read_bytes()
    if data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR': raise SystemExit(path+' is not a PNG')
    return struct.unpack('>II',data[16:24])
for path,size in {'icon-192.png':(192,192),'icon-512.png':(512,512),'icon-maskable-512.png':(512,512)}.items():
    got=png_size(path)
    if got!=size: raise SystemExit(f'{path} has dimensions {got}, expected {size}')

for ref in ['./manifest.webmanifest','./icon.svg','./icon-192.png','./design/voidcut-design-system.css','./design/voidcut-design-system.js']:
    if ref not in html: raise SystemExit('HTML runtime reference missing: '+ref)
if "register('./sw.js',{scope:'./'})" not in html: raise SystemExit('Service-worker registration contract missing')
if "VOIDCUT_CACHE_VERSION = '6.0.0-pwa1'" not in sw: raise SystemExit('Unexpected service-worker cache version')
for token in ["type === 'SKIP_WAITING'",'self.skipWaiting()','self.clients.claim()',"self.addEventListener('install'","self.addEventListener('activate'","self.addEventListener('fetch'"]:
    if token not in sw: raise SystemExit('Service-worker lifecycle contract missing: '+token)
core_match=re.search(r'const VOIDCUT_CORE_PATHS = \[(.*?)\];',sw,re.S)
if not core_match: raise SystemExit('Cannot locate service-worker core asset list')
core_paths=re.findall(r"'([^']+)'",core_match.group(1))
for rel in core_paths:
    if rel=='./': continue
    p=rel[2:] if rel.startswith('./') else rel
    if not Path(p).is_file(): raise SystemExit('Precached asset missing on disk: '+rel)
if 'COMPLETE — PWA RELEASE CERTIFICATION PASS' not in Path('design/RELEASE_PWA_STATUS.md').read_text(encoding='utf-8'): raise SystemExit('PWA certification record is not green')

print('VOIDCUT FINAL RC STATIC CERTIFICATION PASS')
print('Required files:',len(required),'DOM IDs:',len(parser.ids),'SW core assets:',len(core_paths),'Manifest icons:',len(actual_icons))
