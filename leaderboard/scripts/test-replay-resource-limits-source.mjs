import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const indexPath = path.resolve(process.argv[2] || '../index.html');
const workerPath = path.join(root, 'leaderboard/src/index.js');
const builderPath = path.join(root, 'leaderboard/scripts/build-verifier.mjs');
const html = fs.readFileSync(indexPath, 'utf8');
const worker = fs.readFileSync(workerPath, 'utf8');
const builder = fs.readFileSync(builderPath, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
assert.ok(scripts.length, 'VOIDCUT inline runtime was not found');
const source = scripts.sort((a,b)=>b.length-a.length)[0];

assert.ok(source.includes('const COMPETITIVE_REPLAY_EVENT_LIMIT=12000,COMPETITIVE_REPLAY_MAX_DURATION=1800,COMPETITIVE_REPLAY_MAX_STEPS=216100;'), 'competitive replay limits missing');
assert.ok(source.includes('const REPLAY_EVENT_LIMIT=50000,REPLAY_CODE_LIMIT=12000000,REPLAY_TIME_EPS=1e-6;'), 'local/legacy replay envelope changed unexpectedly');

const competitiveMatch = source.match(/function competitiveReplayValidationReason\(r\)\{[^\n]+\}/);
assert.ok(competitiveMatch, 'competitive replay validation helper missing');
const makeCompetitive = (baseReason='valid') => new Function(`
  const COMPETITIVE_REPLAY_EVENT_LIMIT=12000,COMPETITIVE_REPLAY_MAX_DURATION=1800;
  const replayValidationReason=()=>${JSON.stringify(baseReason)};
  ${competitiveMatch[0]};
  return competitiveReplayValidationReason;
`)();
const competitive = makeCompetitive();
assert.equal(competitive({version:9,deathTime:1800,events:{length:12000}}), 'valid');
assert.equal(competitive({version:9,deathTime:1800,events:{length:12001}}), 'resource-limit');
assert.equal(competitive({version:9,deathTime:1800.001,events:{length:1}}), 'resource-limit');
assert.equal(competitive({version:8,deathTime:1,events:{length:1}}), 'unsupported-ruleset');
assert.equal(makeCompetitive('invalid-events')({version:9,deathTime:1,events:{length:1}}), 'invalid-events', 'base validation failures must win before resource policy');

const analyzer = source.match(/function analyzeReplayData\(data,competitive=false\)\{[^\n]+\}/)?.[0] || '';
assert.ok(analyzer, 'competitive analyzer signature missing');
assert.ok(analyzer.includes("if(competitive&&steps>=COMPETITIVE_REPLAY_MAX_STEPS){invalidReason='step-budget';break}"), 'independent verifier step budget missing');
assert.ok(analyzer.indexOf('steps>=COMPETITIVE_REPLAY_MAX_STEPS') < analyzer.indexOf('s.update(DT)'), 'step budget must be checked before simulation work');
assert.ok(analyzer.includes("const validation=competitive?competitiveReplayValidationReason(data):replayValidationReason(data)"), 'competitive/local validation split missing');
assert.ok(analyzer.includes('return{cuts,big:big?.i??null,close:close?.i??null,death:deathCut,verified,invalidReason,steps}'), 'analyzer step accounting result missing');

assert.ok(builder.includes('const analysis=analyzeReplayData(replay,true);'), 'generated verifier is not opting into competitive limits');

for (const invariant of [
  'const MAX_REPLAY_BYTES = 2_500_000;',
  'const MAX_COMPETITIVE_EVENTS = 12_000;',
  'const MAX_COMPETITIVE_DURATION = 1_800;',
  'async function readBoundedText(request, maxBytes)',
  'const reader = request.body.getReader();',
  'if (total > maxBytes) throw new Error(\'body-too-large\');',
  'try { await reader.cancel(); } catch {}',
  'text = await readBoundedText(request, MAX_REPLAY_BYTES);',
  "replay.events.length > MAX_COMPETITIVE_EVENTS",
  "replay.deathTime > MAX_COMPETITIVE_DURATION",
  "'replay-resource-limit'",
]) assert.ok(worker.includes(invariant), `missing Worker F4 invariant: ${invariant}`);

const preflightAt = worker.indexOf('replay.events.length > MAX_COMPETITIVE_EVENTS');
const verifyAt = worker.indexOf('const official = verifyReplay(replay);');
assert.ok(preflightAt >= 0 && verifyAt > preflightAt, 'resource preflight must happen before deterministic verification');

const boundedMatch = worker.match(/async function readBoundedText\(request, maxBytes\) \{[\s\S]*?\n\}/);
assert.ok(boundedMatch, 'bounded stream reader source missing');
const readBoundedText = new Function(`${boundedMatch[0]};return readBoundedText;`)();
assert.equal(await readBoundedText(new Request('https://test.invalid',{method:'POST',body:'12345'}), 5), '12345');
await assert.rejects(() => readBoundedText(new Request('https://test.invalid',{method:'POST',body:'123456'}), 5), /body-too-large/);
const utf8 = '€€'; // 6 UTF-8 bytes, only 2 JS characters.
await assert.rejects(() => readBoundedText(new Request('https://test.invalid',{method:'POST',body:utf8}), 5), /body-too-large/, 'limit must count bytes, not JS characters');

console.log('F4 replay resource limit source regression PASS');
