import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const workerPath = path.join(root, 'leaderboard/src/index.js');
const configPath = path.join(root, 'leaderboard/wrangler.jsonc');
const worker = fs.readFileSync(workerPath, 'utf8');
const config = fs.readFileSync(configPath, 'utf8');

const helperMatch = worker.match(/function preauthKey\(request\) \{[\s\S]*?\n\}/);
assert.ok(helperMatch, 'preauthKey helper missing');
const preauthKey = new Function(`${helperMatch[0]};return preauthKey;`)();

function req(ip, ua, forwarded = '') {
  const headers = new Headers();
  if (ip != null) headers.set('CF-Connecting-IP', ip);
  if (ua != null) headers.set('User-Agent', ua);
  if (forwarded) {
    headers.set('X-Forwarded-For', forwarded);
    headers.set('X-Real-IP', forwarded);
  }
  return new Request('https://test.invalid', { headers });
}

const ip = '203.0.113.41';
assert.equal(preauthKey(req(ip, 'UA-A')), `ip:${ip}`);
assert.equal(preauthKey(req(ip, 'UA-B')), `ip:${ip}`, 'rotating User-Agent must not split pre-auth rate-limit identity');
assert.equal(preauthKey(req(ip, 'UA-C', '198.51.100.17')), `ip:${ip}`, 'forwarding headers must not split trusted-IP identity');
assert.equal(preauthKey(req(ip, '')), `ip:${ip}`, 'omitting User-Agent must not split pre-auth rate-limit identity');
assert.equal(preauthKey(req('203.0.113.42', 'UA-A')), 'ip:203.0.113.42', 'different trusted client IP should use a different network bucket');
assert.equal(preauthKey(req(null, 'attacker-controlled', '198.51.100.99')), 'ip:unknown', 'missing trusted IP must use a stable fail-closed bucket');
assert.equal(preauthKey(req(' 203.0.113.41 ', 'UA-A')), `ip:${ip}`, 'trusted IP should be trimmed before keying');

assert.ok(!helperMatch[0].includes('User-Agent'), 'preauthKey must not depend on User-Agent');
assert.ok(!helperMatch[0].includes('X-Forwarded-For'), 'preauthKey must not trust caller-controlled forwarding headers');
assert.ok(!helperMatch[0].includes('X-Real-IP'), 'preauthKey must not trust caller-controlled real-IP headers');
assert.ok(helperMatch[0].includes("request.headers.get('CF-Connecting-IP')"), 'preauthKey must use Cloudflare client IP');
assert.ok(helperMatch[0].includes("`ip:${ip || 'unknown'}`"), 'preauthKey must namespace and fail closed');

assert.ok(worker.includes('env.PROFILE_LIMIT.limit({ key: preauthKey(request) })'), 'profile creation must use trusted-IP pre-auth key');
assert.ok(worker.includes('const key = player?.id || preauthKey(request);'), 'anonymous run tickets must use trusted-IP pre-auth key');
assert.ok(worker.includes('env.RUN_LIMIT.limit({ key })'), 'run ticket limiter missing');

const forwardStart = worker.indexOf('async function forwardSubmission(request, env, ticketId)');
const verifierStart = worker.indexOf('export class ReplayVerifier', forwardStart);
assert.ok(forwardStart >= 0 && verifierStart > forwardStart, 'submission forwarding section missing');
const forward = worker.slice(forwardStart, verifierStart);
assert.ok(forward.includes('env.SUBMIT_LIMIT.limit({ key: preauthKey(request) })'), 'submission pre-auth limiter must use trusted Cloudflare IP');
assert.ok(!forward.includes('const tokenKey = await sha256(token);'), 'attacker-controlled bearer token must not define the submission limiter bucket');
assert.ok(!forward.includes('env.SUBMIT_LIMIT.limit({ key: tokenKey })'), 'rotating bearer tokens must not split submission limiter identity');
assert.ok(forward.includes("if (!token) return error(request, 401, 'profile-required'"), 'submission still requires a bearer identity before forwarding');

const verifier = worker.slice(verifierStart);
assert.ok(verifier.includes('const player = await authenticate(request, this.env, true);'), 'bearer identity must still be authenticated inside the serialized verifier');
assert.ok(verifier.includes("if (!player) return error(request, 401, 'invalid-profile'"), 'invalid bearer identity must still fail authentication');

for (const invariant of [
  '"name": "PROFILE_LIMIT", "namespace_id": "6101", "simple": { "limit": 10, "period": 60 }',
  '"name": "RUN_LIMIT", "namespace_id": "6102", "simple": { "limit": 40, "period": 60 }',
  '"name": "SUBMIT_LIMIT", "namespace_id": "6103", "simple": { "limit": 20, "period": 60 }',
]) assert.ok(config.includes(invariant), `rate-limit configuration changed unexpectedly: ${invariant}`);

console.log('F6/F22 trusted pre-auth rate-limit source regression PASS');
