import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const worker = fs.readFileSync(path.join(root, 'leaderboard/src/index.js'), 'utf8');
const client = fs.readFileSync(path.join(root, 'leaderboard/client/global-leaderboard-runtime.js'), 'utf8');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const config = fs.readFileSync(path.join(root, 'leaderboard/wrangler.jsonc'), 'utf8');

for (const obsolete of [
  'checkTurnstile',
  'TURNSTILE_REQUIRED',
  'TURNSTILE_SECRET',
  'turnstileToken',
  'challenges.cloudflare.com/turnstile',
  'human-check-failed',
]) {
  assert.ok(!worker.includes(obsolete), `backend-only Turnstile contract remains: ${obsolete}`);
}

for (const [label, source] of [['client runtime', client], ['shipped index', html]]) {
  for (const obsolete of ['turnstileToken', 'cf-turnstile', 'challenges.cloudflare.com/turnstile']) {
    assert.ok(!source.includes(obsolete), `${label} unexpectedly contains partial Turnstile integration: ${obsolete}`);
  }
}

assert.ok(worker.includes("env.PROFILE_LIMIT.limit({ key: preauthKey(request) })"), 'profile rate limiting must remain after Turnstile removal');
assert.ok(worker.includes("const name = cleanName(body.name);"), 'profile name validation must remain after Turnstile removal');
assert.ok(worker.includes("INSERT INTO players(id,name,token_hash,created_at,updated_at)"), 'profile creation persistence must remain after Turnstile removal');
assert.ok(worker.includes("const token = randomToken();"), 'profile token issuance must remain after Turnstile removal');
assert.ok(worker.includes("const tokenHash = await sha256(token);"), 'profile token hashing must remain after Turnstile removal');

for (const invariant of [
  '"name": "PROFILE_LIMIT", "namespace_id": "6101", "simple": { "limit": 10, "period": 60 }',
  '"name": "RUN_LIMIT", "namespace_id": "6102", "simple": { "limit": 40, "period": 60 }',
  '"name": "SUBMIT_LIMIT", "namespace_id": "6103", "simple": { "limit": 20, "period": 60 }',
]) assert.ok(config.includes(invariant), `rate-limit protection changed unexpectedly: ${invariant}`);

assert.ok(client.includes("JSON.stringify({name})"), 'profile client request contract changed unexpectedly');
assert.ok(html.includes("JSON.stringify({name})"), 'shipped profile client request contract changed unexpectedly');

console.log('F7 Turnstile contract regression PASS');
