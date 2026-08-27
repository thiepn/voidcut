import { test, expect } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SW_PATH = path.join(ROOT, 'sw.js');
const API = 'https://voidcut-leaderboard.thiepn.workers.dev';
const SAVE_KEY = 'voidcut.standalone.v1';
const IDENTITY_KEY = 'voidcut.leaderboard.identity.v1';
const IDENTITY_BACKUP_KEY = 'voidcut.leaderboard.identity.backup.v1';
const QUEUE_KEY = 'voidcut.leaderboard.submissions.v1';
const CACHE_PREFIX = 'voidcut-shell-';
const BUILD = '6.1.0';

const baseSave = {
  schemaVersion: 17,
  tutorialSeen: true,
  dividerTutorialSeen: true,
  bestScore: 230023,
  deepestChamber: 23,
  totalRuns: 23,
  settings: {
    sound: false,
    music: false,
    haptics: false,
    reducedMotion: true,
    highContrast: false,
    largeUI: false,
    trails: true,
    swipeSensitivity: 'normal',
    powerMode: 'full',
    colorTheme: 'arcade',
  },
};

const legacyIdentity = {
  playerId: 'f23-player-00000001',
  name: 'F23Tester',
  token: 'f23-test-token-0000000000000001',
};

async function installApiFixtures(page) {
  await page.route(`${API}/**`, async route => {
    const url = new URL(route.request().url());
    const headers = {
      'access-control-allow-origin': '*',
      'content-type': 'application/json; charset=utf-8',
    };
    if (url.pathname === '/run/start') {
      await route.fulfill({
        status: 200,
        headers,
        body: JSON.stringify({
          ok: true,
          ticketId: 'f23-browser-ticket',
          seed: 0x23c0ffee,
          expiresAt: Date.now() + 60 * 60 * 1000,
          ruleset: { build: BUILD, replay: 9, arena: 2, director: 6 },
          ranked: true,
        }),
      });
      return;
    }
    if (url.pathname === '/leaderboard') {
      await route.fulfill({
        status: 200,
        headers,
        body: JSON.stringify({
          ok: true,
          ruleset: { build: BUILD, replay: 9, arena: 2, director: 6 },
          rows: [],
          self: null,
        }),
      });
      return;
    }
    if (url.pathname.startsWith('/run/submit/')) {
      await route.fulfill({ status: 503, headers, body: JSON.stringify({ error: 'f23-offline-fixture' }) });
      return;
    }
    await route.fulfill({ status: 404, headers, body: JSON.stringify({ error: 'not-found' }) });
  });
}

async function seedDurableState(page) {
  await page.addInitScript(({ save, identity }) => {
    if (!localStorage.getItem('voidcut.standalone.v1')) {
      localStorage.setItem('voidcut.standalone.v1', JSON.stringify(save));
    }
    if (!localStorage.getItem('voidcut.leaderboard.identity.v1')) {
      localStorage.setItem('voidcut.leaderboard.identity.v1', JSON.stringify(identity));
    }
  }, { save: baseSave, identity: legacyIdentity });
}

async function openApp(page, { seed = true } = {}) {
  await installApiFixtures(page);
  if (seed) await seedDurableState(page);
  await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
}

async function ensureControlledServiceWorker(page) {
  await page.evaluate(async () => { await navigator.serviceWorker.ready; });
  if (!(await page.evaluate(() => !!navigator.serviceWorker.controller))) {
    await page.reload({ waitUntil: 'domcontentloaded' });
  }
  await expect.poll(() => page.evaluate(() => !!navigator.serviceWorker.controller), { timeout: 20_000 }).toBe(true);
}

async function durableSnapshot(page) {
  return page.evaluate(({ saveKey, identityKey, backupKey, queueKey }) => {
    function parse(raw) {
      try { return raw ? JSON.parse(raw) : null; } catch { return null; }
    }
    const save = parse(localStorage.getItem(saveKey));
    const unwrapSave = value => value?.d || value || null;
    const identity = parse(localStorage.getItem(identityKey));
    const backup = parse(localStorage.getItem(backupKey));
    const unwrapIdentity = value => value?.d || value || null;
    return {
      save: unwrapSave(save),
      identity: unwrapIdentity(identity),
      backupIdentity: unwrapIdentity(backup),
      queuePresent: localStorage.getItem(queueKey) != null,
    };
  }, { saveKey: SAVE_KEY, identityKey: IDENTITY_KEY, backupKey: IDENTITY_BACKUP_KEY, queueKey: QUEUE_KEY });
}

function expectSeededState(snapshot) {
  expect(snapshot.save?.schemaVersion).toBe(17);
  expect(snapshot.save?.bestScore).toBe(baseSave.bestScore);
  expect(snapshot.save?.deepestChamber).toBe(baseSave.deepestChamber);
  expect(snapshot.save?.settings?.reducedMotion).toBe(true);
  expect(snapshot.identity).toMatchObject(legacyIdentity);
  expect(snapshot.backupIdentity).toMatchObject(legacyIdentity);
}

async function voidcutCaches(page) {
  return page.evaluate(async prefix => (await caches.keys()).filter(name => name.startsWith(prefix)).sort(), CACHE_PREFIX);
}

async function currentCacheHasIndex(page) {
  return page.evaluate(async ({ prefix }) => {
    const names = (await caches.keys()).filter(name => name.startsWith(prefix));
    if (!names.length) return false;
    for (const name of names) {
      const cache = await caches.open(name);
      const match = await cache.match(new URL('./index.html', location.href).href, { ignoreSearch: true });
      if (match) return true;
    }
    return false;
  }, { prefix: CACHE_PREFIX });
}

async function workerStatus(page, workerKind = 'controller') {
  return page.evaluate(async kind => {
    const reg = await navigator.serviceWorker.getRegistration('./');
    const worker = kind === 'waiting' ? reg?.waiting : navigator.serviceWorker.controller;
    if (!worker) return null;
    return await new Promise(resolve => {
      const channel = new MessageChannel();
      const timer = setTimeout(() => resolve(null), 1500);
      channel.port1.onmessage = event => {
        clearTimeout(timer);
        resolve(event.data || null);
      };
      worker.postMessage({ type: 'DIAGNOSTIC_STATUS' }, [channel.port2]);
    });
  }, workerKind);
}

async function waitForNoInstallingWorker(page) {
  await expect.poll(() => page.evaluate(async () => {
    const reg = await navigator.serviceWorker.getRegistration('./');
    return reg?.installing?.state || 'none';
  }), { timeout: 20_000 }).not.toBe('installing');
}

function capturePageErrors(page) {
  const errors = [];
  page.on('pageerror', error => errors.push(String(error?.stack || error)));
  return errors;
}

test.describe.configure({ mode: 'serial' });

test('F23 offline boot preserves save and leaderboard identity after a controlled install', async ({ page, context }) => {
  test.setTimeout(90_000);
  const errors = capturePageErrors(page);
  await openApp(page);
  await ensureControlledServiceWorker(page);
  expectSeededState(await durableSnapshot(page));
  expect(await currentCacheHasIndex(page)).toBe(true);

  await context.setOffline(true);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
  expect(await page.evaluate(() => !!navigator.serviceWorker.controller)).toBe(true);
  expectSeededState(await durableSnapshot(page));
  expect(errors).toEqual([]);
});

test('F23 deleting the shell cache self-heals online and the rebuilt shell boots offline', async ({ page, context }) => {
  test.setTimeout(90_000);
  const errors = capturePageErrors(page);
  await openApp(page);
  await ensureControlledServiceWorker(page);
  expect((await voidcutCaches(page)).length).toBeGreaterThan(0);

  await page.evaluate(async prefix => {
    for (const name of await caches.keys()) if (name.startsWith(prefix)) await caches.delete(name);
  }, CACHE_PREFIX);
  expect(await voidcutCaches(page)).toEqual([]);

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
  await expect.poll(() => currentCacheHasIndex(page), { timeout: 15_000 }).toBe(true);
  expectSeededState(await durableSnapshot(page));

  await context.setOffline(true);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
  expectSeededState(await durableSnapshot(page));
  expect(errors).toEqual([]);
});

test('F23 a broken update install cannot evict the active worker, cache, or durable state', async ({ page, context }) => {
  test.setTimeout(120_000);
  const errors = capturePageErrors(page);
  const original = await fs.readFile(SW_PATH, 'utf8');
  try {
    await openApp(page);
    await ensureControlledServiceWorker(page);
    const beforeCaches = await voidcutCaches(page);
    expect(beforeCaches.length).toBeGreaterThan(0);
    expectSeededState(await durableSnapshot(page));

    const broken = original.replace(
      "  './design/voidcut-design-system.js'\n];",
      "  './design/voidcut-design-system.js',\n  './__f23_missing_core_asset__.js'\n];",
    );
    expect(broken).not.toBe(original);
    await fs.writeFile(SW_PATH, `${broken}\n// F23 intentionally broken install ${Date.now()}\n`, 'utf8');

    await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      if (!reg) throw new Error('service worker registration missing');
      await reg.update();
    });
    await waitForNoInstallingWorker(page);
    await page.waitForTimeout(500);

    const state = await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      return {
        controller: !!navigator.serviceWorker.controller,
        active: !!reg?.active,
        waiting: !!reg?.waiting,
      };
    });
    expect(state.controller).toBe(true);
    expect(state.active).toBe(true);
    expect(state.waiting).toBe(false);
    expect(await voidcutCaches(page)).toEqual(beforeCaches);
    expectSeededState(await durableSnapshot(page));

    await context.setOffline(true);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page.locator('#menu')).toBeVisible();
    expectSeededState(await durableSnapshot(page));
    expect(errors).toEqual([]);
  } finally {
    await context.setOffline(false);
    await fs.writeFile(SW_PATH, original, 'utf8');
  }
});

test('F23 a valid explicit update claims two open tabs without losing durable state', async ({ page, context }) => {
  test.setTimeout(120_000);
  const errorsA = capturePageErrors(page);
  const original = await fs.readFile(SW_PATH, 'utf8');
  const marker = `f23-multitab-${Date.now()}`;
  let pageB;
  try {
    await openApp(page);
    await ensureControlledServiceWorker(page);
    pageB = await context.newPage();
    const errorsB = capturePageErrors(pageB);
    await openApp(pageB, { seed: false });
    await ensureControlledServiceWorker(pageB);
    expectSeededState(await durableSnapshot(page));
    expectSeededState(await durableSnapshot(pageB));

    const oldA = await workerStatus(page);
    const oldB = await workerStatus(pageB);
    expect(oldA?.probe).toBeUndefined();
    expect(oldB?.probe).toBeUndefined();

    const needle = "port.postMessage({ type: 'VOIDCUT_SW_STATUS', build: VOIDCUT_BUILD, cache: VOIDCUT_CACHE, scope: VOIDCUT_SCOPE });";
    const replacement = `port.postMessage({ type: 'VOIDCUT_SW_STATUS', build: VOIDCUT_BUILD, cache: VOIDCUT_CACHE, scope: VOIDCUT_SCOPE, probe: '${marker}' });`;
    const updated = original.replace(needle, replacement);
    expect(updated).not.toBe(original);
    await fs.writeFile(SW_PATH, `${updated}\n// F23 multitab update ${marker}\n`, 'utf8');

    await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      if (!reg) throw new Error('service worker registration missing');
      await reg.update();
    });
    await expect.poll(() => page.evaluate(async () => !!(await navigator.serviceWorker.getRegistration('./'))?.waiting), { timeout: 30_000 }).toBe(true);
    await expect(page.locator('#updateApp')).toBeVisible();
    expect((await workerStatus(page, 'waiting'))?.probe).toBe(marker);
    expect((await workerStatus(page))?.probe).toBeUndefined();
    expect((await workerStatus(pageB))?.probe).toBeUndefined();

    const loaded = page.waitForEvent('load');
    await page.locator('#updateApp').click();
    await loaded;
    await expect(page.locator('#menu')).toBeVisible();
    await expect.poll(async () => (await workerStatus(page))?.probe || null, { timeout: 30_000 }).toBe(marker);
    await expect.poll(async () => (await workerStatus(pageB))?.probe || null, { timeout: 30_000 }).toBe(marker);

    expectSeededState(await durableSnapshot(page));
    expectSeededState(await durableSnapshot(pageB));
    expect(errorsA).toEqual([]);
    expect(errorsB).toEqual([]);
  } finally {
    await fs.writeFile(SW_PATH, original, 'utf8');
    if (pageB) await pageB.close();
  }
});

test('F23 cache generations overlap while waiting and obsolete shells are deleted only after activation', async ({ page }) => {
  test.setTimeout(120_000);
  const errors = capturePageErrors(page);
  await openApp(page);
  await ensureControlledServiceWorker(page);
  const oldCaches = await voidcutCaches(page);
  expect(oldCaches).toContain(`${CACHE_PREFIX}${BUILD}`);
  const nextBuild = `f23-next-${Date.now()}`;

  await page.evaluate(async build => {
    await navigator.serviceWorker.register(`./sw.js?build=${encodeURIComponent(build)}`, { scope: './', updateViaCache: 'none' });
  }, nextBuild);
  await expect.poll(() => page.evaluate(async () => !!(await navigator.serviceWorker.getRegistration('./'))?.waiting), { timeout: 30_000 }).toBe(true);

  const whileWaiting = await voidcutCaches(page);
  expect(whileWaiting).toContain(`${CACHE_PREFIX}${BUILD}`);
  expect(whileWaiting).toContain(`${CACHE_PREFIX}${nextBuild}`);

  await page.evaluate(async () => {
    const reg = await navigator.serviceWorker.getRegistration('./');
    if (!reg?.waiting) throw new Error('waiting next-build worker missing');
    reg.waiting.postMessage({ type: 'SKIP_WAITING' });
  });
  await expect.poll(() => page.evaluate(() => navigator.serviceWorker.controller?.scriptURL || ''), { timeout: 30_000 }).toContain(`build=${encodeURIComponent(nextBuild)}`);
  await expect.poll(() => voidcutCaches(page), { timeout: 20_000 }).toEqual([`${CACHE_PREFIX}${nextBuild}`]);
  expectSeededState(await durableSnapshot(page));
  expect(errors).toEqual([]);
});

test('F23 unregister plus cache removal can reinstall cleanly without deleting application data', async ({ page, context }) => {
  test.setTimeout(120_000);
  const errors = capturePageErrors(page);
  await openApp(page);
  await ensureControlledServiceWorker(page);
  expectSeededState(await durableSnapshot(page));

  await page.evaluate(async prefix => {
    const reg = await navigator.serviceWorker.getRegistration('./');
    if (reg) await reg.unregister();
    for (const name of await caches.keys()) if (name.startsWith(prefix)) await caches.delete(name);
  }, CACHE_PREFIX);
  expect(await voidcutCaches(page)).toEqual([]);
  expectSeededState(await durableSnapshot(page));

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
  await ensureControlledServiceWorker(page);
  await expect.poll(() => currentCacheHasIndex(page), { timeout: 15_000 }).toBe(true);
  expectSeededState(await durableSnapshot(page));

  await context.setOffline(true);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
  expectSeededState(await durableSnapshot(page));
  expect(errors).toEqual([]);
});

test('F23 deliberate localStorage loss boots a clean save offline and does not resurrect leaderboard ownership', async ({ page, context }) => {
  test.setTimeout(90_000);
  const errors = capturePageErrors(page);
  await openApp(page);
  await ensureControlledServiceWorker(page);
  expectSeededState(await durableSnapshot(page));

  await page.evaluate(() => localStorage.clear());
  await context.setOffline(true);
  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();

  const after = await durableSnapshot(page);
  expect(after.save?.schemaVersion).toBe(17);
  expect(after.save?.bestScore).toBe(0);
  expect(after.save?.totalRuns).toBe(0);
  expect(after.identity).toBeNull();
  expect(after.backupIdentity).toBeNull();
  expect(after.queuePresent).toBe(false);
  expect(await page.evaluate(() => !!navigator.serviceWorker.controller)).toBe(true);
  expect(errors).toEqual([]);
});
