import { chromium, firefox, webkit } from 'playwright';

const base = process.env.VOIDCUT_BASE_URL || 'http://127.0.0.1:4173/';
const engines = [['chromium', chromium], ['firefox', firefox], ['webkit', webkit]];

async function assertVisible(page, selector, label) {
  const el = page.locator(selector);
  await el.waitFor({ state: 'visible', timeout: 10000 });
  if (!(await el.isVisible())) throw new Error(`${label} is not visible`);
}

function benignEngineConsoleMessage(name, text) {
  return name === 'webkit' && text === 'Viewport argument key "interactive-widget" not recognized and ignored.';
}

for (const [name, engine] of engines) {
  const browser = await engine.launch({ headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
    const page = await context.newPage();
    const consoleErrors = [];
    page.on('pageerror', e => consoleErrors.push(`pageerror: ${e.message}`));
    page.on('console', m => {
      if (m.type() !== 'error') return;
      const text = m.text();
      if (!benignEngineConsoleMessage(name, text)) consoleErrors.push(`console: ${text}`);
    });
    await page.goto(base, { waitUntil: 'domcontentloaded' });
    await assertVisible(page, '#menu', `${name} menu`);
    await assertVisible(page, '#play', `${name} play button`);

    for (const [open, panel, back] of [
      ['#records', '#recordsPanel', '#recordsBack'],
      ['#mastery', '#masteryPanel', '#masteryBack'],
      ['#cosmetics', '#cosmeticsPanel', '#cosmeticsBackTop'],
      ['#compete', '#competitionPanel', '#competitionBack'],
    ]) {
      await page.click(open);
      await assertVisible(page, panel, `${name} ${panel}`);
      await page.click(back);
      await assertVisible(page, '#menu', `${name} menu return`);
    }

    await page.click('#play');
    await assertVisible(page, '#tutorial', `${name} first-run tutorial`);
    const training = await page.locator('#tutorial').evaluate(el => el.classList.contains('training'));
    if (!training) throw new Error(`${name} tutorial did not enter training mode`);

    if (consoleErrors.length) throw new Error(`${name} runtime errors:\n${consoleErrors.join('\n')}`);
    await context.close();
    console.log(`${name}: PASS`);
  } finally {
    await browser.close();
  }
}

// One representative phone-sized Chromium pass for overflow and primary navigation.
const mobileBrowser = await chromium.launch({ headless: true });
try {
  const context = await mobileBrowser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  await page.goto(base, { waitUntil: 'domcontentloaded' });
  await assertVisible(page, '#menu', 'mobile menu');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1);
  if (overflow) throw new Error('mobile layout has horizontal overflow');
  await page.click('#play');
  await assertVisible(page, '#tutorial', 'mobile tutorial');
  console.log('mobile-chromium: PASS');
  await context.close();
} finally {
  await mobileBrowser.close();
}
