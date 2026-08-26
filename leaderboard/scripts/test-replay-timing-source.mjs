import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const indexPath = path.resolve(process.argv[2] || '../index.html');
const html = fs.readFileSync(indexPath, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
assert.ok(scripts.length, 'VOIDCUT inline runtime was not found');
const source = scripts.sort((a, b) => b.length - a.length)[0];

const timingMatch = source.match(/function replayInputTiming\(r,e,simTime\)\{[^\n]+\}/);
assert.ok(timingMatch, 'replayInputTiming helper is missing');
const replayInputTiming = new Function(`const REPLAY_TIME_EPS=1e-6;${timingMatch[0]};return replayInputTiming;`)();

const dt = 1 / 120;
assert.equal(replayInputTiming({ version: 9 }, { t: 1 }, 1), 'due');
assert.equal(replayInputTiming({ version: 9 }, { t: 1 }, 1 + dt), 'stale');
assert.equal(replayInputTiming({ version: 9 }, { t: 1 + dt }, 1), 'future');
assert.equal(replayInputTiming({ version: 8 }, { t: 1 }, 1 + dt), 'due');

const validationMatch = source.match(/function replayValidationReason\(r\)\{[^\n]+\}/);
assert.ok(validationMatch, 'replayValidationReason is missing');
const replayValidationReason = new Function(`
  const REPLAY_EVENT_LIMIT=50000,REPLAY_TIME_EPS=1e-6;
  const replayHash=r=>r.hash;
  ${validationMatch[0]};
  return replayValidationReason;
`)();

const event = (t, x = 200, y = 300, dx = 1, dy = 0) => ({ t, o: { x, y }, d: { x: dx, y: dy } });
const base = {
  version: 9,
  arenaGeneration: 2,
  directorGeneration: 6,
  seed: 0x50100003,
  score: 0,
  chamber: 1,
  deathTime: 2,
  hash: 'TEST',
};
assert.equal(
  replayValidationReason({ ...base, events: [event(1), event(1, 210, 300, 0, 1)] }),
  'invalid-events',
  'v9 duplicate timestamps must be rejected',
);
assert.equal(
  replayValidationReason({ ...base, events: [event(1), event(1 + 5e-7, 210, 300, 0, 1)] }),
  'invalid-events',
  'v9 timestamps inside the strict epsilon must be rejected',
);
assert.equal(
  replayValidationReason({ ...base, events: [event(2 + 2e-6)] }),
  'invalid-events',
  'v9 input after deathTime + epsilon must be rejected',
);
assert.equal(
  replayValidationReason({ ...base, version: 8, events: [event(1), event(1, 210, 300, 0, 1)] }),
  'valid',
  'legacy duplicate timestamp validation behavior must remain compatible',
);

for (const required of [
  "invalidReason='stale-input'",
  'idx===data.events.length',
  "finishReplay('INPUT TIMING MISMATCH')",
]) {
  assert.ok(source.includes(required), `missing hardened replay invariant: ${required}`);
}

console.log('F1 replay timing source regression PASS');
