import fs from 'node:fs';
import { chromium, firefox, webkit } from 'playwright';

const ROOT_URL = 'http://127.0.0.1:4173/';
const PROJECT_URL = 'http://127.0.0.1:4174/voidcut/';
const SAVE_KEY = 'voidcut.standalone.v1';
const failures = [];
const results = [];

function fail(label, detail) {
  failures.push(`${label}: ${detail}`);
}

async function inspectBoot(browserType, engine, url, viewport, label) {
  const browser = await browserType.launch({ headless: true });
  const context = await browser.newContext({ viewport, serviceWorkers: 'block' });
  const page = await context.newPage();
  const runtime = [];
  page.on('pageerror', e => runtime.push(`pageerror ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') runtime.push(`console ${m.text()}`); });
  page.on('requestfailed', r => runtime.push(`requestfailed ${r.url()} ${r.failure()?.errorText || ''}`));
  page.on('response', r => {
    if (r.url().startsWith(new URL(url).origin) && r.status() >= 400) runtime.push(`http ${r.status()} ${r.url()}`);
  });
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForFunction(() => window.VoidcutDesign && window.VoidcutCertification, { timeout: 15000 });
    await page.waitForTimeout(120);
    const audit = await page.evaluate(() => ({
      title: document.title,
      phase: document.querySelector('meta[name="voidcut-visual-phase"]')?.content || '',
      menu: !document.getElementById('menu')?.classList.contains('hidden'),
      overflow: document.documentElement.scrollWidth > innerWidth + 1 || document.body.scrollWidth > innerWidth + 1,
      cert: window.VoidcutCertification.audit(),
    }));
    if (audit.title !== 'VOIDCUT') fail(label, `title=${audit.title}`);
    if (audit.phase !== 'VD7') fail(label, `visual phase=${audit.phase}`);
    if (!audit.menu) fail(label, 'menu is not visible');
    if (audit.overflow) fail(label, 'horizontal overflow');
    if (!audit.cert.themeSuite) fail(label, 'theme-suite runtime audit failed');
    if (audit.cert.touchFailures?.length) fail(label, `undersized controls ${JSON.stringify(audit.cert.touchFailures.slice(0, 3))}`);
    if (runtime.length) fail(label, runtime.join(' | '));
    results.push(`${engine} ${label} PASS`);
  } catch (error) {
    fail(label, error.stack || String(error));
  } finally {
    await context.close();
    await browser.close();
  }
}

async function crossEngineSmoke() {
  const engines = [
    ['Chromium', chromium],
    ['Firefox', firefox],
    ['WebKit', webkit],
  ];
  const deployments = [
    ['root', ROOT_URL],
    ['project', PROJECT_URL],
  ];
  const viewports = [
    ['desktop', { width: 1440, height: 900 }],
    ['mobile', { width: 390, height: 844 }],
  ];
  for (const [engine, type] of engines) {
    for (const [deployment, url] of deployments) {
      for (const [vp, viewport] of viewports) {
        await inspectBoot(type, engine, url, viewport, `${deployment}/${vp}`);
      }
    }
  }
}

async function checkManifestInstallability(context, page, label) {
  const cdp = await context.newCDPSession(page);
  const manifest = await cdp.send('Page.getAppManifest');
  if ((manifest.errors || []).length) fail(label, `manifest errors ${JSON.stringify(manifest.errors)}`);
  try {
    const install = await cdp.send('Page.getInstallabilityErrors');
    if ((install.installabilityErrors || []).length) fail(label, `installability errors ${JSON.stringify(install.installabilityErrors)}`);
  } catch (error) {
    if (String(error).includes('installability errors')) throw error;
    results.push(`${label} installability API unavailable; manifest/SW gates retained`);
  }
}

async function waitForController(page, timeout = 15000) {
  await page.waitForFunction(() => !!navigator.serviceWorker?.controller, { timeout });
}

async function chromiumReleaseLifecycle(url, tempSwPath, label) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'allow' });
  let page = await context.newPage();
  const runtime = [];
  page.on('pageerror', e => runtime.push(`pageerror ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') runtime.push(`console ${m.text()}`); });
  page.on('requestfailed', r => runtime.push(`requestfailed ${r.url()} ${r.failure()?.errorText || ''}`));
  page.on('response', r => { if (r.url().startsWith(new URL(url).origin) && r.status() >= 400) runtime.push(`http ${r.status()} ${r.url()}`); });

  try {
    // Fresh online boot and registration.
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForFunction(() => window.VoidcutDesign && window.VoidcutCertification && 'serviceWorker' in navigator, { timeout: 15000 });
    await page.evaluate(() => navigator.serviceWorker.ready.then(() => true));
    await page.reload({ waitUntil: 'networkidle', timeout: 30000 });
    await waitForController(page);

    const online = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      const primary = JSON.parse(localStorage.getItem('voidcut.standalone.v1') || 'null');
      return {
        title: document.title,
        phase: document.querySelector('meta[name="voidcut-visual-phase"]')?.content || '',
        scope: reg?.scope || '',
        active: reg?.active?.state || '',
        controller: !!navigator.serviceWorker.controller,
        caches: await caches.keys(),
        primary: primary ? { f: primary.f, v: primary.v, schema: primary.d?.schemaVersion } : null,
      };
    });
    if (online.title !== 'VOIDCUT' || online.phase !== 'VD7') fail(label, `fresh boot mismatch ${JSON.stringify(online)}`);
    if (!online.controller || online.active !== 'activated') fail(label, `service worker not controlling ${JSON.stringify(online)}`);
    if (!online.caches.includes('voidcut-shell-6.0.0-pwa1')) fail(label, `release cache missing ${JSON.stringify(online.caches)}`);
    if (!online.primary || online.primary.f !== 2 || online.primary.v !== 16 || online.primary.schema !== 16) fail(label, `fresh primary save invalid ${JSON.stringify(online.primary)}`);
    if (label === 'root') {
      if (!new URL(online.scope).pathname.endsWith('/')) fail(label, `root scope invalid ${online.scope}`);
      await checkManifestInstallability(context, page, `${label}/installability`);
    } else {
      if (!new URL(online.scope).pathname.endsWith('/voidcut/')) fail(label, `project scope invalid ${online.scope}`);
      await checkManifestInstallability(context, page, `${label}/installability`);
    }

    // Built-in deterministic release audit and system diagnostics.
    await page.evaluate(() => document.getElementById('runStressDiagnostics')?.click());
    await page.waitForFunction(() => /VOIDCUT 6\.0\.0 RELEASE AUDIT • (PASS|FAIL)/.test(document.getElementById('diagnosticsText')?.textContent || ''), { timeout: 90000 });
    const stress = await page.locator('#diagnosticsText').textContent();
    if (!stress?.includes('RELEASE AUDIT • PASS')) fail(label, `built-in release audit failed: ${stress?.slice(0, 800)}`);

    await page.evaluate(() => document.getElementById('runDiagnostics')?.click());
    await page.waitForFunction(() => /RESULT: (PASS|WARN|FAIL)/.test(document.getElementById('diagnosticsText')?.textContent || ''), { timeout: 30000 });
    const system = await page.locator('#diagnosticsText').textContent();
    if (system?.includes('RESULT: FAIL')) fail(label, `system diagnostics failed: ${system?.slice(0, 1000)}`);

    // Offline reload.
    await context.setOffline(true);
    await page.reload({ waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForFunction(() => window.VoidcutDesign && window.VoidcutCertification && navigator.serviceWorker.controller, { timeout: 15000 });
    const offline = await page.evaluate(() => ({
      title: document.title,
      phase: document.querySelector('meta[name="voidcut-visual-phase"]')?.content || '',
      controller: !!navigator.serviceWorker.controller,
      menu: !document.getElementById('menu')?.classList.contains('hidden'),
    }));
    if (offline.title !== 'VOIDCUT' || offline.phase !== 'VD7' || !offline.controller || !offline.menu) fail(label, `offline reload failed ${JSON.stringify(offline)}`);
    await context.setOffline(false);

    // Atomic update path: install a second revision, confirm it waits, then explicitly activate it.
    const originalSW = fs.readFileSync(tempSwPath, 'utf8');
    const updatedSW = originalSW.replace('6.0.0-pwa1', '6.0.0-rc-update-test');
    if (updatedSW === originalSW) throw new Error(`cannot construct test SW revision at ${tempSwPath}`);
    fs.writeFileSync(tempSwPath, updatedSW);
    const waiting = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      await reg.update();
      const deadline = Date.now() + 15000;
      while (!reg.waiting && Date.now() < deadline) await new Promise(r => setTimeout(r, 50));
      return { waiting: !!reg.waiting, keys: await caches.keys(), controller: !!navigator.serviceWorker.controller };
    });
    if (!waiting.waiting) fail(label, 'update worker did not enter waiting state');
    if (!waiting.keys.includes('voidcut-shell-6.0.0-pwa1') || !waiting.keys.includes('voidcut-shell-6.0.0-rc-update-test')) fail(label, `parallel release caches missing ${JSON.stringify(waiting.keys)}`);

    const applied = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      const changed = new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('controllerchange timeout')), 15000);
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
    fs.writeFileSync(tempSwPath, originalSW);
    if (!applied.controller) fail(label, 'updated worker did not control page');
    if (applied.keys.includes('voidcut-shell-6.0.0-pwa1') || !applied.keys.includes('voidcut-shell-6.0.0-rc-update-test')) fail(label, `cache cleanup after update failed ${JSON.stringify(applied.keys)}`);

    // Browser-level service-worker uninstall + reinstall lifecycle.
    await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      if (reg) await reg.unregister();
      for (const key of await caches.keys()) if (key.startsWith('voidcut-shell-')) await caches.delete(key);
    });
    await page.close();
    page = await context.newPage();
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.evaluate(() => navigator.serviceWorker.ready.then(() => true));
    await page.reload({ waitUntil: 'networkidle', timeout: 30000 });
    await waitForController(page);
    const reinstall = await page.evaluate(async () => ({
      controller: !!navigator.serviceWorker.controller,
      caches: await caches.keys(),
      primary: JSON.parse(localStorage.getItem('voidcut.standalone.v1') || 'null')?.d?.schemaVersion || null,
    }));
    if (!reinstall.controller || !reinstall.caches.includes('voidcut-shell-6.0.0-pwa1') || reinstall.primary !== 16) fail(label, `reinstall lifecycle failed ${JSON.stringify(reinstall)}`);

    if (runtime.length) fail(label, runtime.join(' | '));
    results.push(`${label} PWA lifecycle PASS`);
  } catch (error) {
    fail(label, error.stack || String(error));
  } finally {
    await context.close();
    await browser.close();
  }
}

async function legacySaveMigrations() {
  const fixtures = [1, 8, 15];
  for (const schemaVersion of fixtures) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 390, height: 844 }, serviceWorkers: 'block' });
    await context.addInitScript(({ key, schemaVersion }) => {
      if (!/^https?:$/.test(location.protocol)) return;
      const legacy = {
        schemaVersion,
        bestScore: 654321 + schemaVersion,
        deepestChamber: 17,
        totalRuns: 23,
        lifetimeCuts: 456,
        lifetimeCloseCalls: 7,
        tutorialSeen: true,
        dividerTutorialSeen: true,
        records: { largestCut: 42.5, bestSingleCut: 12345, longestRunSeconds: 98.5 },
        settings: {
          sound: false, music: false, haptics: false, reducedMotion: true, highContrast: false,
          largeUI: true, trails: false, swipeSensitivity: 'low', powerMode: 'eco', colorTheme: 'arcade'
        },
        cosmetics: { arena: 'void', ball: 'core', trail: 'beam', cut: 'pulse', collapse: 'implode' }
      };
      localStorage.setItem(key, JSON.stringify(legacy));
    }, { key: SAVE_KEY, schemaVersion });
    const page = await context.newPage();
    try {
      await page.goto(ROOT_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForFunction(() => window.VoidcutDesign && window.VoidcutCertification, { timeout: 15000 });
      const migrated = await page.evaluate(key => {
        const x = JSON.parse(localStorage.getItem(key) || 'null');
        return x && {
          f: x.f, v: x.v, schemaVersion: x.d?.schemaVersion,
          bestScore: x.d?.bestScore, deepestChamber: x.d?.deepestChamber, totalRuns: x.d?.totalRuns,
          lifetimeCuts: x.d?.lifetimeCuts, largestCut: x.d?.records?.largestCut,
          sound: x.d?.settings?.sound, music: x.d?.settings?.music, largeUI: x.d?.settings?.largeUI,
          powerMode: x.d?.settings?.powerMode, migrationFromSchema: x.d?.system?.migrationFromSchema,
          arena: x.d?.cosmetics?.arena, ball: x.d?.cosmetics?.ball,
        };
      }, SAVE_KEY);
      const expectedScore = 654321 + schemaVersion;
      const ok = migrated && migrated.f === 2 && migrated.v === 16 && migrated.schemaVersion === 16 &&
        migrated.bestScore === expectedScore && migrated.deepestChamber === 17 && migrated.totalRuns === 23 &&
        migrated.lifetimeCuts === 456 && migrated.largestCut === 42.5 && migrated.sound === false && migrated.music === false &&
        migrated.largeUI === true && migrated.powerMode === 'eco' && migrated.migrationFromSchema === schemaVersion &&
        migrated.arena === 'void' && migrated.ball === 'core';
      if (!ok) fail(`save/schema-${schemaVersion}`, `migration mismatch ${JSON.stringify(migrated)}`);
      else results.push(`legacy save schema ${schemaVersion} → 16 PASS`);
    } catch (error) {
      fail(`save/schema-${schemaVersion}`, error.stack || String(error));
    } finally {
      await context.close();
      await browser.close();
    }
  }
}

await crossEngineSmoke();
await legacySaveMigrations();
await chromiumReleaseLifecycle(ROOT_URL, '/tmp/voidcut-root/sw.js', 'root');
await chromiumReleaseLifecycle(PROJECT_URL, '/tmp/voidcut-project/voidcut/sw.js', 'project');

console.log(`RC browser checks/results: ${results.length}`);
for (const result of results) console.log('PASS', result);
if (failures.length) {
  console.error(`VOIDCUT FINAL RC BROWSER CERTIFICATION FAIL (${failures.length})`);
  for (const x of failures) console.error('- ' + x);
  process.exit(1);
}
console.log('VOIDCUT FINAL RC BROWSER CERTIFICATION PASS');
