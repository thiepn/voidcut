import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root = path.resolve(process.cwd(), '..');
const workerPath = path.join(root, 'leaderboard/src/index.js');
const generatedPath = path.join(root, 'leaderboard/src/generated-verifier.js');
const worker = fs.readFileSync(workerPath, 'utf8');
assert.ok(fs.existsSync(generatedPath), 'generated verifier missing; run npm run build:verifier first');
const generated = fs.readFileSync(generatedPath, 'utf8');

const tempModule = path.join(root, 'leaderboard/src', `.f22-adversarial-${process.pid}-${Date.now()}.mjs`);
fs.writeFileSync(
  tempModule,
  `${generated}\nexport { Sim, DT, analyzeReplayData, replayHash, replayValidationReason, competitiveReplayValidationReason, replayInputTiming };\n`,
  'utf8',
);

let verifier;
try {
  verifier = await import(`${pathToFileURL(tempModule).href}?v=${Date.now()}`);
} finally {
  try { fs.unlinkSync(tempModule); } catch {}
}

const {
  verifyReplay,
  Sim,
  DT,
  replayHash,
  replayValidationReason,
  competitiveReplayValidationReason,
  replayInputTiming,
} = verifier;

function clone(value) {
  return structuredClone(value);
}
function resign(replay) {
  replay.hash = '';
  replay.hash = replayHash(replay);
  return replay;
}
function buildFatalReplay(seed = 0xF2202026) {
  const sim = new Sim(seed);
  sim.reset(seed, 2, 6, 9);
  let guard = 0;
  while (sim.briefingRemaining > 0 && guard++ < 2000) {
    const result = sim.update(DT);
    assert.equal(result.dead, false, 'passive briefing setup unexpectedly died');
  }
  assert.equal(sim.briefingRemaining, 0, 'briefing did not settle before adversarial replay fixture');
  const ball = sim.balls[0];
  assert.ok(ball, 'fatal replay fixture has no core');
  const origin = { x: ball.pos.x, y: ball.pos.y };
  const direction = { x: 1, y: 0 };
  const region = sim.regionAt(origin);
  assert.ok(region, 'fatal replay fixture core is outside its region');
  const eventTime = +sim.runElapsed.toFixed(8);
  assert.equal(sim.beginCut(region.id, origin, direction), true, 'fatal replay fixture cut could not start');
  let died = false;
  for (let i = 0; i < 2000; i++) {
    const result = sim.update(DT);
    if (result.dead) {
      died = true;
      break;
    }
    assert.ok(!result.res, 'fatal replay fixture resolved safely instead of remaining a fatal cut');
  }
  assert.equal(died, true, 'fatal replay fixture did not produce a deterministic death');
  return resign({
    version: 9,
    arenaGeneration: 2,
    directorGeneration: 6,
    seed,
    events: [{ t: eventTime, o: origin, d: direction }],
    score: sim.score,
    chamber: sim.chamber,
    deathTime: +sim.runElapsed.toFixed(8),
    hash: '',
  });
}

// --- Deterministic verifier attack corpus ---------------------------------
const base = buildFatalReplay();
assert.equal(replayValidationReason(base), 'valid', 'generated current replay fixture is structurally invalid');
assert.equal(competitiveReplayValidationReason(base), 'valid', 'generated current replay fixture is not competitively eligible');
const official = verifyReplay(base);
assert.ok(official, 'generated verifier rejected the known-good deterministic replay fixture');
assert.equal(official.score, base.score);
assert.equal(official.chamber, base.chamber);
assert.equal(official.deathTime, base.deathTime);

const hashTamper = clone(base);
hashTamper.hash = hashTamper.hash === '00000000' ? 'FFFFFFFF' : '00000000';
assert.equal(replayValidationReason(hashTamper), 'hash-mismatch');
assert.equal(verifyReplay(hashTamper), null, 'internal replay hash tampering was accepted');

for (let i = 1; i <= 32; i++) {
  const inflated = resign({ ...clone(base), score: base.score + i * 1000003 });
  assert.equal(replayValidationReason(inflated), 'valid', `score-inflation fixture ${i} failed structural setup`);
  assert.equal(verifyReplay(inflated), null, `score inflation attack ${i} was accepted after recomputing the client hash`);
}
for (const chamberDelta of [1, 2, 10, 100]) {
  const deeper = resign({ ...clone(base), chamber: base.chamber + chamberDelta });
  assert.equal(replayValidationReason(deeper), 'valid');
  assert.equal(verifyReplay(deeper), null, `forged chamber +${chamberDelta} was accepted`);
}
for (const timeDelta of [0.25, 1, 10]) {
  const forgedTime = resign({ ...clone(base), deathTime: base.deathTime + timeDelta });
  assert.equal(replayValidationReason(forgedTime), 'valid');
  assert.equal(verifyReplay(forgedTime), null, `forged deathTime +${timeDelta} was accepted`);
}
const forgedOrigin = clone(base);
forgedOrigin.events[0].o = { x: -1000000, y: -1000000 };
resign(forgedOrigin);
assert.equal(replayValidationReason(forgedOrigin), 'valid', 'off-arena origin must reach deterministic verification rather than fail only structural parsing');
assert.equal(verifyReplay(forgedOrigin), null, 'forged off-arena input was accepted');

const duplicate = clone(base);
duplicate.events.push(clone(duplicate.events[0]));
resign(duplicate);
assert.equal(replayValidationReason(duplicate), 'invalid-events', 'duplicate v9 input timestamps were accepted');
assert.equal(verifyReplay(duplicate), null);

const nearDuplicate = clone(base);
nearDuplicate.events.push({ ...clone(nearDuplicate.events[0]), t: nearDuplicate.events[0].t + 5e-7 });
resign(nearDuplicate);
assert.equal(replayValidationReason(nearDuplicate), 'invalid-events', 'v9 timestamp within strict epsilon was accepted');

const postDeath = clone(base);
postDeath.events[0].t = base.deathTime + 2e-6;
resign(postDeath);
assert.equal(replayValidationReason(postDeath), 'invalid-events', 'post-death input was accepted');

for (const seed of [-1, 0x100000000, 1.5]) {
  const bad = resign({ ...clone(base), seed });
  assert.equal(replayValidationReason(bad), 'invalid-seed', `invalid seed ${seed} was accepted`);
}
for (const score of [-1, Number.MAX_SAFE_INTEGER + 1]) {
  const bad = resign({ ...clone(base), score });
  assert.equal(replayValidationReason(bad), 'invalid-result', `invalid score ${score} was accepted`);
}
const badChamber = resign({ ...clone(base), chamber: 0 });
assert.equal(replayValidationReason(badChamber), 'invalid-result');

const legacy = resign({ ...clone(base), version: 8 });
assert.equal(replayValidationReason(legacy), 'valid', 'supported legacy replay lost local compatibility');
assert.equal(competitiveReplayValidationReason(legacy), 'unsupported-ruleset', 'legacy replay entered the current competitive ruleset');
assert.equal(verifyReplay(legacy), null, 'server verifier accepted legacy replay v8');

const wrongArena = resign({ ...clone(base), arenaGeneration: 3 });
assert.equal(replayValidationReason(wrongArena), 'unsupported-ruleset');
const wrongDirector = resign({ ...clone(base), directorGeneration: 5 });
assert.equal(replayValidationReason(wrongDirector), 'unsupported-ruleset');

const tooLong = resign({ ...clone(base), deathTime: 1800.001 });
assert.equal(replayValidationReason(tooLong), 'valid');
assert.equal(competitiveReplayValidationReason(tooLong), 'resource-limit', 'competitive duration ceiling can be bypassed');
assert.equal(verifyReplay(tooLong), null);

const manyEvents = Array.from({ length: 12001 }, (_, i) => ({
  t: +(0.1 * (i + 1)).toFixed(8),
  o: { x: 300, y: 400 },
  d: { x: 1, y: 0 },
}));
const tooMany = resign({
  version: 9,
  arenaGeneration: 2,
  directorGeneration: 6,
  seed: 0xF2200022,
  events: manyEvents,
  score: 0,
  chamber: 1,
  deathTime: 1201,
  hash: '',
});
assert.equal(replayValidationReason(tooMany), 'valid', 'resource-limit fixture must pass the broad local envelope');
assert.equal(competitiveReplayValidationReason(tooMany), 'resource-limit', '12,000-event competitive ceiling can be bypassed');
assert.equal(verifyReplay(tooMany), null);

const timingEvent = { t: 1 };
assert.equal(replayInputTiming(base, timingEvent, 1), 'due');
assert.equal(replayInputTiming(base, timingEvent, 1 + DT), 'stale');
assert.equal(replayInputTiming(base, timingEvent, 1 - DT), 'future');

// --- Worker auth, ticket, rate-limit and storage attack contracts ----------
function section(start, end) {
  const a = worker.indexOf(start);
  const b = worker.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Worker section missing: ${start}`);
  return worker.slice(a, b);
}

const preauthMatch = worker.match(/function preauthKey\(request\) \{[\s\S]*?\n\}/);
assert.ok(preauthMatch, 'trusted pre-auth identity helper missing');
const preauthKey = new Function(`${preauthMatch[0]};return preauthKey;`)();
const makeRequest = (ip, ua, forwarded = '') => new Request('https://voidcut.invalid/run/submit/ticket', {
  headers: {
    ...(ip == null ? {} : { 'CF-Connecting-IP': ip }),
    'User-Agent': ua,
    'X-Forwarded-For': forwarded,
    'X-Real-IP': forwarded,
  },
});
assert.equal(preauthKey(makeRequest('203.0.113.9', 'UA-A', '198.51.100.1')), 'ip:203.0.113.9');
assert.equal(preauthKey(makeRequest('203.0.113.9', 'UA-B', '192.0.2.77')), 'ip:203.0.113.9', 'attacker-controlled headers split trusted-IP limiter identity');
assert.equal(preauthKey(makeRequest(null, 'UA-C', '198.51.100.99')), 'ip:unknown', 'missing trusted IP must fail closed into a shared bucket');

const startRun = section('async function startRun(request, env)', 'async function leaderboard(request, env)');
assert.ok(startRun.includes("if (token && !player) return error(request, 401, 'invalid-profile'"), 'invalid bearer tokens can still fall back to anonymous ticket issuance');
assert.ok(startRun.indexOf("if (token && !player)") < startRun.indexOf('RUN_LIMIT.limit'), 'invalid token must be rejected before ticket rate-limit/issuance flow');
assert.ok(startRun.includes("INSERT INTO run_tickets(id,seed,player_id,created_at,expires_at,status)"), 'server-issued ticket persistence missing');
assert.ok(startRun.includes('seed = randomSeed()'), 'ranked ticket seed is not server-generated');

const forward = section('async function forwardSubmission(request, env, ticketId)', 'export class ReplayVerifier');
assert.ok(forward.includes("if (!token) return error(request, 401, 'profile-required'"), 'submission accepts missing leaderboard identity');
assert.ok(forward.includes('SUBMIT_LIMIT.limit({ key: preauthKey(request) })'), 'submission pre-auth limiter is not keyed by trusted IP');
assert.ok(!forward.includes('sha256(token)'), 'rotating attacker-controlled bearer tokens can still split submission limiter buckets');
assert.ok(forward.includes('if (len && len > MAX_REPLAY_BYTES)'), 'submission Content-Length preflight missing');
assert.ok(forward.includes('env.VERIFIER.getByName(ticketId)'), 'same-ticket submissions are not serialized through one Durable Object');
assert.ok(forward.includes("headers.set('x-voidcut-ticket', ticketId)"), 'ticket id is not bound to the verifier request');

const verifierSource = section('export class ReplayVerifier', 'export default');
const order = [
  ['authenticate', 'const player = await authenticate(request, this.env, true);'],
  ['ticket lookup', "SELECT * FROM run_tickets WHERE id=? LIMIT 1"],
  ['owner check', 'ticket.player_id && ticket.player_id !== player.id'],
  ['verified idempotency', "ticket.status === 'verified'"],
  ['used/rejected guard', "ticket.status === 'rejected' || ticket.used_at"],
  ['expiry guard', 'Date.now() > Number(ticket.expires_at)'],
  ['bounded body read', 'readBoundedText(request, MAX_REPLAY_BYTES)'],
  ['ruleset guard', 'replay?.version !== RULESET.replay'],
  ['seed guard', '(replay.seed >>> 0) !== (Number(ticket.seed) >>> 0)'],
  ['resource guard', 'replay.events.length > MAX_COMPETITIVE_EVENTS'],
  ['deterministic verifier', 'const official = verifyReplay(replay);'],
  ['server content hash', 'const serverReplayHash = await sha256(text);'],
  ['R2 write', 'this.env.REPLAYS.put(`verified/${serverReplayHash}.json`'],
  ['ticket commit', "UPDATE run_tickets SET player_id=?,used_at=?,status='verified'"],
];
let previous = -1;
for (const [label, token] of order) {
  const at = verifierSource.indexOf(token);
  assert.ok(at >= 0, `anti-cheat guard missing: ${label}`);
  assert.ok(at > previous, `anti-cheat guard is out of order: ${label}`);
  previous = at;
}
assert.ok(verifierSource.indexOf('ticket.player_id && ticket.player_id !== player.id') < verifierSource.indexOf("ticket.status === 'verified'"), 'verified-ticket idempotency leaks across player identities');
assert.ok(verifierSource.includes("if (!official) return this.#reject(request, ticketId, 'verification-failed'"), 'failed deterministic verification does not consume/reject the ticket');
assert.ok(verifierSource.indexOf('const official = verifyReplay(replay);') < verifierSource.indexOf('this.env.REPLAYS.put(`verified/${serverReplayHash}.json`'), 'unverified replay can reach R2');
assert.ok(verifierSource.includes('compareLeaderboardRank('), 'personal-best precheck bypasses canonical ranking order');
assert.ok(verifierSource.includes('best_score < ? OR'), 'atomic PB score predicate missing');
assert.ok(verifierSource.includes('(best_score = ? AND best_chamber < ?)'), 'atomic PB chamber predicate missing');
assert.ok(verifierSource.includes('(best_score = ? AND best_chamber = ? AND (best_time IS NULL OR best_time > ?))'), 'atomic PB time predicate missing');
assert.ok(verifierSource.includes("WHERE id=? AND used_at IS NULL`"), 'ticket verification commit is not single-use conditional');
assert.ok(verifierSource.includes("UPDATE run_tickets SET used_at=?,status='rejected' WHERE id=? AND used_at IS NULL"), 'rejected attacks do not atomically consume their ticket');

const replayRoute = section('async function replayResponse(request, env, hash)', 'async function forwardSubmission(request, env, ticketId)');
assert.ok(replayRoute.indexOf('SELECT id FROM players WHERE best_replay_hash=? LIMIT 1') < replayRoute.indexOf('env.REPLAYS.get(`verified/${replayHash}.json`)'), 'unreferenced R2 replay objects can be retrieved directly');

for (const invariant of [
  'const MAX_REPLAY_BYTES = 2_500_000;',
  'const MAX_COMPETITIVE_EVENTS = 12_000;',
  'const MAX_COMPETITIVE_DURATION = 1_800;',
  "const RULESET = Object.freeze({ build: '6.1.0', replay: 9, arena: 2, director: 6 });",
]) assert.ok(worker.includes(invariant), `competitive invariant missing: ${invariant}`);

console.log('F22 adversarial leaderboard / anti-cheat suite PASS');
console.log('  deterministic replay tampering: rejected');
console.log('  resource exhaustion corpus: rejected');
console.log('  trusted-IP limiter anti-rotation: enforced');
console.log('  ticket ownership/idempotency: enforced');
console.log('  server-seed/ruleset/single-use/PB/R2 ordering: enforced');
