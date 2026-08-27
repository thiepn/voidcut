import { test, expect } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SW_PATH = path.join(ROOT, 'sw.js');
const API = 'https://voidcut-leaderboard.thiepn.workers.dev';
const BUILD = '6.1.0';
const SAVE_SCHEMA = 17;
const REPLAY_VERSION = 9;
const ARENA_GENERATION = 2;
const DIRECTOR_GENERATION = 6;

const baseSave = {
  schemaVersion: SAVE_SCHEMA,
  tutorialSeen: true,
  dividerTutorialSeen: true,
  settings: {
    sound: false,
    music: false,
    haptics: false,
    reducedMotion: false,
    highContrast: false,
    largeUI: false,
    trails: true,
    swipeSensitivity: 'normal',
    powerMode: 'full',
    colorTheme: 'arcade',
  },
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
          ticketId: 'f21-browser-ticket',
          seed: 0x21c0ffee,
          expiresAt: Date.now() + 60 * 60 * 1000,
          ruleset: { build: BUILD, replay: REPLAY_VERSION, arena: ARENA_GENERATION, director: DIRECTOR_GENERATION },
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
          ruleset: { build: BUILD, replay: REPLAY_VERSION, arena: ARENA_GENERATION, director: DIRECTOR_GENERATION },
          rows: [],
          self: null,
        }),
      });
      return;
    }
    await route.fulfill({ status: 404, headers, body: JSON.stringify({ error: 'not-found' }) });
  });
}

async function seedSave(page, overrides = {}) {
  const seed = { ...baseSave, ...overrides, settings: { ...baseSave.settings, ...(overrides.settings || {}) } };
  await page.addInitScript(value => {
    localStorage.setItem('voidcut.standalone.v1', JSON.stringify(value));
  }, seed);
}

async function openApp(page, { seed = true } = {}) {
  await installApiFixtures(page);
  if (seed) await seedSave(page);
  await page.goto('/index.html', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
}

async function ensureControlledServiceWorker(page) {
  await page.evaluate(async () => { await navigator.serviceWorker.ready; });
  if (!(await page.evaluate(() => !!navigator.serviceWorker.controller))) {
    await page.reload({ waitUntil: 'domcontentloaded' });
  }
  await expect.poll(() => page.evaluate(() => !!navigator.serviceWorker.controller)).toBe(true);
}

function capturePageErrors(page) {
  const errors = [];
  page.on('pageerror', error => errors.push(String(error?.stack || error)));
  return errors;
}

test.describe.configure({ mode: 'serial' });

test('release metadata and responsive layouts match the current contracts', async ({ page }) => {
  const errors = capturePageErrors(page);
  await openApp(page);

  const metadata = await page.evaluate(() => Object.fromEntries([
    'build', 'release-channel', 'save-schema', 'replay-version', 'arena-generation', 'director-generation',
  ].map(name => [name, document.querySelector(`meta[name="voidcut-${name}"]`)?.content || null])));
  expect(metadata).toEqual({
    build: BUILD,
    'release-channel': 'stable',
    'save-schema': String(SAVE_SCHEMA),
    'replay-version': String(REPLAY_VERSION),
    'arena-generation': String(ARENA_GENERATION),
    'director-generation': String(DIRECTOR_GENERATION),
  });

  for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport);
    await expect(page.locator('#play')).toBeVisible();
    const layout = await page.evaluate(() => {
      const play = document.getElementById('play').getBoundingClientRect();
      const settings = document.getElementById('menuSettingsFab').getBoundingClientRect();
      return {
        scrollWidth: document.documentElement.scrollWidth,
        innerWidth,
        play: { left: play.left, right: play.right, top: play.top, bottom: play.bottom },
        settings: { left: settings.left, right: settings.right, top: settings.top, bottom: settings.bottom },
      };
    });
    expect(layout.scrollWidth).toBeLessThanOrEqual(layout.innerWidth + 1);
    for (const box of [layout.play, layout.settings]) {
      expect(box.left).toBeGreaterThanOrEqual(-1);
      expect(box.right).toBeLessThanOrEqual(viewport.width + 1);
      expect(box.top).toBeGreaterThanOrEqual(-1);
      expect(box.bottom).toBeLessThanOrEqual(viewport.height + 1);
    }
  }
  expect(errors).toEqual([]);
});

test('save-17 persistence survives reload and keyboard/pointer input remains usable', async ({ page }) => {
  const errors = capturePageErrors(page);
  await openApp(page);

  await page.locator('#menuSettingsFab').click();
  const reduced = page.locator('.toggle[data-setting="reducedMotion"]');
  await expect(reduced).toBeVisible();
  expect(await reduced.evaluate(el => el.classList.contains('is-on'))).toBe(false);
  await reduced.click();

  const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('voidcut.standalone.v1')));
  expect(stored.f).toBe(2);
  expect(stored.v).toBe(SAVE_SCHEMA);
  expect(stored.d.schemaVersion).toBe(SAVE_SCHEMA);
  expect(stored.d.settings.reducedMotion).toBe(true);

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('#menu')).toBeVisible();
  const afterReload = await page.evaluate(() => JSON.parse(localStorage.getItem('voidcut.standalone.v1')));
  expect(afterReload.d.settings.reducedMotion).toBe(true);

  await page.locator('#play').click();
  await expect(page.locator('#pauseBtn')).toBeVisible();
  await page.keyboard.press('Space');
  await expect(page.locator('#pausePanel')).toBeVisible();
  await page.locator('#resume').click();
  await expect(page.locator('#pausePanel')).toBeHidden();

  const canvas = page.locator('#game');
  const box = await canvas.boundingBox();
  expect(box).not.toBeNull();
  const x = box.x + Math.max(20, box.width * 0.18);
  const y = box.y + Math.max(20, box.height * 0.18);
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x + 8, y + 8, { steps: 2 });
  await page.mouse.up();
  await expect(canvas).toBeVisible();
  expect(errors).toEqual([]);
});

test('touch-style pointer input works on a mobile viewport without layout overflow', async ({ browser }) => {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true });
  const page = await context.newPage();
  const errors = capturePageErrors(page);
  try {
    await openApp(page);
    await page.locator('#play').click();
    await expect(page.locator('#pauseBtn')).toBeVisible();
    const canvas = page.locator('#game');
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    const clientX = box.x + box.width * 0.22;
    const clientY = box.y + box.height * 0.22;
    await canvas.dispatchEvent('pointerdown', { pointerId: 41, pointerType: 'touch', isPrimary: true, buttons: 1, clientX, clientY });
    await canvas.dispatchEvent('pointermove', { pointerId: 41, pointerType: 'touch', isPrimary: true, buttons: 1, clientX: clientX + 9, clientY: clientY + 7 });
    await canvas.dispatchEvent('pointerup', { pointerId: 41, pointerType: 'touch', isPrimary: true, buttons: 0, clientX: clientX + 9, clientY: clientY + 7 });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    expect(overflow).toBeLessThanOrEqual(1);
    await expect(canvas).toBeVisible();
    expect(errors).toEqual([]);
  } finally {
    await context.close();
  }
});

test('current replay-9 and deterministic release audit passes in the real browser', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = capturePageErrors(page);
  await openApp(page);
  await page.locator('#menuSettingsFab').click();
  await page.locator('#systemChecks').click();
  await expect(page.locator('#diagnosticsPanel')).toBeVisible();
  await page.locator('#runStressDiagnostics').click();
  await expect(page.locator('#runStressDiagnostics')).toBeEnabled({ timeout: 150_000 });
  const report = await page.locator('#diagnosticsText').innerText();
  expect(report).toContain('GLOBAL COMPETITION AUDIT • PASS');
  expect(report).toContain('Release 6.1.0 contract PASS');
  expect(report).toContain('Strict replay input timing PASS');
  expect(report).toContain('High-score replay round-trip PASS');
  expect(report).toContain('same-seed determinism');
  expect(report).not.toContain('FAILURES');
  expect(errors).toEqual([]);
});

test('service-worker update installs waiting and activates only after the explicit update action', async ({ page }) => {
  test.setTimeout(120_000);
  const errors = capturePageErrors(page);
  const original = await fs.readFile(SW_PATH, 'utf8');
  try {
    await openApp(page);
    await ensureControlledServiceWorker(page);
    await expect(page.locator('#updateApp')).toBeHidden();

    await fs.writeFile(SW_PATH, `${original}\n// F21 browser update probe ${Date.now()}\n`, 'utf8');
    await page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      if (!reg) throw new Error('service worker registration missing');
      await reg.update();
    });

    await expect.poll(() => page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      return !!reg?.waiting;
    }), { timeout: 30_000 }).toBe(true);
    await expect(page.locator('#updateApp')).toBeVisible();
    await expect(page.locator('#updateApp')).toHaveText('UPDATE READY');

    const before = await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null);
    await page.waitForTimeout(400);
    expect(await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL || null)).toBe(before);

    const loaded = page.waitForEvent('load');
    await page.locator('#updateApp').click();
    await loaded;
    await expect.poll(() => page.evaluate(async () => {
      const reg = await navigator.serviceWorker.getRegistration('./');
      return !!navigator.serviceWorker.controller && !reg?.waiting;
    })).toBe(true);
    await expect(page.locator('#updateApp')).toBeHidden();
    expect(errors).toEqual([]);
  } finally {
    await fs.writeFile(SW_PATH, original, 'utf8');
  }
});
