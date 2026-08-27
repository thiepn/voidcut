import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const spec = fs.readFileSync(path.join(root, 'tests/pwa-destructive.spec.mjs'), 'utf8');
const workflow = fs.readFileSync(path.join(root, '.github/workflows/cross-browser-release.yml'), 'utf8');
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));

for (const title of [
  'offline boot preserves save and leaderboard identity after a controlled install',
  'deleting the shell cache self-heals online and the rebuilt shell boots offline',
  'a broken update install cannot evict the active worker, cache, or durable state',
  'a valid explicit update claims two open tabs without losing durable state',
  'cache generations overlap while waiting and obsolete shells are deleted only after activation',
  'unregister plus cache removal can reinstall cleanly without deleting application data',
  'deliberate localStorage loss boots a clean save offline and does not resurrect leaderboard ownership',
]) {
  assert.ok(spec.includes(title), `F23 destructive lifecycle case missing: ${title}`);
}

for (const invariant of [
  "const SAVE_KEY = 'voidcut.standalone.v1';",
  "const IDENTITY_KEY = 'voidcut.leaderboard.identity.v1';",
  "const IDENTITY_BACKUP_KEY = 'voidcut.leaderboard.identity.backup.v1';",
  "const CACHE_PREFIX = 'voidcut-shell-';",
  'await context.setOffline(true);',
  'await caches.delete(name)',
  "'./__f23_missing_core_asset__.js'",
  "reg.waiting.postMessage({ type: 'SKIP_WAITING' });",
  'await reg.unregister();',
  'localStorage.clear()',
  "expect(after.identity).toBeNull();",
  "expect(after.backupIdentity).toBeNull();",
]) assert.ok(spec.includes(invariant), `F23 destructive invariant missing: ${invariant}`);

assert.equal(pkg.scripts?.['test:pwa-destructive'], 'playwright test tests/pwa-destructive.spec.mjs', 'F23 package script missing or changed');

assert.ok(workflow.includes('name: F1-F23 source/regression gate'), 'release source gate is not labeled through F23');
assert.ok(workflow.includes('Run F23 destructive PWA suite contract regression'), 'F23 source regression is not wired into release workflow');
assert.ok(workflow.includes('node scripts/test-destructive-pwa-suite-source.mjs'), 'F23 source regression command missing');
assert.ok(workflow.includes('destructive-pwa:'), 'dedicated destructive PWA job missing');
assert.ok(workflow.includes('name: F23 destructive PWA lifecycle / ${{ matrix.browser }}'), 'F23 destructive PWA browser matrix name missing');
assert.ok(workflow.includes('matrix:\n        browser: [chromium, firefox, webkit]'), 'F23 destructive PWA matrix must cover Chromium, Firefox and WebKit');
assert.ok(workflow.includes('npx playwright test tests/pwa-destructive.spec.mjs --project=${{ matrix.browser }}'), 'F23 destructive PWA execution command missing');
assert.ok(workflow.includes('needs: [source-regressions, adversarial-leaderboard, destructive-pwa]'), 'normal browser certification is not gated on F23 destructive PWA success');
assert.ok(workflow.includes('npx playwright test tests/release-cross-browser.spec.mjs --project=${{ matrix.browser }}'), 'normal browser job must stay separate from destructive corpus');

console.log('F23 destructive PWA lifecycle suite contract regression PASS');
