import assert from 'node:assert/strict';
import fs from 'node:fs';

const root = new URL('../../', import.meta.url);
const workflow = fs.readFileSync(new URL('.github/workflows/cross-browser-release.yml', root), 'utf8');
const packageJson = JSON.parse(fs.readFileSync(new URL('leaderboard/package.json', root), 'utf8'));
const suite = fs.readFileSync(new URL('leaderboard/scripts/test-adversarial-leaderboard.mjs', root), 'utf8');

assert.equal(packageJson.scripts?.['test:adversarial'], 'npm run build:verifier && node scripts/test-adversarial-leaderboard.mjs', 'permanent adversarial npm script missing');
assert.ok(workflow.includes('name: F22 adversarial leaderboard / anti-cheat gate'), 'F22 CI job missing');
assert.ok(workflow.includes('npm run test:adversarial'), 'F22 CI job does not execute the adversarial suite');
assert.ok(workflow.includes('test-adversarial-release-suite-source.mjs'), 'F22 suite contract regression is not in the source gate');
assert.match(workflow, /browser-matrix:[\s\S]*?needs:\s*\[[^\]]*adversarial-leaderboard[^\]]*\]/, 'browser certification is not gated on F22 adversarial tests');

for (const token of [
  'score inflation attack',
  'forged chamber',
  'forged deathTime',
  'internal replay hash tampering',
  'duplicate v9 input timestamps',
  'post-death input',
  'competitive duration ceiling',
  '12,000-event competitive ceiling',
  'trusted-IP limiter anti-rotation',
  'verified-ticket idempotency leaks across player identities',
  'same-ticket submissions are not serialized',
  'server-issued ticket persistence missing',
  'atomic PB score predicate missing',
  'unverified replay can reach R2',
]) assert.ok(suite.includes(token), `F22 attack coverage missing: ${token}`);

assert.ok(suite.includes("SUBMIT_LIMIT.limit({ key: preauthKey(request) })"), 'F22 does not enforce trusted-IP submission throttling');
assert.ok(suite.includes("ticket.player_id && ticket.player_id !== player.id"), 'F22 does not enforce ticket ownership before idempotent success');
assert.ok(suite.includes("if (token && !player) return error(request, 401, 'invalid-profile'"), 'F22 does not prevent invalid bearer fallback to anonymous tickets');

console.log('F22 adversarial release-suite contract regression PASS');
