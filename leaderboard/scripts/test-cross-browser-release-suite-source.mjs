import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../../', import.meta.url);
const pkg = JSON.parse(fs.readFileSync(new URL('package.json', root), 'utf8'));
const config = fs.readFileSync(new URL('playwright.config.mjs', root), 'utf8');
const spec = fs.readFileSync(new URL('tests/release-cross-browser.spec.mjs', root), 'utf8');
const workflow = fs.readFileSync(new URL('.github/workflows/cross-browser-release.yml', root), 'utf8');

assert.equal(pkg.devDependencies?.['@playwright/test'], '1.62.1', 'Playwright version must be pinned for reproducible browser certification');
assert.equal(pkg.scripts?.['test:browser'], 'playwright test', 'browser test script missing');

for (const project of ['chromium', 'firefox', 'webkit']) {
  assert.match(config, new RegExp(`name: '${project}'`), `${project} Playwright project missing`);
  assert.ok(workflow.includes(project), `${project} CI matrix entry missing`);
}
assert.ok(config.includes("serviceWorkers: 'allow'"), 'real service-worker behavior must remain enabled');
assert.ok(config.includes("node tests/pwa-test-server.mjs"), 'suite must use the controllable local branch server instead of production');
assert.ok(config.includes('workers: 1'), 'SW mutation/update probe must remain serial within a browser job');

for (const token of [
  "'save-schema': String(SAVE_SCHEMA)",
  "'replay-version': String(REPLAY_VERSION)",
  "'arena-generation': String(ARENA_GENERATION)",
  "'director-generation': String(DIRECTOR_GENERATION)",
  "JSON.parse(localStorage.getItem('voidcut.standalone.v1'))",
  "page.keyboard.press('Space')",
  'page.mouse.down()',
  'page.mouse.move(',
  'page.touchscreen.tap(',
  'hasTouch: true',
  'GLOBAL COMPETITION AUDIT • PASS',
  'Strict replay input timing PASS',
  'High-score replay round-trip PASS',
  'same-seed determinism',
  "await reg.update()",
  "return !!reg?.waiting",
  "toHaveText('UPDATE READY')",
  "page.locator('#updateApp').click()",
]) assert.ok(spec.includes(token), `cross-browser contract missing: ${token}`);
assert.ok(!spec.includes("dispatchEvent('pointerdown'"), 'touch certification must use native browser input rather than synthetic PointerEvents');

for (const forbidden of ['thiepn.github.io/voidcut', 'thiepn.dev/voidcut']) {
  assert.ok(!spec.includes(forbidden), 'browser suite must not target deployed production pages');
}

assert.match(workflow, /matrix:\s*\n\s*browser:\s*\[chromium, firefox, webkit\]/, 'CI must use an explicit three-browser matrix');
assert.ok(workflow.includes('npx playwright install --with-deps ${{ matrix.browser }}'), 'CI must install the exact matrix browser with system dependencies');
assert.ok(workflow.includes('npx playwright test tests/release-cross-browser.spec.mjs --project=${{ matrix.browser }}'), 'CI must run the F21 browser corpus only in the matrix browser project per isolated job');
for (let phase = 1; phase <= 20; phase++) {
  const marker = phase === 12 ? 'test-backend-maintenance-source.py' : phase === 20 ? 'test-expanded-diagnostics-source.mjs' : null;
  if (marker) assert.ok(workflow.includes(marker), `F${phase} regression missing from release suite`);
}
assert.ok(workflow.includes('test-cross-browser-release-suite-source.mjs'), 'F21 source regression must run in CI');
assert.ok(workflow.includes('upload-artifact@v4'), 'browser failure evidence must be retained as CI artifacts');

console.log('F21 cross-browser release suite source regression PASS');
