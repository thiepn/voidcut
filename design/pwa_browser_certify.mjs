import fs from 'node:fs';
import { chromium } from 'playwright';

const origin = 'http://127.0.0.1:4173';
const core = [
  '/', '/index.html', '/manifest.webmanifest', '/icon.svg', '/icon-192.png', '/icon-512.png', '/icon-maskable-512.png',
  '/design/voidcut-design-system.css', '/design/voidcut-design-system.js'
];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'allow' });
const page = await context.newPage();
const errors = [];
const failed = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
page.on('requestfailed', r => failed.push(r.url() + ': ' + (r.failure()?.errorText || 'failed')));

await page.goto(origin + '/', { waitUntil: 'networkidle' });
await page.waitForFunction(() => window.VoidcutDesign && 'serviceWorker' in navigator);

const manifestResponse = await page.request.get(origin + '/manifest.webmanifest');
if (!manifestResponse.ok()) throw new Error('manifest fetch failed ' + manifestResponse.status());
const manifest = await manifestResponse.json();
if (manifest.name !== 'VOIDCUT' || manifest.start_url !== './' || manifest.scope !== './') {
  throw new Error('manifest runtime contract mismatch');
}

await page.evaluate(() => navigator.serviceWorker.ready.then(() => true));
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(() => navigator.serviceWorker.controller && window.VoidcutDesign && window.VoidcutCertification);

const onlineAudit = await page.evaluate(async corePaths => {
  const reg = await navigator.serviceWorker.getRegistration('./');
  const keys = await caches.keys();
  const cache = await caches.open('voidcut-shell-6.0.0-pwa1');
  const checks = {};
  for (const path of corePaths) {
    const url = new URL(path, location.origin).href;
    checks[path] = !!(await cache.match(url, { ignoreSearch: true }));
  }
  return {
    controlled: !!navigator.serviceWorker.controller,
    scope: reg?.scope || '',
    active: reg?.active?.state || '',
    waiting: !!reg?.waiting,
    keys,
    checks,
    title: document.title,
    visualPhase: document.querySelector('meta[name="voidcut-visual-phase"]')?.content || ''
  };
}, core);

if (!onlineAudit.controlled || onlineAudit.active !== 'activated') throw new Error('service worker is not active/controller');
if (!onlineAudit.scope.endsWith('/')) throw new Error('service worker scope invalid: ' + onlineAudit.scope);
if (!onlineAudit.keys.includes('voidcut-shell-6.0.0-pwa1')) throw new Error('release cache missing');
for (const [path, ok] of Object.entries(onlineAudit.checks)) if (!ok) throw new Error('precache missing ' + path);
if (onlineAudit.title !== 'VOIDCUT' || onlineAudit.visualPhase !== 'VD7') throw new Error('controlled product boot mismatch');

const cdp = await context.newCDPSession(page);
const appManifest = await cdp.send('Page.getAppManifest');
if ((appManifest.errors || []).length) throw new Error('manifest parser errors: ' + JSON.stringify(appManifest.errors));
try {
  const installability = await cdp.send('Page.getInstallabilityErrors');
  if ((installability.installabilityErrors || []).length) {
    throw new Error('installability errors: ' + JSON.stringify(installability.installabilityErrors));
  }
} catch (error) {
  if (String(error).includes('installability errors:')) throw error;
  console.log('Page.getInstallabilityErrors unavailable; manifest/SW/offline gates remain authoritative');
}

await context.setOffline(true);
await page.reload({ waitUntil: 'domcontentloaded' });
await page.waitForFunction(() => window.VoidcutDesign && window.VoidcutCertification && navigator.serviceWorker.controller);
const offlineAudit = await page.evaluate(() => ({
  title: document.title,
  phase: document.querySelector('meta[name="voidcut-visual-phase"]')?.content || '',
  controller: !!navigator.serviceWorker.controller,
  menuVisible: !document.getElementById('menu')?.classList.contains('hidden')
}));
if (offlineAudit.title !== 'VOIDCUT' || offlineAudit.phase !== 'VD7' || !offlineAudit.controller || !offlineAudit.menuVisible) {
  throw new Error('offline boot contract failed: ' + JSON.stringify(offlineAudit));
}
await context.setOffline(false);

const originalSW = fs.readFileSync('sw.js', 'utf8');
const updatedSW = originalSW.replace('6.0.0-pwa1', '6.0.0-pwa2-test');
if (updatedSW === originalSW) throw new Error('could not construct update worker');
fs.writeFileSync('sw.js', updatedSW);

const updateAudit = await page.evaluate(async () => {
  const reg = await navigator.serviceWorker.getRegistration('./');
  await reg.update();
  const deadline = Date.now() + 10000;
  while (!reg.waiting && Date.now() < deadline) await new Promise(r => setTimeout(r, 50));
  return { waiting: !!reg.waiting, active: reg.active?.state || '', keys: await caches.keys(), controller: !!navigator.serviceWorker.controller };
});
if (!updateAudit.waiting) throw new Error('updated worker did not wait');
if (!updateAudit.keys.includes('voidcut-shell-6.0.0-pwa1') || !updateAudit.keys.includes('voidcut-shell-6.0.0-pwa2-test')) {
  throw new Error('atomic parallel caches missing: ' + JSON.stringify(updateAudit.keys));
}

const applyAudit = await page.evaluate(async () => {
  const reg = await navigator.serviceWorker.getRegistration('./');
  const changed = new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('controllerchange timeout')), 10000);
    navigator.serviceWorker.addEventListener('controllerchange', () => { clearTimeout(timer); resolve(true); }, { once: true });
  });
  reg.waiting.postMessage({ type: 'SKIP_WAITING' });
  await changed;
  const deadline = Date.now() + 5000;
  let keys = await caches.keys();
  while (keys.includes('voidcut-shell-6.0.0-pwa1') && Date.now() < deadline) {
    await new Promise(r => setTimeout(r, 50));
    keys = await caches.keys();
  }
  return { controller: !!navigator.serviceWorker.controller, keys };
});
fs.writeFileSync('sw.js', originalSW);

if (!applyAudit.controller) throw new Error('updated worker failed to control page');
if (applyAudit.keys.includes('voidcut-shell-6.0.0-pwa1') || !applyAudit.keys.includes('voidcut-shell-6.0.0-pwa2-test')) {
  throw new Error('old cache cleanup failed: ' + JSON.stringify(applyAudit.keys));
}
if (errors.length) throw new Error('browser errors: ' + JSON.stringify(errors));
if (failed.length) throw new Error('request failures: ' + JSON.stringify(failed));

console.log('ONLINE', JSON.stringify(onlineAudit));
console.log('OFFLINE', JSON.stringify(offlineAudit));
console.log('UPDATE_WAIT', JSON.stringify(updateAudit));
console.log('UPDATE_APPLY', JSON.stringify(applyAudit));
console.log('VOIDCUT PWA BROWSER CERTIFICATION PASS');
await browser.close();
