import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const indexPath = path.join(root, 'index.html');
const clientPath = path.join(root, 'leaderboard/client/global-leaderboard-runtime.js');
const html = fs.readFileSync(indexPath, 'utf8');
const client = fs.readFileSync(clientPath, 'utf8');

assert.ok(html.includes("const RANKED_START_WAIT_MS=2000;"), 'inline ranked-start budget missing');
assert.ok(client.includes("const RANKED_START_WAIT_MS=2000;"), 'source-client ranked-start budget missing');

const helperPattern = /async function acquireLeaderboardTicket\(waitMs=RANKED_START_WAIT_MS\)\{[^\n]+\}/;
const inlineHelperMatch = html.match(helperPattern);
assert.ok(inlineHelperMatch, 'inline acquireLeaderboardTicket helper missing');
const inlineHelper = inlineHelperMatch[0];
const clientHelperMatch = client.match(helperPattern);
assert.ok(clientHelperMatch, 'source-client acquireLeaderboardTicket helper missing');
assert.equal(clientHelperMatch[0], inlineHelper, 'source client and shipped inline acquisition helpers must match');

function makeAcquire(take, prefetch) {
  return new Function(
    'RANKED_START_WAIT_MS',
    'takeLeaderboardTicket',
    'prefetchLeaderboardTicket',
    `${inlineHelper};return acquireLeaderboardTicket;`,
  )(2000, take, prefetch);
}

{
  const ticket = { ticketId: 'ready', seed: 1, expiresAt: Date.now() + 100000 };
  let prefetchCalls = 0;
  const acquire = makeAcquire(() => ticket, async () => { prefetchCalls++; return ticket; });
  const result = await acquire(5);
  assert.equal(result.ticket, ticket, 'ready ticket must start immediately');
  assert.equal(result.reason, null);
  assert.equal(prefetchCalls, 0, 'ready ticket must not trigger another acquisition');
}

{
  const ticket = { ticketId: 'pending', seed: 2, expiresAt: Date.now() + 100000 };
  let available = null;
  const acquire = makeAcquire(
    () => { const t = available; available = null; return t; },
    () => new Promise(resolve => setTimeout(() => { available = ticket; resolve(ticket); }, 5)),
  );
  const result = await acquire(100);
  assert.equal(result.ticket, ticket, 'pending ticket must be consumed after request settles');
  assert.equal(result.reason, null);
}

{
  const acquire = makeAcquire(() => null, async () => null);
  const result = await acquire(100);
  assert.equal(result.ticket, null);
  assert.equal(result.reason, 'LEADERBOARD UNAVAILABLE', 'settled request without ticket must be explicit local fallback');
}

{
  let eventual = null;
  const later = { ticketId: 'later', seed: 3, expiresAt: Date.now() + 100000 };
  const acquire = makeAcquire(
    () => { const t = eventual; eventual = null; return t; },
    () => new Promise(resolve => setTimeout(() => { eventual = later; resolve(later); }, 30)),
  );
  const result = await acquire(5);
  assert.equal(result.ticket, null, 'ticket arriving after start budget must not attach to current run');
  assert.equal(result.reason, 'LEADERBOARD TIMEOUT');
  await new Promise(resolve => setTimeout(resolve, 40));
  assert.equal(eventual, later, 'late ticket may remain available for a later run');
}

for (const required of [
  "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false,rankedTimingIntegrity=null,rankedStartPromise=null,leaderboardSubmissionQueue=[],leaderboardQueueDrainPromise=null,leaderboardQueueRetryTimer=null;",
  "async function start(challenge=null,skipTutorial=false)",
  "if(challenge){launchRun(challenge,skipTutorial,null,null);return}",
  "if(rankedStartPromise)return rankedStartPromise",
  "state='starting'",
  "const acquired=await acquireLeaderboardTicket()",
  "if(state!=='starting')return null",
  "launchRun(null,skipTutorial,acquired.ticket,acquired.reason)",
  "rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;if(!challenge&&!activeLeaderboardTicket)rankedRunInvalidReason=rankedStartReason||'LEADERBOARD UNAVAILABLE'",
  "showCoach('LOCAL RUN','A global leaderboard ticket was not available for this start.'",
  "$('play').onclick=()=>start()",
  "const target=activeChallenge;start(target)",
]) assert.ok(html.includes(required), `missing F8 start invariant: ${required}`);

const launchMatch = html.match(/function launchRun\(challenge=null,skipTutorial=false,rankTicket=null,rankedStartReason=null\)\{[\s\S]*?\}\nasync function start/);
assert.ok(launchMatch, 'launchRun helper missing');
assert.ok(!launchMatch[0].includes('takeLeaderboardTicket()'), 'launchRun must not race ticket acquisition synchronously');
assert.ok(launchMatch[0].includes('rankTicket?.seed??freshSeed()'), 'server ticket seed must remain authoritative when ranked');
assert.ok(launchMatch[0].includes('void prefetchLeaderboardTicket()'), 'next-run prefetch must still happen after launch');

console.log('F8 ranked start ticket synchronization regression PASS');
