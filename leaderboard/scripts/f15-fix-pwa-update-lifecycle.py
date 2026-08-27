from pathlib import Path

root = Path(__file__).resolve().parents[2]
sw_path = root / 'sw.js'
index_path = root / 'index.html'
f14_test_path = root / 'leaderboard' / 'scripts' / 'test-service-worker-navigation-cache-source.mjs'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

# Service worker: updated workers must be allowed to enter waiting state.
sw = sw_path.read_text(encoding='utf-8')
old_install = """self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VOIDCUT_CACHE);
    await cache.addAll(VOIDCUT_CORE_URLS);
    await self.skipWaiting();
  })());
});
"""
new_install = """self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(VOIDCUT_CACHE);
    await cache.addAll(VOIDCUT_CORE_URLS);
  })());
});
"""
sw = replace_once(sw, old_install, new_install, 'install-time skipWaiting removal')
sw_path.write_text(sw, encoding='utf-8')

# Client: derive update-ready state from the actual waiting worker and activate only after durable save.
html = index_path.read_text(encoding='utf-8')
old_client = """let deferredInstall=null,swRegistration=null,updateReady=false,updateApplying=false;const installBtn=$('installApp'),updateBtn=$('updateApp');
function refreshInstall(){installBtn.classList.toggle('hidden',standaloneDisplay()||!deferredInstall)}
function refreshUpdate(){updateBtn.classList.toggle('hidden',!updateReady||updateApplying||state!=='menu');updateBtn.textContent=updateApplying?'UPDATING…':'UPDATE READY'}
function watchRegistration(reg){swRegistration=reg;const inspect=()=>{updateReady=!!reg.waiting;refreshUpdate()};if(reg.waiting)inspect();reg.addEventListener('updatefound',()=>{const w=reg.installing;if(!w)return;w.addEventListener('statechange',()=>{if(w.state==='installed'&&navigator.serviceWorker.controller){updateReady=true;refreshUpdate()}})});navigator.serviceWorker.addEventListener('controllerchange',()=>{if(updateApplying)location.reload()});inspect()}
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredInstall=e;refreshInstall()});
window.addEventListener('appinstalled',()=>{deferredInstall=null;refreshInstall()});
installBtn.onclick=async()=>{if(!deferredInstall)return;const p=deferredInstall;deferredInstall=null;refreshInstall();try{await p.prompt();await p.userChoice}catch{}};
updateBtn.onclick=()=>{if(!swRegistration?.waiting)return;updateApplying=true;refreshUpdate();if(!persist()){updateApplying=false;refreshUpdate();showCoach('SAVE FAILED','Update was not applied.','Free browser storage or export a backup, then retry.',1800);return}swRegistration.waiting.postMessage({type:'SKIP_WAITING'})};
"""
new_client = """let deferredInstall=null,swRegistration=null,updateReady=false,updateApplying=false;const installBtn=$('installApp'),updateBtn=$('updateApp');
function refreshInstall(){installBtn.classList.toggle('hidden',standaloneDisplay()||!deferredInstall)}
function refreshUpdate(){updateBtn.classList.toggle('hidden',!updateReady||updateApplying||state!=='menu');updateBtn.textContent=updateApplying?'UPDATING…':'UPDATE READY'}
function syncWaitingUpdate(reg=swRegistration){updateReady=!!reg?.waiting;refreshUpdate();return updateReady}
function trackInstallingWorker(reg,worker){if(!worker)return;const inspect=()=>{if(worker.state==='installed'||worker.state==='redundant')setTimeout(()=>syncWaitingUpdate(reg),0)};worker.addEventListener('statechange',inspect);inspect()}
function watchRegistration(reg){swRegistration=reg;if(reg.installing)trackInstallingWorker(reg,reg.installing);reg.addEventListener('updatefound',()=>trackInstallingWorker(reg,reg.installing));navigator.serviceWorker.addEventListener('controllerchange',()=>{updateReady=false;refreshUpdate();if(updateApplying)location.reload()});syncWaitingUpdate(reg)}
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();deferredInstall=e;refreshInstall()});
window.addEventListener('appinstalled',()=>{deferredInstall=null;refreshInstall()});
installBtn.onclick=async()=>{if(!deferredInstall)return;const p=deferredInstall;deferredInstall=null;refreshInstall();try{await p.prompt();await p.userChoice}catch{}};
updateBtn.onclick=()=>{const waiting=swRegistration?.waiting;if(!waiting){updateReady=false;refreshUpdate();return}if(updateApplying)return;if(!persist()){refreshUpdate();showCoach('SAVE FAILED','Update was not applied.','Free browser storage or export a backup, then retry.',1800);return}updateApplying=true;refreshUpdate();try{waiting.postMessage({type:'SKIP_WAITING'})}catch{updateApplying=false;syncWaitingUpdate();showCoach('UPDATE FAILED','Update was not applied.','Retry when the update is ready.',1600)}};
"""
html = replace_once(html, old_client, new_client, 'manual update client lifecycle')
index_path.write_text(html, encoding='utf-8')

# F14 remains about navigation isolation; remove its now-obsolete F15 boundary assertion.
f14 = f14_test_path.read_text(encoding='utf-8')
f14 = replace_once(
    f14,
    "assert.ok(sw.includes('await self.skipWaiting();'), 'F14 must not change install-time skipWaiting; F15 owns update lifecycle');\n",
    '',
    'F14 obsolete skipWaiting assertion',
)
f14_test_path.write_text(f14, encoding='utf-8')

# Register F15 as implemented pending the gated regression run.
reg = register_path.read_text(encoding='utf-8')
old_row = '| VC-017 | MEDIUM | `skipWaiting()` automatic activation conflicts with UI logic that expects a waiting service worker for manual update activation. | F15 | OPEN |'
new_row = '| VC-017 | MEDIUM | `skipWaiting()` automatic activation conflicts with UI logic that expects a waiting service worker for manual update activation. | F15 | FIXED — VERIFYING |'
reg = replace_once(reg, old_row, new_row, 'VC-017 register row')
reg += '''\n## F15 implementation record — explicit PWA update activation\n\n- Updated service workers no longer call `skipWaiting()` during `install`; when an older worker controls an open page, the new worker can now reach the browser's normal `waiting` state.\n- The explicit `SKIP_WAITING` message handler remains the sole early-activation path, so activation is initiated by the app's update action rather than automatically by installation.\n- Client `updateReady` state is now synchronized from the actual `ServiceWorkerRegistration.waiting` property. An `installed` event alone no longer marks an update ready.\n- Existing `registration.waiting` workers are detected immediately, and workers already installing when registration is observed are tracked in addition to future `updatefound` events.\n- Installed/redundant worker state changes schedule a registration re-inspection so the UI reflects the registration's final waiting state rather than racing the lifecycle transition.\n- The update button captures the actual waiting worker, persists the save first, and sends `SKIP_WAITING` only after persistence succeeds. Missing/stale waiting workers fail closed without entering an applying state.\n- `controllerchange` reload remains gated by `updateApplying`, preventing first-install or unrelated controller changes from forcing a page reload.\n- F14 navigation cache isolation is unchanged. F16 cache revision/freshness/write behavior is unchanged and the cache revision remains `6.1.0-pwa4`.\n- No gameplay, balance, leaderboard, replay, save-schema, scoring or visual-design behavior changed in F15.\n'''
register_path.write_text(reg, encoding='utf-8')
