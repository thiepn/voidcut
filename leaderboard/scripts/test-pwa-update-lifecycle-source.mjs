import fs from 'node:fs';
import assert from 'node:assert/strict';

const root = new URL('../../', import.meta.url);
const sw = fs.readFileSync(new URL('sw.js', root), 'utf8');
const html = fs.readFileSync(new URL('index.html', root), 'utf8');

assert.ok(sw.includes("const VOIDCUT_CACHE_VERSION = '6.1.0-pwa4';"), 'F15 must not change F16 cache revision');

const installBlock = sw.match(/self\.addEventListener\('install',[\s\S]*?\n\}\);/);
assert.ok(installBlock, 'service-worker install handler missing');
assert.doesNotMatch(installBlock[0], /skipWaiting\s*\(/, 'install must not force an updated worker past waiting state');
assert.match(sw, /if \(type === 'SKIP_WAITING'\) \{\s*self\.skipWaiting\(\);\s*\}/, 'explicit SKIP_WAITING message must remain the activation path');
assert.match(sw, /self\.addEventListener\('activate',[\s\S]*?await self\.clients\.claim\(\);/, 'activated worker must still claim clients so explicit update can hand control over');

for (const name of ['syncWaitingUpdate', 'trackInstallingWorker', 'watchRegistration']) {
  assert.match(html, new RegExp(`function ${name}\\(`), `${name} helper missing`);
}

const syncSource = html.match(/function syncWaitingUpdate\(reg=swRegistration\)\{[^\n]+\}/)?.[0];
const trackSource = html.match(/function trackInstallingWorker\(reg,worker\)\{[^\n]+\}/)?.[0];
assert.ok(syncSource, 'syncWaitingUpdate source missing');
assert.ok(trackSource, 'trackInstallingWorker source missing');

function makeTarget(extra = {}) {
  const handlers = new Map();
  return Object.assign({
    addEventListener(type, fn) {
      if (!handlers.has(type)) handlers.set(type, []);
      handlers.get(type).push(fn);
    },
    emit(type) {
      for (const fn of handlers.get(type) || []) fn();
    },
  }, extra);
}

let updateReady = false;
let refreshes = 0;
const swRegistration = null;
function refreshUpdate() { refreshes++; }
const { syncWaitingUpdate, trackInstallingWorker } = new Function(
  'setTimeout',
  'refreshUpdate',
  'swRegistration',
  'getUpdateReady',
  'setUpdateReady',
  `let updateReady=getUpdateReady();
   ${syncSource}
   ${trackSource}
   return {
     syncWaitingUpdate,
     trackInstallingWorker,
     read:()=>updateReady,
   };`,
)(setTimeout, refreshUpdate, swRegistration, () => updateReady, v => { updateReady = v; });

{
  const reg = { waiting: { state: 'installed' } };
  assert.equal(syncWaitingUpdate(reg), true, 'existing waiting worker must immediately mark update ready');
}
{
  const reg = { waiting: null };
  assert.equal(syncWaitingUpdate(reg), false, 'no waiting worker must clear update-ready state');
}
{
  const reg = { waiting: null };
  const worker = makeTarget({ state: 'installing' });
  trackInstallingWorker(reg, worker);
  assert.equal(refreshes > 0, true, 'tracking should inspect lifecycle state without throwing');
  const waiting = { state: 'installed', postMessage() {} };
  reg.waiting = waiting;
  worker.state = 'installed';
  worker.emit('statechange');
  await new Promise(resolve => setTimeout(resolve, 5));
  assert.equal(syncWaitingUpdate(reg), true, 'installed worker must be recognized only when registration.waiting is populated');
}
{
  const reg = { waiting: null };
  const worker = makeTarget({ state: 'redundant' });
  trackInstallingWorker(reg, worker);
  await new Promise(resolve => setTimeout(resolve, 5));
  assert.equal(syncWaitingUpdate(reg), false, 'redundant worker without waiting registration must not expose an update');
}

const watch = html.match(/function watchRegistration\(reg\)\{[^\n]+\}/)?.[0] || '';
assert.ok(watch.includes('if(reg.installing)trackInstallingWorker(reg,reg.installing)'), 'already-installing worker must be tracked');
assert.ok(watch.includes("reg.addEventListener('updatefound',()=>trackInstallingWorker(reg,reg.installing))"), 'future updatefound workers must be tracked');
assert.ok(watch.includes('updateReady=false;refreshUpdate();if(updateApplying)location.reload()'), 'controllerchange must clear readiness and reload only for explicit apply');
assert.ok(watch.endsWith('syncWaitingUpdate(reg)}'), 'registration watch must initialize from actual waiting state');
assert.ok(!watch.includes("w.state==='installed'&&navigator.serviceWorker.controller"), 'installed event alone must not fabricate updateReady');

const click = html.match(/updateBtn\.onclick=\(\)=>\{[^\n]+\};/)?.[0] || '';
assert.ok(click, 'update button handler missing');
assert.ok(click.includes('const waiting=swRegistration?.waiting'), 'update action must capture the actual waiting worker');
assert.ok(click.includes("if(!waiting){updateReady=false;refreshUpdate();return}"), 'stale/missing waiting worker must fail closed');
assert.ok(click.includes('if(updateApplying)return'), 'duplicate update activation must be blocked');
const persistAt = click.indexOf('if(!persist())');
const applyingAt = click.indexOf('updateApplying=true');
const postAt = click.indexOf("waiting.postMessage({type:'SKIP_WAITING'})");
assert.ok(persistAt >= 0 && applyingAt > persistAt && postAt > applyingAt, 'save must persist before applying state and SKIP_WAITING message');
assert.ok(click.includes("catch{updateApplying=false;syncWaitingUpdate();showCoach('UPDATE FAILED'"), 'postMessage failure must recover UI state');
assert.ok(!click.includes('swRegistration.waiting.postMessage'), 'handler must post to the captured waiting worker, avoiding registration races');

assert.match(html, /navigator\.serviceWorker\.register\('\.\/sw\.js',\{scope:'\.\/'\}\)\.then\(reg=>\{watchRegistration\(reg\);reg\.update\(\)\.catch\(\(\)=>\{\}\)\}\)/,
  'registration must continue to watch lifecycle and proactively check for updates');

console.log('F15 PWA manual update lifecycle regression PASS');
