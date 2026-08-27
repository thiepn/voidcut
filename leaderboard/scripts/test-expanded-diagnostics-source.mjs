import fs from 'node:fs';
import assert from 'node:assert/strict';

const root = new URL('../../', import.meta.url);
const html = fs.readFileSync(new URL('index.html', root), 'utf8');
const sw = fs.readFileSync(new URL('sw.js', root), 'utf8');
const source = html.match(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)
  ?.map(x => x.replace(/^<script(?:\s[^>]*)?>/i, '').replace(/<\/script>$/i, ''))
  .sort((a,b)=>b.length-a.length)[0] || '';
assert.ok(source, 'VOIDCUT inline runtime missing');

for (const name of ['diagnosticRankedTimingProbe','diagnosticLeaderboardProbe','waitForDiagnosticWorker','diagnosticWorkerStatus','diagnosticServiceWorkerProbe']) {
  assert.match(source, new RegExp(`function ${name}\\(`), `${name} helper missing`);
}

const timing = source.match(/function diagnosticRankedTimingProbe\(\)\{[^\n]+\}/)?.[0] || '';
assert.ok(timing, 'ranked timing diagnostic source missing');
for (const token of [
  'trackRankedFrameGap(.12,.05,false)',
  'trackRankedFrameGap(.21,.05,false)',
  "trackRankedFrameGap(.10,.05,false)",
  'trackRankedCatchup(true,false)',
  "trackRankedTimingReset('DIAGNOSTIC RESET',false,1100)",
  "trackRankedTimingReset('DIAGNOSTIC RESET',false,1250)",
  "rankedRunInvalidReason!=='FRAME STALL'",
  "rankedRunInvalidReason!=='TIMING DRIFT'",
  "rankedRunInvalidReason!=='CATCH-UP LIMIT'",
  "rankedRunInvalidReason!=='DIAGNOSTIC RESET'",
  'finally{state=snapshot.state;',
  'activeLeaderboardTicket=snapshot.activeLeaderboardTicket',
  'rankedTimingIntegrity=snapshot.rankedTimingIntegrity',
  'last=snapshot.last;acc=snapshot.acc',
]) assert.ok(timing.includes(token), `ranked timing diagnostic invariant missing: ${token}`);

const frameHelper = source.match(/function trackRankedFrameGap\([^\n]+\}/)?.[0] || '';
const catchupHelper = source.match(/function trackRankedCatchup\([^\n]+\}/)?.[0] || '';
assert.ok(frameHelper.includes('notify=true'), 'frame-gap helper must preserve notify=true runtime default');
assert.ok(frameHelper.includes("invalidateRankedTiming('FRAME STALL',notify)"), 'frame-stall diagnostic notification control missing');
assert.ok(frameHelper.includes("invalidateRankedTiming('TIMING DRIFT',notify)"), 'timing-drift diagnostic notification control missing');
assert.ok(catchupHelper.includes('notify=true'), 'catch-up helper must preserve notify=true runtime default');
assert.ok(catchupHelper.includes("invalidateRankedTiming('CATCH-UP LIMIT',notify)"), 'catch-up diagnostic notification control missing');
assert.ok(source.includes('trackRankedFrameGap(rawSec,delta)'), 'normal frame loop must retain default notify behavior');
assert.ok(source.includes('trackRankedCatchup(stepLimitHit)'), 'normal catch-up loop must retain default notify behavior');

const board = source.match(/async function diagnosticLeaderboardProbe\(\)\{[^\n]+\}/)?.[0] || '';
assert.ok(board, 'leaderboard diagnostic source missing');
assert.ok(board.includes("leaderboardRequest('/leaderboard?limit=5',{},false)"), 'diagnostic must hit public leaderboard read path');
assert.ok(board.includes("leaderboardRequest(`/replay/${encodeURIComponent(hash)}`,{},false)"), 'diagnostic must retrieve a published replay');
assert.ok(board.includes('validReplay(replay)'), 'live replay must pass local structural validation');
assert.ok(board.includes('verifyCompetitiveReplay(replay)'), 'live replay must pass deterministic competitive verification');
assert.ok(board.includes('rules.replay!==RELEASE_CONTRACT.replay'), 'live leaderboard replay contract must be checked');
assert.ok(board.includes('rules.arena!==RELEASE_CONTRACT.arena'), 'live leaderboard arena contract must be checked');
assert.ok(board.includes('rules.director!==RELEASE_CONTRACT.director'), 'live leaderboard director contract must be checked');
for (const forbidden of ['/profile/create','/run/start','/run/submit']) {
  assert.ok(!board.includes(forbidden), `read-only leaderboard diagnostic must not use ${forbidden}`);
}
assert.ok(board.includes("status:server?'FAIL':'WARN'"), 'network outage must warn while server HTTP errors fail');

// Execute the actual leaderboard probe against controlled read-only responses.
const diagnosticLeaderboardProbe = new Function(
  'leaderboardRequest','RELEASE_CONTRACT','validReplay','verifyCompetitiveReplay',
  `${board}; return diagnosticLeaderboardProbe;`,
)(
  async path => {
    if (path === '/leaderboard?limit=5') return {ruleset:{replay:9,arena:2,director:6},rows:[{rank:1,name:'TEST',score:123,chamber:4,replayHash:'a'.repeat(64)}]};
    if (path === `/replay/${'a'.repeat(64)}`) return {version:9,hash:'a'.repeat(64)};
    throw new Error(`unexpected path ${path}`);
  },
  {replay:9,arena:2,director:6},
  replay => replay?.version === 9,
  replay => replay?.version === 9,
);
assert.equal((await diagnosticLeaderboardProbe()).status, 'PASS', 'valid live leaderboard + replay fixture must pass');

const emptyLeaderboardProbe = new Function(
  'leaderboardRequest','RELEASE_CONTRACT','validReplay','verifyCompetitiveReplay',
  `${board}; return diagnosticLeaderboardProbe;`,
)(async()=>({ruleset:{replay:9,arena:2,director:6},rows:[]}),{replay:9,arena:2,director:6},()=>false,()=>false);
assert.equal((await emptyLeaderboardProbe()).status, 'WARN', 'empty board must warn because replay retrieval cannot be exercised');

const offlineProbe = new Function(
  'leaderboardRequest','RELEASE_CONTRACT','validReplay','verifyCompetitiveReplay',
  `${board}; return diagnosticLeaderboardProbe;`,
)(async()=>{throw new TypeError('offline')},{replay:9,arena:2,director:6},()=>false,()=>false);
assert.equal((await offlineProbe()).status, 'WARN', 'network unavailability must be diagnostic WARN, not FAIL');

const serverErrorProbe = new Function(
  'leaderboardRequest','RELEASE_CONTRACT','validReplay','verifyCompetitiveReplay',
  `${board}; return diagnosticLeaderboardProbe;`,
)(async()=>{const e=new Error('server');e.status=500;e.code='server-error';throw e},{replay:9,arena:2,director:6},()=>false,()=>false);
assert.equal((await serverErrorProbe()).status, 'FAIL', 'live server HTTP failure must fail diagnostics');

const swProbe = source.match(/async function diagnosticServiceWorkerProbe\(\)\{[^\n]+\}/)?.[0] || '';
assert.ok(swProbe, 'service-worker diagnostic source missing');
for (const token of [
  'await reg.update()',
  'await waitForDiagnosticWorker(reg.installing)',
  'const waiting=!!reg.waiting,ready=syncWaitingUpdate(reg)',
  'reg.waiting||reg.active||reg.installing||navigator.serviceWorker.controller',
  'await diagnosticWorkerStatus(worker)',
  "status.type!=='VOIDCUT_SW_STATUS'",
  'status.build!==BUILD_ID',
  'status.cache!==expectedCache',
  'scriptBuild!==status.build',
]) assert.ok(swProbe.includes(token), `PWA diagnostic invariant missing: ${token}`);
assert.ok(!swProbe.includes('SKIP_WAITING'), 'diagnostics must never activate a waiting worker');

assert.match(sw, /if \(type === 'DIAGNOSTIC_STATUS'\) \{[\s\S]*?VOIDCUT_SW_STATUS[\s\S]*?build: VOIDCUT_BUILD[\s\S]*?cache: VOIDCUT_CACHE[\s\S]*?scope: VOIDCUT_SCOPE[\s\S]*?return;\s*\}/,
  'service worker must expose read-only diagnostic build/cache/scope status');
assert.match(sw, /if \(type === 'SKIP_WAITING'\) \{\s*self\.skipWaiting\(\);\s*\}/,
  'F15 manual activation message must remain intact');

const systemChecks = source.match(/async function runSystemChecks\(\)\{[^\n]+\}/)?.[0] || '';
assert.ok(systemChecks, 'runSystemChecks source missing');
assert.ok(systemChecks.includes('const timingProbe=diagnosticRankedTimingProbe()'), 'system checks must run ranked timing probe');
assert.ok(systemChecks.includes('diagnosticLeaderboardProbe(),diagnosticServiceWorkerProbe()'), 'system checks must run live leaderboard and PWA probes');
assert.ok(systemChecks.includes("[['LIVE LEADERBOARD',leaderboardProbe],['RANKED TIMING',timingProbe],['PWA UPDATE',swProbe]]"), 'probe outcomes must feed overall warning/failure status');
for (const label of ['LIVE LEADERBOARD:', 'RANKED TIMING:', 'PWA UPDATE:']) assert.ok(systemChecks.includes(label), `${label} report line missing`);
assert.ok(html.includes('Checks the installed release, live services, timing guards and PWA update state.'), 'diagnostic UI description must disclose expanded live checks');

console.log('F20 expanded built-in diagnostics regression PASS');
