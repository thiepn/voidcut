import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const workerPath = path.join(root, 'leaderboard/src/index.js');
const worker = fs.readFileSync(workerPath, 'utf8');

const helperMatch = worker.match(/function normalizeReplayHash\(value\) \{[\s\S]*?\n\}/);
assert.ok(helperMatch, 'normalizeReplayHash helper missing');
const normalizeReplayHash = new Function(`${helperMatch[0]};return normalizeReplayHash;`)();

const lower = '0123456789abcdef'.repeat(4);
const upper = lower.toUpperCase();
assert.equal(lower.length, 64);
assert.equal(normalizeReplayHash(lower), lower, 'lowercase SHA-256 must remain canonical');
assert.equal(normalizeReplayHash(upper), lower, 'uppercase request form must canonicalize to lowercase');
assert.equal(normalizeReplayHash('AbCdEf0123456789'.repeat(4)), 'abcdef0123456789'.repeat(4), 'mixed-case replay id must canonicalize');
assert.equal(normalizeReplayHash(lower.slice(1)), null, '63-character replay id must be rejected');
assert.equal(normalizeReplayHash(`${lower.slice(0,63)}g`), null, 'non-hex replay id must be rejected');
assert.equal(normalizeReplayHash(`${lower}00`), null, 'overlong replay id must be rejected');
assert.equal(normalizeReplayHash(null), null, 'missing replay id must be rejected');

for (const required of [
  "const replayHash = normalizeReplayHash(hash);",
  "bind(replayHash).first()",
  "env.REPLAYS.get(`verified/${replayHash}.json`)",
  "url.pathname.slice('/replay/'.length).toLowerCase()",
  "map(x => x.toString(16).padStart(2, '0')).join('')",
]) assert.ok(worker.includes(required), `missing F5 canonicalization invariant: ${required}`);

assert.ok(!worker.includes("/^[A-F0-9]{64}$/.test(hash)"), 'uppercase-only replay validation must be removed');

console.log('F5 replay hash normalization source regression PASS');
