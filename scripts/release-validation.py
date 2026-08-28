from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
html = (root / 'index.html').read_text(encoding='utf-8')
sw = (root / 'sw.js').read_text(encoding='utf-8')
worker = (root / 'leaderboard/src/index.js').read_text(encoding='utf-8')
manifest = json.loads((root / 'manifest.webmanifest').read_text(encoding='utf-8'))

errors = []
def require(cond, message):
    if not cond:
        errors.append(message)

# Release identity / contracts.
require('voidcut-build" content="6.1.1' in html, 'frontend build metadata must be 6.1.1')
require("const RELEASE_VERSION='6.1.1'" in html, 'runtime release version must be 6.1.1')
require("const SAVE_SCHEMA=17" in html, 'save schema must remain 17')
require("replay:9" in html, 'frontend replay contract must remain 9')
require("const RULESET = Object.freeze({ build: '6.1.1', replay: 9, arena: 2, director: 6 })" in worker, 'leaderboard ruleset must match frontend')
require("const VOIDCUT_CACHE_VERSION = '6.1.1-pwa1'" in sw, 'service-worker cache must match release patch')

# Player-facing regression closures.
require(' COMBO`' not in html and ' COMBO' not in html, 'misleading COMBO label remains')
require('CUT STREAK' in html, 'cut streak label missing')
require('Math.min(100,Math.round(sim.removed/sim.area*100))' in html, 'wordmark FIELD value must use actual removed area')
require("{points:265,title:'VOIDMASTER'" in html, 'VOIDMASTER threshold must be 265')
require('LONGEST RUN</div><div id="recordLongest"' not in html, 'LONGEST RUN must not remain a headline record')
require('LARGEST CUT</div><div id="recordLongest"' in html, 'headline replacement for longest run missing')
require('prefers-reduced-motion: reduce' in html and 'function motionReduced(){return !!save.settings.reducedMotion||!!systemReducedMotion()}' in html, 'canvas reduced-motion bridge missing')
require("showLeaderboardJoin(message='Name this profile once to publish your verified score.'){const card=leaderboardJoinCard();card.classList.remove('hidden');$('leaderboardJoinStatus').textContent=message}" in html, 'leaderboard join flow should not autofocus')
require('setTimeout(()=>$(' not in html or "leaderboardNameInput')?.focus" not in html, 'leaderboard name autofocus remains')
require("text:'RANKED RUN" in html and "text:'LOCAL RUN" in html, 'ranked/local in-run status missing')
require('voidcut.leaderboard.pending.v1' in html, 'durable pending leaderboard submission key missing')
require('leaderboardStorageWritable' in html, 'leaderboard identity storage preflight missing')
require('SELECT A RUN TO WATCH' in html, 'leaderboard replay affordance missing')
require('ADVANCED DIAGNOSTICS' in html, 'player-facing diagnostics demotion missing')
require('>6.0.0<' not in html, 'stale 6.0.0 diagnostics label remains')
require('>16<' not in re.sub(r'<script[\s\S]*?</script>', '', html), 'stale visible save-16 contract remains')
require('#menu.has-health-warning .health-note' in html, 'critical health-warning responsive override missing')

# PWA: explicit update-ready model. install must not activate immediately.
install_match = re.search(r"self\.addEventListener\('install',[\s\S]*?\n\}\);", sw)
require(bool(install_match), 'service-worker install handler missing')
if install_match:
    require('skipWaiting' not in install_match.group(0), 'install handler must not call skipWaiting')
require("if (type === 'SKIP_WAITING')" in sw and 'self.skipWaiting()' in sw, 'explicit SKIP_WAITING message path missing')

# Global leaderboard correctness.
require("/^[a-f0-9]{64}$/i.test(hash)" in worker or "/^[a-f0-9]{64}$/.test(hash)" in worker, 'replay hash validation must accept lowercase SHA-256')
require("toString(16).padStart(2, '0')" in worker, 'server SHA-256 format unexpectedly changed')

# Manifest / shell assets.
require(manifest.get('name') == 'VOIDCUT', 'manifest name must remain VOIDCUT')
for p in ['index.html','sw.js','manifest.webmanifest','icon.svg','icon-192.png','icon-512.png','icon-maskable-512.png','design/voidcut-design-system.css','design/voidcut-design-system.js']:
    require((root / p).exists(), f'missing release asset: {p}')

if errors:
    print('VOIDCUT RELEASE VALIDATION FAILED')
    for e in errors:
        print(f'- {e}')
    raise SystemExit(1)

print('VOIDCUT RELEASE VALIDATION PASS')
print('build=6.1.1 save=17 replay=9 arena=2 director=6')
